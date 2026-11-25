"""Financial regressions motivated by errors found during the project survey."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from engine import build_report, cagr, ratio

class FinancialTests(unittest.TestCase):
    def test_elapsed_years_not_observation_count(self):
        self.assertAlmostEqual(cagr(100,121,2),0.1)
        self.assertIsNone(cagr(-100,121,2))
    def test_missing_and_zero_denominators_stay_unavailable(self):
        self.assertIsNone(ratio(None,10));self.assertIsNone(ratio(10,0))
    def test_historical_reconciliation_all_periods(self):
        for p in ['FY19','FY20','FY21','9M Dec-2020','9M Dec-2021']:
            r=build_report(p)
            self.assertTrue(all(c['passed'] for c in r['checks']))
            self.assertEqual(len(r['facts']),22)
            self.assertTrue(all(f['period_end']<r['historical_evidence_cutoff'] for f in r['facts']))
    def test_cash_conversion_and_period_separation(self):
        self.assertAlmostEqual(build_report('FY21')['derived']['cfo_pat'],231.96/711.19)
        self.assertAlmostEqual(build_report('9M Dec-2021')['derived']['cfo_pat'],24.04/829.06)
        self.assertEqual(build_report('9M Dec-2021')['period_kind'],'interim')
    def test_unknown_period_rejected(self):
        with self.assertRaises(ValueError):build_report('FY25')

if __name__=='__main__':unittest.main()
