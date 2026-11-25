import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from ipo_ready import allocation, server


def snapshot():
    def listed(symbol, price, drawdown):
        return {"id": symbol, "name": symbol, "quote": {"state": "reported", "price_inr": price},
                "history": {"state": "ok", "max_drawdown_pct": drawdown}}

    def company(company_id, quote, lot, quote_state="reported"):
        return {"id": company_id, "name": company_id, "business_model": "exchange",
                "quote": {"state": quote_state, "price_inr": quote}, "liquidity": {"lot_shares": lot}}

    return {
        "build_id": "test-build", "as_of": "2026-11-24", "market_date": "2026-11-23", "default_company": "igx",
        "instruments": [
            {"id": "FRSB2020T", "name": "Bond", "liquidity": {"state": "locked", "face_value_inr": 1000}},
            listed("HDFCBANK", "817.80", "-31.24"), listed("GOLDBEES", "103.05", "-22.33"),
            listed("MCX", "3581.60", "-22.21"),
        ],
        "unlisted": [company("igx", "488.00", 500), company("ncdex", "253.00", 100),
                     company("haldia", None, 100, "suspect_quote"), company("icex", "4.00", None)],
    }


class AllocationTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = snapshot()

    def allocate(self, amount="500000", tolerance="balanced", company="igx", include=True):
        return allocation.allocate(self.snapshot, Decimal(amount), tolerance, company, include)

    def test_default_reproduces_whole_units_and_excludes_igx(self):
        result = self.allocate()
        self.assertEqual(result["unlisted"]["state"], "minimum_lot_exceeds_limit")
        self.assertEqual(result["unlisted"]["min_lot_inr"], Decimal("244000"))
        self.assertEqual(result["unlisted"]["effective_limit_inr"], Decimal("50000"))
        baseline = result["baseline"]
        self.assertEqual([row.get("units") for row in baseline["holdings"]], [175, 183, 970, 20, None])
        self.assertEqual(baseline["holdings"][-1]["amount_inr"], Decimal("3752.10"))
        self.assertEqual(baseline["stress_loss_inr"], Decimal("90563.30"))
        self.assertEqual(result["scenario"]["risk_mix"], baseline["risk_mix"])

    def test_ncdex_fits_and_haircut_and_stress_budget_apply(self):
        result = self.allocate(company="ncdex")
        basis = result["scenario"]
        self.assertEqual(result["unlisted"]["lots"], 1)
        self.assertEqual(basis["unlisted_shock_loss_inr"], Decimal("8855"))
        self.assertEqual(basis["unlisted_exit_haircut_loss_inr"], Decimal("4111.25"))
        self.assertTrue(basis["stress_budget_applied"])
        self.assertEqual(basis["listed_target_scale_pct"], Decimal("94.24"))
        self.assertEqual(basis["stress_loss_inr"], Decimal("94179.32"))

    def test_growth_lot_threshold_and_shared_exchange_cap(self):
        below = self.allocate(amount="1219999.99", tolerance="growth")
        self.assertEqual(below["unlisted"]["lots"], 0)
        at = self.allocate(amount="1220000.00", tolerance="growth")
        self.assertEqual(at["unlisted"]["lots"], 1)
        result = self.allocate(amount="1250000", tolerance="growth")
        self.assertTrue(result["scenario"]["exchange_cap_applied"])
        self.assertEqual(result["scenario"]["exchange_exposure_inr"], Decimal("312050.40"))
        self.assertEqual(result["scenario"]["holdings"][3]["units"], 19)
        self.assertEqual(result["baseline"]["holdings"][3]["units"], 87)

    def test_data_gaps_and_opt_out(self):
        self.assertEqual(self.allocate(company="haldia")["unlisted"]["state"], "quote_unavailable")
        self.assertEqual(self.allocate(company="icex")["unlisted"]["state"], "lot_unavailable")
        self.assertEqual(self.allocate(company="ncdex", include=False)["unlisted"]["state"], "excluded")
        self.snapshot["instruments"][0]["liquidity"]["state"] = "unavailable"
        self.snapshot["instruments"][1]["quote"]["price_inr"] = None
        self.snapshot["instruments"][2]["history"] = {"state": "insufficient_history"}
        rows = self.allocate()["scenario"]["holdings"]
        self.assertEqual([r["status"] for r in rows[:2]], ["input_unavailable", "input_unavailable"])
        self.assertEqual(rows[2]["loss_basis"], "scenario_floor")
        self.assertEqual(rows[2]["loss_pct"], 22)
        self.assertGreater(rows[-1]["amount_inr"], Decimal("300000"))

    def test_budget_and_weight_invariants_across_profiles_and_amounts(self):
        for tolerance in allocation.PROFILES:
            for amount in ("1.01", "199.99", "500000.01", "1250000.00", "100000000"):
                with self.subTest(tolerance=tolerance, amount=amount):
                    result = self.allocate(amount=amount, tolerance=tolerance, company="ncdex")
                    for side in (result["baseline"], result["scenario"]):
                        rows = side["holdings"]
                        self.assertTrue(all(row["amount_inr"] >= 0 for row in rows))
                        self.assertEqual(sum(row["amount_inr"] for row in rows), Decimal(amount))
                        self.assertEqual(sum(row["weight_pct"] for row in rows), 100)
                        self.assertEqual(sum(group["weight_pct"] for group in side["risk_mix"].values()), 100)
                        self.assertEqual(sum(row["stress_loss_inr"] for row in rows), side["stress_loss_inr"])
                        self.assertLessEqual(side["stress_loss_inr"], result["policy"]["max_loss_inr"])
                        self.assertLessEqual(side["exchange_exposure_inr"], side["exchange_limit_inr"])


class AllocationRouteTests(unittest.TestCase):
    def test_request_validation_and_snapshot_refresh(self):
        endpoint = "/api/portfolio/allocate"
        with tempfile.TemporaryDirectory() as folder, patch.object(server, "CURRENT", Path(folder)):
            client = server.app.test_client()
            self.assertEqual(client.get(endpoint).status_code, 503)
            for query in ("amount=0", "amount=-1", "amount=NaN", "amount=Infinity", "amount=1e7", "amount=1.234",
                          "amount=100000000.01", "amount=500,000", "amount=1&amount=2", "tolerance=extreme",
                          "include_unlisted=yes", "extra=1"):
                self.assertEqual(client.get(f"{endpoint}?{query}").status_code, 400, query)
            data = snapshot()
            path = Path(folder) / "portfolio.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            response = client.get(endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(response.json["build_id"], "test-build")
            self.assertEqual(response.json["amount_inr"], "500000.00")
            self.assertEqual(client.get(f"{endpoint}?company=nse").status_code, 400)
            data["build_id"] = "new-test-build"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(client.get(endpoint).json["build_id"], "new-test-build")
