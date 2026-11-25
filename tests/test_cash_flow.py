"""Regression checks for retained filings and ambiguous provider rows."""
from decimal import Decimal
import unittest

from ipo_ready import issuer
from ipo_ready.cash_flow import _reconcile
from ipo_ready.pipeline import build_company, latest_good_items, load_universe, summary_row
from ipo_ready.screener import parse_query, screen


class CashFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider = latest_good_items("wwipl")[0]
        cls.issuers = issuer.latest_issuer_docs()
        cls.universe = {company["id"]: company for company in load_universe()["unlisted"]}

    def company(self, company_id, docs):
        return build_company(self.universe[company_id], self.provider.get(f"{company_id}-financial"),
                             self.provider.get(f"{company_id}-overview"), docs)

    def test_retained_statement(self):
        company = self.company("igx", self.issuers)
        cash = company["cash_flow"]["by_period"]
        expected = {
            "FY2024": ("18.736", "-189.819", "187.572", "-1.025", "-3.272", "15.464"),
            "FY2025": ("15.464", "3.287", "-4.366", "-1.168", "-2.247", "13.217"),
            "FY2026": ("13.217", "156.685", "-153.535", "-12.410", "-9.260", "3.957"),
        }
        for period, values in expected.items():
            with self.subTest(period=period):
                view = cash[period]
                self.assertEqual(view["basis"], "issuer_and_esos_trust")
                self.assertEqual(view["reconciliation"]["state"], "reconciled")
                for key, amount in zip(("opening", "cfo", "cfi", "cff", "net_change", "closing"), values):
                    cell = view["lines"][key]
                    ev = company["evidence"][cell["ev"]]
                    self.assertEqual(cell["value"], amount)
                    self.assertEqual((ev["page"], ev["period"], ev["raw_unit"]), (7, period, "INR million"))
        lines = cash["FY2026"]["lines"]
        self.assertEqual(lines["payables_and_liabilities"]["value"], "138.628")
        self.assertEqual(lines["settlement_accounts"]["value"], "3.671")
        self.assertEqual(lines["other_effects"]["state"], "included_in_activity_totals")
        self.assertEqual(lines["debt_principal"]["state"], "not_in_source")
        self.assertEqual(cash["FY2025"]["lines"]["dividends"]["state"], "dash")
        self.assertIsNone(cash["FY2025"]["lines"]["dividends"]["value"])
        compare = cash["FY2026"]["provider_comparison"]
        self.assertEqual(compare["lines"]["cfo"]["value"], "156.89")
        self.assertEqual(compare["differences"]["cfo"], {"issuer_minus_provider": "-0.205", "state": "differs"})
        self.assertEqual(compare["differences"]["cfi"]["state"], "within_provider_rounding")
        self.assertEqual(cash["FY2022"]["reconciliation"]["state"], "partial")
        self.assertEqual(cash["FY2022"]["lines"]["cff"]["state"], "blank")

    def test_provider_only_when_filing_is_unavailable(self):
        company = self.company("igx", {})
        cash = company["cash_flow"]["by_period"]["FY2026"]
        self.assertEqual(cash["origin"], "provider")
        self.assertIsNone(cash["provider_comparison"])
        self.assertEqual(cash["lines"]["cfo"]["value"], "156.89")
        self.assertIsNone(cash["lines"]["opening"]["value"])
        self.assertEqual(cash["reconciliation"]["state"], "partial")

    def test_review_repairs_propagate_to_screen_inputs(self):
        poly = self.company("polymatech", self.issuers)
        fields = {k: v["by_period"]["FY2025"]["value"] for k, v in poly["fields"].items()}
        self.assertEqual([fields[k] for k in ("pat", "pat_pre_associate", "pat_owners", "eps_basic", "eps_diluted")],
                         ["375.5864", "375.0116", "361.3663", "9.07", "9.07"])
        summary = summary_row(poly, {})
        self.assertEqual(summary["metrics"]["pe"], {"value": 3.9691, "state": "ok", "basis": "reported_basic"})
        self.assertEqual(summary["metrics"]["pe_proxy"]["value"], 3.819)
        for field, limit, matches in (("P/E", "3.82", 0), ("P/E", "3.90", 0), ("P/E", "15", 1),
                                      ("Proxy P/E", "3.82", 1)):
            query = parse_query(f"Market cap > 500 AND {field} < {limit} AND ROCE > 22%")
            self.assertEqual(len(screen(query, [summary], {})["matches"]), matches)
        self.assertEqual(self.company("grouppharma", {})["fields"]["pat"]["by_period"]["FY2026"]["state"], "conflict")
        igx = self.company("igx", self.issuers)
        quick = igx["metrics"]["FY2026"]["quick_ratio"]
        self.assertEqual((quick["value"], quick["inventory_state"]), ("1.5137", "assumed_nil"))
        self.assertEqual([igx["evidence"][key]["page"] for key in quick["ev"]], [5, 5, 54])
        self.assertEqual(igx["metrics"]["FY2022"]["quick_ratio"]["state"], "missing_input")
        self.assertEqual(self.company("igx", {})["metrics"]["FY2026"]["quick_ratio"]["state"], "missing_input")

    def test_arithmetic_with_explicit_other_activity(self):
        fixture = {key: {"value": str(value)} for key, value in {
            "opening": 7, "cfo": 5, "cfi": -3, "cff": -2, "net_change": 1, "closing": 8, "other_effects": 1,
        }.items()}
        self.assertEqual(_reconcile(fixture)["state"], "reconciled")
        fixture["other_effects"]["value"] = "0"
        result = _reconcile(fixture)
        self.assertEqual(result["state"], "conflict")
        self.assertEqual(Decimal(result["activity_residual"]), -1)


if __name__ == "__main__":
    unittest.main()
