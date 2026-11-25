"""NSE lookup coverage using dated captures and a small directory fixture."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ipo_ready import lookup, server


class CompanyLookupTests(unittest.TestCase):
    def test_retained_market_search_and_verified_snapshot(self):
        with TemporaryDirectory() as directory, patch.object(lookup, "RECORDS", Path(directory)), \
                patch.object(lookup, "SOURCE_ROOT", Path(directory) / "captures"):
            result = lookup.search("nse:bse", online=False)
            self.assertEqual(result["matches"][0]["symbol"], "BSE")
            self.assertEqual(result["mode"], "retained_nse_closes")
            record, state = lookup.acquire("BSE", online=False, history_sessions=3)
            self.assertEqual(state, "added")
            self.assertEqual(record["row"]["coverage"], "annual")
            self.assertEqual(record["row"]["quote_as_of"], "2026-11-23")
            self.assertEqual(len(record["company"]["price_history"]), 3)
            self.assertEqual(record["company"]["research"]["by_period"]["FY2026"]["comparison"]["revenue"]["basis"], "standalone")
            self.assertTrue(all("sha256" in ev for ev in record["company"]["evidence"].values()))
            self.assertEqual(lookup.acquire("BSE", online=False)[1], "already_added")
            self.assertEqual(lookup.read_acquired("nse-bse"), record)

    def test_directory_fixture_isin_and_series(self):
        body = (b"SYMBOL,NAME OF COMPANY,SERIES,ISIN NUMBER\n"
                b"TEST,Test Industries,EQ,INE001A01010\n"
                b"OUT,Other Series,BE,INE002A01010\n")
        item = {"abs_path": "fixture.csv", "body": body, "sha256": "fixture",
                "retrieved_at": "2026-11-24T12:00:00+00:00", "mode": "retained"}
        with patch.object(lookup, "_capture", return_value=item):
            self.assertEqual(lookup.search("INE001A01010")["matches"][0]["symbol"], "TEST")
            self.assertEqual(lookup.search("Other Series")["count"], 0)

    def test_local_api_adds_once_and_exposes_the_same_record(self):
        with TemporaryDirectory() as directory, patch.object(lookup, "RECORDS", Path(directory)), \
                patch.object(server, "_lookup_online", return_value=False), server.app.test_client() as client:
            search = client.get("/api/company-lookup", query_string={"q": "CDSL"})
            self.assertEqual(search.json["matches"][0]["id"], "nse-cdsl")
            added = client.post("/api/company-lookup", json={"symbol": "CDSL"})
            self.assertEqual(added.status_code, 200)
            self.assertEqual(added.json["state"], "added")
            self.assertEqual(client.post("/api/company-lookup", json={"symbol": "CDSL"}).json["state"], "already_added")
            self.assertEqual(client.post("/api/company-lookup", json={"symbol": "BSE"}).json["state"], "added")
            catalog = client.get("/data/current/catalog.json").json
            self.assertEqual(sum(row["id"] == "nse-cdsl" for row in catalog["companies"]), 1)
            self.assertIn("nse-bse", [row["id"] for row in catalog["companies"]])
            detail = client.get("/data/current/company/nse-cdsl.json").json
            self.assertEqual(detail["id"], added.json["row"]["id"])
            result = client.get("/api/screen", query_string={"query": "Revenue > 0", "market": "listed"})
            self.assertIn("nse-cdsl", [row["id"] for row in result.json["matches"]])
            self.assertEqual(client.post("/api/company-lookup", json={"symbol": "https://unrelated.example/"}).status_code, 400)
            self.assertEqual(client.post("/api/company-lookup", json={"symbol": "UNKNOWN999"}).status_code, 404)

    def test_failing_financial_source_keeps_price_and_coverage_gap(self):
        with TemporaryDirectory() as directory, patch.object(lookup, "RECORDS", Path(directory)), \
                patch.object(lookup, "_financials", return_value=None):
            result, _ = lookup.acquire("HDFCBANK", online=False)
            self.assertEqual(result["company"]["lookup"]["financials"], "unavailable")
            self.assertEqual(result["row"]["coverage"], "identity_only")
            self.assertIsNotNone(result["row"]["price_inr"])
            self.assertIsNone(result["screen"]["metrics"]["revenue_cr"]["value"])
