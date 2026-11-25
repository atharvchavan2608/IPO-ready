"""Unit tests: metrics edge cases, parsing states/units, split adjustment, fallback selection, agent."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

from ipo_ready import metrics as M
from ipo_ready.market import adjust_splits, weekly_stats
from ipo_ready.parse_wwipl import normalise_period, parse_number, UNIT_RX, SCALE_TO_CRORE

ROOT = Path(__file__).resolve().parent.parent


class MetricsTest(unittest.TestCase):
    def test_ratio_zero_and_missing(self):
        self.assertEqual(M.ratio(1, 0, "a/b")["state"], M.ZERO_DEN)
        self.assertEqual(M.ratio(None, 2, "a/b")["state"], M.MISSING)
        self.assertEqual(M.ratio("445.94", "294.60", "a/b")["value"], "1.5137")

    def test_growth_negative_and_zero_base(self):
        self.assertEqual(M.growth(10, -5)["state"], M.NEG_BASE)
        self.assertEqual(M.growth(10, 0)["state"], M.ZERO_DEN)
        self.assertEqual(M.growth("61.01", "48.80")["value"], "25.0205")

    def test_quick_ratio_states(self):
        self.assertEqual(M.quick_ratio(100, None, "missing", 50)["state"], M.MISSING)
        r = M.quick_ratio(100, None, "inapplicable", 50)
        self.assertEqual((r["value"], r["state"]), ("2.0000", M.OK))
        self.assertIn("nil", r["note"])
        self.assertEqual(M.quick_ratio(100, 20, "reported", 40)["value"], "2.0000")
        self.assertEqual(M.quick_ratio(100, 20, "reported", 0)["state"], M.ZERO_DEN)

    def test_pe_loss_and_zero(self):
        self.assertEqual(M.pe(100, -2)["state"], M.NEG_BASE)
        self.assertEqual(M.pe(100, 0)["state"], M.ZERO_DEN)
        self.assertEqual(M.pe(488, "5.676")["value"], "85.9760")

    def test_eps_and_market_cap_reproduce_igx(self):
        # IGX FY2026: PAT 42.02 cr, 74,030,400 shares, quote 488
        eps = M.eps_from("42.02", 74_030_400)
        self.assertEqual(eps["value"], "5.6760")
        self.assertEqual(M.market_cap_cr(488, 74_030_400)["value"], "3612.6835")

    def test_cagr(self):
        self.assertEqual(M.cagr(121, 100, 2)["value"], "10.0000")
        self.assertEqual(M.cagr(100, -1, 2)["state"], M.NEG_BASE)
        self.assertEqual(M.cagr(100, 50, 0)["state"], M.ZERO_DEN)


class ParseTest(unittest.TestCase):
    def test_number_states(self):
        self.assertEqual(parse_number("")[1], "blank")
        self.assertEqual(parse_number("-")[1], "dash")
        self.assertEqual(parse_number("#DIV/0!")[1], "provider_error")
        self.assertEqual(parse_number("0.00")[1], "explicit_zero")
        self.assertEqual(parse_number("(14.05)")[0], Decimal("-14.05"))
        self.assertEqual(parse_number("1,42,898")[0], Decimal("142898"))
        self.assertEqual(parse_number("69.08%")[2], "%")
        self.assertEqual(parse_number("abc")[1], "unparsed")

    def test_periods(self):
        self.assertEqual(normalise_period("2025-26"), "FY2026")
        self.assertEqual(normalise_period("31-03-2026"), "FY2026")
        self.assertEqual(normalise_period("As at 31 March 2023"), "FY2023")
        self.assertEqual(normalise_period("31-Mar-23"), "FY2023")
        self.assertEqual(normalise_period("30-09-2025"), "PE:2025-09-30")
        self.assertEqual(normalise_period("2023"), "FY2023?")
        self.assertIsNone(normalise_period("Particulars"))

    def test_units(self):
        for heading, unit in (("Balance Sheet (Rs. in Million)", "million"), ("P&L (Rs in Lakhs)", "lakh"),
                              ("(In Rs. Crore)", "crore"), ("(Rs in Thousands)", "thousand")):
            m = UNIT_RX.search(heading)
            self.assertIsNotNone(m, heading)
            self.assertIn(m.group(1).lower().rstrip("s"), SCALE_TO_CRORE)
            self.assertEqual(m.group(1).lower().rstrip("s"), unit)


class MarketTest(unittest.TestCase):
    def test_split_detected_and_adjusted(self):
        s = [{"date": "a", "close": 10000.0}, {"date": "b", "close": 11000.0}, {"date": "c", "close": 2216.0}, {"date": "d", "close": 2300.0}]
        adj, ev = adjust_splits(s)
        self.assertEqual(ev[0]["factor"], 5)
        self.assertAlmostEqual(adj[0]["close"], 2000.0)
        self.assertEqual(adj[0]["close_raw"], 10000.0)

    def test_ordinary_fall_not_a_split(self):
        _, ev = adjust_splits([{"date": "a", "close": 100.0}, {"date": "b", "close": 70.0}])
        self.assertEqual(ev, [])

    def test_weekly_stats_insufficient(self):
        self.assertEqual(weekly_stats([{"date": "a", "close": 1.0}])["state"], "insufficient_history")


class FallbackTest(unittest.TestCase):
    def test_latest_good_item_falls_back(self):
        from ipo_ready import sources
        tmp = Path(tempfile.mkdtemp())
        try:
            for run, ok in (("20260101T000000Z", True), ("20260102T000000Z", False)):
                d = tmp / "src" / run
                d.mkdir(parents=True)
                item = {"id": "x", "status": 200 if ok else None, "url": "u", "retrieved_at": run, "sha256": "h"}
                if ok:
                    (d / "x.html").write_text("ok")
                    item["path"] = "x.html"
                else:
                    item["error"] = "simulated"
                (d / "manifest.json").write_text(json.dumps({"items": [item]}))
            with mock.patch.object(sources, "CAPTURES", tmp):
                items, fb = sources.latest_good_items("src")
            self.assertEqual(items["x"]["run"], "20260101T000000Z")
            self.assertEqual(fb[0]["state"], "fallback_to_previous_capture")
        finally:
            shutil.rmtree(tmp)


@unittest.skipUnless((ROOT / "data" / "captures" / "issuer").exists(), "issuer captures not present")
class AgentTest(unittest.TestCase):
    def setUp(self):
        from ipo_ready.config import load_universe
        self.uni = {c["id"]: c for c in load_universe()["unlisted"]}

    def test_igx_inventory_inapplicable_with_page_evidence(self):
        from ipo_ready import agent
        r = agent.run(self.uni["igx"], {}, "inventories")
        self.assertEqual(r["status"], "inapplicable")
        pages = {(e["document"], e["page"]) for e in r["evidence"] if e["kind"] == "explicit_not_applicable"}
        self.assertIn(("igx-restated-financials", 54), pages)
        self.assertEqual([s["tool"] for s in r["trace"]],
                         ["provider_lookup", "applicability_rule", "statement_line_check", "document_search", "classify_passages", "verdict"])

    def test_naive_npa_substring_is_noisy(self):
        from ipo_ready import agent
        r = agent.run(self.uni["igx"], {}, "npa")
        search = next(s for s in r["trace"] if s["tool"] == "document_search")["output"]
        self.assertGreater(search["pages_with_naive_substring"], search["pages_with_word_matches"])
        self.assertEqual(r["status"], "inapplicable")

    def test_lender_without_documents_is_not_found(self):
        from ipo_ready import agent
        r = agent.run(self.uni["herofincorp"], {}, "npa")
        self.assertEqual(r["status"], "not_found_no_documents")
        self.assertEqual(r["expectation"]["level"], "expected")

    def test_provider_value_wins(self):
        from ipo_ready import agent
        fields = {"inventories": {"FY2026": {"state": "reported", "value": "12.5"}}}
        r = agent.run(self.uni["indiacarbon"], fields, "inventories")
        self.assertEqual(r["status"], "found_in_provider")


if __name__ == "__main__":
    unittest.main()
