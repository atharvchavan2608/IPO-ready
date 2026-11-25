"""Focused regression cases for the shared model and two V2 scenario paths."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from ipo_ready import server
from ipo_ready.allocation import workspace_scenario
from ipo_ready.catalog import build_catalog
from ipo_ready.config import BUILDS
from ipo_ready.pipeline import build_company, latest_good_items, latest_issuer_docs, load_universe
from ipo_ready.portfolio import build_portfolio
from ipo_ready.ratios import RATIOS, build_ratios
from ipo_ready.research_views import build_research
from ipo_ready.screener import QueryError, parse_query


class V2WorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        items = latest_good_items("wwipl")[0]
        config = next(row for row in load_universe()["unlisted"] if row["id"] == "igx")
        cls.igx = build_company(config, items["igx-financial"], items["igx-overview"], latest_issuer_docs())
        cls.igx["identity"] = {"listing": "unlisted"}
        cls.igx["ratios"] = build_ratios(cls.igx)
        baseline = BUILDS / "20261123T191506Z"
        cls.portfolio = json.loads((baseline / "portfolio.json").read_text(encoding="utf-8"), parse_float=Decimal)
        market = json.loads((baseline / "market.json").read_text(encoding="utf-8"))
        retained = build_portfolio(market, [], "igx", *latest_good_items("portfolio_terms"), "test")
        cls.portfolio.update(workspace_instruments=retained["workspace_instruments"], listed_history=retained["listed_history"])
        cls.listed_rows = [{"id": "nse-iex", "name": "Indian Energy Exchange", "identity": {"listing": "listed"},
                            "model": "exchange", "coverage": "annual", "price_inr": "109.15", "quote_as_of": "2026-11-23"},
                           {"id": "nse-aether", "name": "Aether", "identity": {"listing": "listed"},
                            "model": "manufacturer", "coverage": "identity_only", "price_inr": None},
                           {"id": "igx", "name": "IGX", "identity": {"listing": "unlisted"}}]

    def test_issuer_ratios_and_claim_evidence(self):
        ratios = self.igx["ratios"]["by_period"]["FY2026"]
        self.assertEqual(len(ratios), sum(len(items) for items in RATIOS.values()))
        self.assertEqual(ratios["fcf_margin"]["value"], "255.6954")
        self.assertEqual(ratios["fcf_margin"]["basis"], "issuer_and_esos_trust")
        self.assertEqual(ratios["pe"]["eps_basis"], "reported_basic")
        self.assertEqual(ratios["eps_diluted"]["value"], "5.6600")
        self.assertEqual(ratios["volume_growth"]["value"], "27.9407")
        self.assertEqual(ratios["fee_per_unit"]["unit"], "₹/MMBtu")
        self.assertEqual(self.igx["ratios"]["by_period"]["FY2022"]["fcf_margin"]["state"], "missing_input")
        research = build_research(self.igx)
        claim = next(item for item in research["by_period"]["FY2026"]["claims"] if "₹138.628" in item["title"])
        self.assertTrue(self.igx["evidence"][claim["ev"][0]]["url"].endswith("#page=7"))

    def test_listed_basis_conflict_and_identity_only(self):
        item = latest_good_items("screener")[0]["IEX-standalone"]
        companies, _ = build_catalog({}, {"IEX-standalone": {**item, "basis": "consolidated"}}, {"stocks": []})
        self.assertEqual(companies["nse-iex"]["periods"], [])
        aether = companies["nse-aether"]
        self.assertEqual(aether["identity"]["isin"], "INE0BWX01014")
        self.assertEqual(aether["identity"]["state"], "verified")
        self.assertIsNone(aether["quote"]["price_inr"])

    def test_budget_and_named_positions(self):
        def check(args):
            result = workspace_scenario(self.portfolio, self.listed_rows, args)
            rows = result["scenario"]["holdings"]
            self.assertEqual(sum(row["amount_inr"] for row in rows), result["amount_inr"])
            self.assertEqual(sum(row["weight_pct"] for row in rows), 100)
            self.assertGreaterEqual(rows[-1]["amount_inr"], result["reserve_inr"])
            self.assertLessEqual(result["scenario"]["exchange_exposure_inr"], result["scenario"]["exchange_limit_inr"])
            return result

        budget = check({"shortlist": "nse-aether,nse-iex"})
        self.assertEqual(budget["focus"]["id"], "nse-iex")
        self.assertEqual(budget["focus"]["amount_inr"], Decimal("99981.40"))
        self.assertEqual(budget["focus"]["history"]["return_pct"], -19.82)
        weak = check({"shortlist": "nse-aether"})
        self.assertIsNone(weak["focus"])
        self.assertEqual(weak["scenario"], weak["baseline"])
        named = check({"company": "igx"})
        self.assertEqual(named["focus"]["state"], "minimum_lot_exceeds_limit")
        self.assertEqual(named["scenario"], named["baseline"])
        feasible = check({"company": "igx", "tolerance": "growth", "amount": "1250000"})
        self.assertEqual(feasible["focus"]["amount_inr"], Decimal("244000"))
        self.assertEqual(feasible["scenario"]["restricted_capital_inr"], Decimal("244000"))
        unavailable = check({"company": "nse-aether"})
        self.assertEqual(unavailable["focus"]["state"], "quote_unavailable")

    def test_liquid_completion_reserve_and_return_cases(self):
        result = workspace_scenario(self.portfolio, self.listed_rows, {"cash_reserve": "5"})
        outcome = result["scenario"]
        self.assertEqual(result["reserve_inr"], 50000)
        self.assertLess(outcome["unspent_inr"], 1000)
        self.assertEqual(outcome["cash_reason"], "whole_units")
        holdings = outcome["holdings"]
        liquid = next(row for row in holdings if row["id"] == "LIQUIDBEES")
        self.assertEqual(liquid["history"]["return_pct"], 5.24)
        self.assertEqual(liquid["return_scenarios"]["base"]["annual_assumption_pct"], 5)
        compound = (liquid["amount_inr"] * Decimal("1.157625")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.assertEqual(liquid["return_scenarios"]["base"]["ending_value_inr"], compound)
        for case, value in outcome["returns"].items():
            self.assertEqual(value["ending_value_inr"], sum(row["return_scenarios"][case]["ending_value_inr"] for row in holdings))
        self.assertLess(outcome["returns"]["downside"]["gain_inr"], outcome["returns"]["base"]["gain_inr"])
        self.assertLess(outcome["returns"]["base"]["gain_inr"], outcome["returns"]["upside"]["gain_inr"])
        self.assertGreater(outcome["risk_mix"]["low"]["amount_inr"], outcome["risk_mix"]["medium"]["amount_inr"])

    def test_allocations_respect_term_and_quote_gates(self):
        for amount in ("1.01", "1000000", "100000000"):
            for tolerance in ("conservative", "balanced", "growth"):
                with self.subTest(amount=amount, tolerance=tolerance):
                    request = {"amount": amount, "tolerance": tolerance, "company": "igx", "horizon": "36"}
                    result = workspace_scenario(self.portfolio, self.listed_rows, request)
                    side = result["scenario"]
                    self.assertEqual(side["cash_inr"] + side["invested_inr"], Decimal(amount))
                    self.assertLessEqual(side["stress_loss_inr"], Decimal(amount) * result["max_loss_pct"] / 100)
                    self.assertLessEqual(side["exchange_exposure_inr"], side["exchange_limit_inr"])
                    self.assertEqual(next(row for row in side["holdings"] if row["id"] == "FRSB2020T")["units"], 0)
        long = workspace_scenario(self.portfolio, self.listed_rows, {"horizon": "84"})["scenario"]
        self.assertGreater(next(row for row in long["holdings"] if row["id"] == "FRSB2020T")["units"], 0)
        stale_rows = [{**self.listed_rows[0], "quote_as_of": "2026-11-20"}, *self.listed_rows[1:]]
        missing_source = {**self.portfolio, "workspace_instruments": []}
        result = workspace_scenario(missing_source, stale_rows, {"company": "nse-iex"})
        self.assertEqual(result["focus"]["state"], "quote_stale")
        self.assertEqual(result["scenario"]["cash_reason"], "liquid_input_unavailable")
        self.assertGreater(result["scenario"]["cash_inr"], 400000)

    def test_read_only_prefix_and_retained_file_recovery(self):
        self.assertEqual(parse_query("SELECT company FROM companies WHERE Revenue > 20"), parse_query("Revenue > 20"))
        with self.assertRaises(QueryError):
            parse_query("SELECT company FROM companies WHERE Revenue > 20; DROP TABLE companies")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            current, builds = root / "current", root / "builds"
            build = builds / "20261124T130000Z"
            build.mkdir(parents=True)
            (build / "manifest.json").write_text('{"build_id":"20261124T130000Z","mode":"offline"}', encoding="utf-8")
            (build / "catalog.json").write_text('{"companies":[]}', encoding="utf-8")
            with patch.multiple(server, CURRENT=current, PUBLISHED_CURRENT=current, BUILDS=builds):
                with server.app.test_client() as client:
                    response = client.get("/data/current/catalog.json")
                    self.assertEqual(response.headers["X-IPO-Ready-Data"], "retained-build")
                    self.assertEqual(response.json, {"companies": []})
                    self.assertTrue(client.get("/api/health").json["retained_build"])
                    response.close()
