from decimal import Decimal
from unittest import TestCase

from ipo_ready.company import build_company
from ipo_ready.config import load_universe
from ipo_ready.issuer import latest_issuer_docs
from ipo_ready.pre_ipo import OYO_REPORT, enrich_pre_ipo
from ipo_ready.ratios import build_ratios
from ipo_ready.research_views import build_research
from ipo_ready.sources import latest_good_items


class PreIPOTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = latest_issuer_docs()
        cls.provider = latest_good_items("wwipl")[0]
        cls.issuer = next(row for row in load_universe()["unlisted"] if row["id"] == "oyo")

    def build_oravel(self, sources):
        company = build_company(self.issuer, self.provider["oyo-financial"], self.provider["oyo-overview"], sources)
        enrich_pre_ipo(company, sources)
        company["identity"] = {"listing": "unlisted"}
        company["ratios"] = build_ratios(company)
        return company

    def test_oravel_cash_includes_separate_fx_and_keeps_reported_rounding(self):
        company = self.build_oravel(self.sources)
        cash = company["cash_flow"]["by_period"]
        self.assertTrue(cash["FY2026"]["effects_after_net"])
        self.assertEqual(cash["FY2026"]["reconciliation"]["state"], "reconciled")
        self.assertEqual(cash["FY2025"]["reconciliation"], {
            "state": "rounding_difference", "activity_residual": "-0.001", "balance_residual": "-0.001",
        })
        cfo = cash["FY2026"]["lines"]["cfo"]
        evidence = company["evidence"][cfo["ev"]]
        self.assertEqual((cfo["value"], evidence["raw_text"], evidence["raw_unit"]), ("2511.21", "25,112.10", "INR million"))
        self.assertEqual((evidence["page"], evidence["retained_page"]), (165, 9))
        self.assertEqual(build_research(company)["by_period"]["FY2026"]["comparison"]["cfo"]["ev"], [cfo["ev"]])
        self.assertEqual(company["issuer_case"]["metrics"]["cash_after_capex_interest_and_leases_cr"], "408.465")

    def test_converted_share_valuation_is_conditional(self):
        company = self.build_oravel(self.sources)
        valuation = company["valuation"]
        self.assertEqual(valuation["market_cap"]["state"], "conditional_share_count")
        self.assertEqual(valuation["shares_used"], "15053791264")
        self.assertEqual(Decimal(valuation["pe"]["value"]), Decimal("30.0735"))
        self.assertEqual(valuation["pe"]["eps_basis"], "reported_basic")
        self.assertIsNone(valuation["pe_proxy"]["value"])
        self.assertIsNone(company["ratios"]["by_period"]["FY2026"]["ev_ebitda"]["value"])
        self.assertEqual(company["ipo_stage"]["state"], "verified")

    def test_missing_annual_source_withholds_old_provider_pe(self):
        documents = {key: doc for key, doc in self.sources.items() if key != OYO_REPORT}
        company = self.build_oravel(documents)
        self.assertEqual(company["ipo_stage"]["state"], "verified")
        self.assertNotIn("issuer_case", company)
        self.assertIsNone(company["valuation"]["pe"]["value"])
        self.assertIsNone(company["valuation"]["market_cap"]["value"])
        self.assertEqual(company["cash_flow"]["by_period"]["FY2026"]["origin"], "provider")
