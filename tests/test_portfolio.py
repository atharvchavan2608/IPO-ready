import datetime as dt
import unittest

from ipo_ready.market import weekly_stats
from ipo_ready.portfolio import LISTED, _bond, _listed


class PortfolioTests(unittest.TestCase):
    def test_volatility_excludes_returns_over_missing_weeks(self):
        start = dt.date(2025, 1, 3)
        points = [{"date": (start + dt.timedelta(weeks=week)).isoformat(), "close": 100 if week < 5 else 125}
                  for week in range(11) if week != 5]
        complete = weekly_stats(points, adjacent_weeks_only=True)
        self.assertEqual(complete["return_count"], 8)
        self.assertEqual(complete["ann_vol_pct"], 0)
        self.assertGreater(weekly_stats(points)["ann_vol_pct"], 0)
        self.assertEqual(weekly_stats(points, adjacent_weeks_only=True, min_returns=9)["state"], "insufficient_history")

    def test_mcx_split_requires_captured_evidence(self):
        before, after = "2025-12-26", "2026-01-02"
        stock = {"weekly": [{"date": before, "close_raw": 11052}, {"date": after, "close_raw": 2216}],
                 "split_events": [{"date": after, "factor": 5}]}
        dates = {before, after}
        unverified = _listed(LISTED[-1], stock, {}, {}, dates)["history"]
        self.assertEqual(unverified["state"], "corporate_action_review")
        verified = _listed(LISTED[-1], stock, {}, {"mcx-split": {"run": "fixture"}}, dates)["history"]
        self.assertEqual(verified["verified_split"]["factor"], 5)
        self.assertEqual(verified["price_points"][0]["close"], 2210.4)
        self.assertEqual(verified["price_points"][0]["close_raw"], 11052)
        self.assertEqual(verified["price_points"][1]["close"], 2216)

    def test_bond_has_no_price_metrics_when_source_capture_is_missing(self):
        bond = _bond({}, dt.date(2026, 11, 24))
        self.assertEqual(bond["coupon"]["state"], "unavailable")
        self.assertIsNone(bond["coupon"]["rate_pct_pa"])
        self.assertEqual(bond["history"]["state"], "not_exchange_traded")
        self.assertNotIn("ann_vol_pct", bond["history"])
