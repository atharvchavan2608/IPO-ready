"""Screening regressions for thresholds, scope exclusions and missing data."""
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from ipo_ready import screener, server


def company(cid, **metrics):
    return {"id": cid, "name": cid, "metrics": metrics}


def metric(value, state="ok"):
    return {"value": value, "state": state}


class ScreenTest(unittest.TestCase):
    def run_query(self, query, rows, exclusions=None):
        return screener.screen(screener.parse_query(query), rows, exclusions or {})

    def test_compound_query_uses_exact_threshold_and_excludes_listed(self):
        rows = [
            company("pass", market_cap_cr=metric("500.0001"), pe=metric("14.9999"), roce_pct=metric(23)),
            company("first boundary", market_cap_cr=metric(500), pe=metric(2), roce_pct=metric(23)),
            company("last boundary", market_cap_cr=metric(600), pe=metric(2), roce_pct=metric(22)),
            company("nse", market_cap_cr=metric(600), pe=metric(2), roce_pct=metric(23)),
        ]
        result = self.run_query(
            "Market capitalization > 500 AND\nPrice to earning < 15 AND Return on capital employed > 22%",
            rows, {"nse": {"reason": "listing evidence"}},
        )
        self.assertEqual([row["id"] for row in result["matches"]], ["pass"])
        self.assertEqual(result["matches"][0]["metrics"]["market_cap_cr"]["value"], Decimal("500.0001"))
        self.assertEqual((result["evaluated"], result["no_match"], result["unresolved"]), (3, 2, 0))
        self.assertEqual(result["excluded"][0]["id"], "nse")

    def test_or_precedence_missing_and_known_false(self):
        rows = [
            company("OR passes", pat_cr=metric(0), pe=metric(None, "negative_base")),
            company("AND fails", pat_cr=metric(-1), pe=metric(None, "zero_denominator"), roce_pct=metric(2)),
            company("unresolved", pat_cr=metric(-1), pe=metric(None, "negative_base"), roce_pct=metric(3)),
            company("AND passes", pat_cr=metric(-1), pe=metric(10), roce_pct=metric(3)),
        ]
        result = self.run_query("PAT = 0 or p/e <= 10 and ROCE >= +3%", rows)
        self.assertEqual([row["id"] for row in result["matches"]], ["AND passes", "OR passes"])
        self.assertEqual((result["no_match"], result["unresolved"]), (1, 1))
        self.assertEqual(result["coverage"]["pe"], {"available": 1, "gaps": {"negative_base": 2, "zero_denominator": 1}})
        self.assertEqual(result["matches"][1]["metrics"]["pe"], metric(None, "negative_base"))

    def test_non_finite_and_suspect_values_cannot_match(self):
        rows = [
            company("nonfinite", pe=metric("NaN")),
            company("suspect", pe=metric(0, "suspect_quote")),
            company("absent"),
        ]
        result = self.run_query("P/E > -0.5", rows)
        self.assertEqual((result["matches"], result["unresolved"]), ([], 3))
        self.assertEqual(result["coverage"]["pe"]["gaps"], {
            "invalid_value": 1, "suspect_quote": 1, "missing_input": 1,
        })

    def test_invalid_queries(self):
        for query in ("", "PAT > 1 OR", "P/E < 15%", "Unknown > 1", "PAT == 1", "(PAT > 1)",
                      "PAT > 1e10", "PAT > NaN", "PAT > 1,000", "a" * 501, " AND ".join(["PAT > 0"] * 13)):
            with self.subTest(query=query), self.assertRaises(screener.QueryError):
                screener.parse_query(query)


class ScreenRouteTest(unittest.TestCase):
    def test_snapshot_refresh_and_unavailable_response(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(server, "CURRENT", Path(tmp)):
            client = server.app.test_client()
            path = Path(tmp) / "companies.json"

            def query(text="PAT > 5"):
                return client.get("/api/screen", query_string={"query": text})

            self.assertEqual(query("PAT >").status_code, 400)
            self.assertEqual(query().status_code, 503)
            path.write_text('{"companies":', encoding="utf-8")
            self.assertEqual(query().status_code, 503)
            path.write_text(json.dumps({"companies": [company("first", pat_cr=metric(6))]}), encoding="utf-8")
            first = query()
            self.assertEqual(first.status_code, 200)
            self.assertEqual(first.json["matches"][0]["id"], "first")
            hits = server._screen_snapshot.cache_info().hits
            self.assertEqual(query().json, first.json)
            self.assertEqual(server._screen_snapshot.cache_info().hits, hits + 1)
            path.write_text(json.dumps({"companies": [company("replacement", pat_cr=metric(4))]}), encoding="utf-8")
            self.assertEqual(query().json["no_match"], 1)
