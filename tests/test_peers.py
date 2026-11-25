"""Regression checks for annual source parsing and peer eligibility."""
from pathlib import Path
import unittest

from ipo_ready import peers
from ipo_ready.issuer import igx_operating_scope, latest_issuer_docs
from ipo_ready.peer_context import read_autoaxles_annual, read_cial_annual
from ipo_ready.parse_screener import parse_screener
from ipo_ready.parse_wwipl import map_canonical, parse_financial
from ipo_ready.sources import latest_good_items


class ListedCaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        items, _ = latest_good_items("screener")
        if not {"IEX-standalone", "KAYNES-consolidated", "RAIN-standalone"} <= items.keys():
            raise unittest.SkipTest("Retained listed captures unavailable")
        cls.items = items

    def test_annual_table_ignores_ttm_and_preserves_raw_scope(self):
        page = parse_screener(self.items["IEX-standalone"])
        self.assertEqual((page["state"], page["basis"]), ("ok", "standalone"))
        self.assertEqual(max(page["annual"]), "2026-03-31")
        fact = page["annual"]["2026-03-31"]["revenue_ops"]
        self.assertEqual((fact["value"], fact["raw_label"], fact["period_label"], fact["raw_unit"]),
                         ("608", "Sales +", "Mar 2026", "INR crore"))
        self.assertEqual(fact["anchor"]["section"], "#profit-loss")

    def test_historical_standalone_column_on_consolidated_page(self):
        page = parse_screener(self.items["KAYNES-consolidated"])
        self.assertEqual(page["basis"], "consolidated")
        self.assertEqual(page["annual"]["2018-03-31"]["revenue_ops"]["basis"], "standalone")

    def test_basis_and_hash_disagreements_fail_closed(self):
        item = self.items["IEX-standalone"]
        self.assertEqual(parse_screener(dict(item, basis="consolidated"))["state"], "unexpected_statement_basis")
        self.assertEqual(parse_screener(dict(item, sha256="wrong"))["state"], "capture_hash_mismatch")

    def test_december_year_end_does_not_match_march(self):
        page = parse_screener(self.items["RAIN-standalone"])
        ref = {"comparison_basis": "standalone", "period_end": "2026-03-31", "price": None}
        result = peers._candidate("RAIN", (True, "test operating rule"), {"RAIN-standalone": page}, None, ref)
        self.assertEqual((result["status"], result["period_end"], result["reasons"]),
                         ("excluded", "2025-12-31", ["no_same_annual_period"]))


class PeerEligibilityTest(unittest.TestCase):
    def setUp(self):
        self.facts = {
            name: {"value": value, "basis": "standalone", "state": "reported"}
            for name, value in {"pat": "40", "eps": "5", "revenue_ops": "100", "other_income": "5"}.items()
        }
        self.period = "2026-03-31"
        self.ref = {"comparison_basis": "standalone", "period_end": self.period, "price": {"date": "2026-11-23"}}
        self.pages = {"TEST-standalone": {"state": "ok", "basis": "standalone", "annual": {self.period: self.facts}}}
        self.stock = {"symbol": "TEST", "date": "2026-11-23", "state": "ok", "source": {}, "close": 75}

    def test_context_and_mismatched_basis_withhold_ratios(self):
        row = peers._candidate("TEST", (False, "different product"), self.pages, self.stock, self.ref)
        self.assertEqual((row["status"], row["metrics"], row["pe"]["state"]), ("context_only", {}, "incompatible_peer"))
        row = peers._candidate("TEST", (True, "same product"), self.pages, self.stock,
                               dict(self.ref, comparison_basis="consolidated"))
        self.assertIn("incompatible_reporting_basis", row["reasons"])

    def test_multiple_uses_same_day_and_positive_annual_earnings(self):
        row = peers._candidate("TEST", (True, "same product"), self.pages, self.stock, self.ref)
        self.assertEqual((row["metrics"]["pat_to_revenue_pct"]["value"], row["pe"]["value"]), ("40.0000", "15.0000"))
        earlier = dict(self.stock, date="2026-11-20")
        row = peers._candidate("TEST", (True, "same product"), self.pages, earlier, self.ref)
        self.assertIn("same Indian calendar date", row["pe"]["note"])
        self.facts["eps"]["value"] = "-5"
        row = peers._candidate("TEST", (True, "same product"), self.pages, self.stock, self.ref)
        self.assertEqual((row["status"], row["pe"]["state"]), ("eligible", "negative_base"))

    def test_issuer_scope_preserves_employee_share_trust(self):
        doc = latest_issuer_docs().get("igx-restated-financials")
        if not doc:
            self.skipTest("IGX retained financials unavailable")
        scope = igx_operating_scope(Path(doc["abs_path"]))
        self.assertEqual((scope["basis"], scope["operating_comparison_basis"], scope["relationship_page"]),
                         ("issuer_and_esos_trust", "standalone", 9))


class PrimaryComparisonTest(unittest.TestCase):
    def setUp(self):
        self.sources, _ = latest_good_items("peer_context")

    def test_cial_annual_lakh_values_preserve_explicit_basis_and_page(self):
        item = self.sources.get("cial-annual-2026")
        if not item:
            self.skipTest("CIAL report unavailable")
        annual = read_cial_annual(item)
        self.assertEqual((annual["basis"], annual["period_end"], annual["evidence"]["page"]),
                         ("consolidated", "2026-03-31", 127))
        self.assertEqual((annual["facts"]["revenue_ops"]["value"], annual["facts"]["eps"]["value"]),
                         ("1401.4885", "11.01"))

    def test_autoaxles_source_uses_annual_column_and_audited_basis(self):
        item = self.sources.get("autoaxles-annual-2026")
        if not item:
            self.skipTest("Automotive Axles statement unavailable")
        annual = read_autoaxles_annual(item)
        self.assertEqual(annual["basis"], "standalone")
        fact = annual["annual"]["2026-03-31"]["pat"]
        self.assertEqual((fact["raw_text"], fact["value"], fact["raw_unit"]),
                         ("16,437.50", "164.375", "INR lakh"))

    def test_new_provider_lines_preserve_gains_and_conflicting_profit(self):
        sources, _ = latest_good_items("wwipl")
        if not {"grouppharma-financial", "axlesindia-financial"} <= sources.keys():
            self.skipTest("Expanded provider captures unavailable")
        group = map_canonical(parse_financial(Path(sources["grouppharma-financial"]["abs_path"]), "grouppharma")["observations"])
        fact = group["pat"]["FY2026"]
        self.assertEqual((fact["state"], fact["value"]), ("conflict", None))
        self.assertEqual([row["value"] for row in fact["components"]], ["12.53", "12.16"])
        axles = map_canonical(parse_financial(Path(sources["axlesindia-financial"]["abs_path"]), "axlesindia")["observations"])
        facts = {key: values["FY2026"] for key, values in axles.items() if "FY2026" in values}
        ratio = peers._operating_metrics(facts, "standalone")["other_income_share_pct"]
        self.assertEqual(ratio["inputs"], {"other_income_and_gains": "16.66", "total_income": "887.85"})
