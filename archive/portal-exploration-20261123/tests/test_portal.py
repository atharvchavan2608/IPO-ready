"""Arithmetic/eligibility checks; these do not validate issuer reporting."""
from copy import deepcopy
from decimal import Decimal
from http.server import ThreadingHTTPServer
import json
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from portal import analytics as a
from portal.main import handler
from portal.snapshot import build

def fact(value, *, end='2026-03-31', state='reported', basis='unspecified', metric='operating_revenue'):
    return {'id': f'{metric}-{end}', 'company_id': 'fixture', 'metric_id': metric,
            'period_start': f'{int(end[:4])-1}-04-01', 'period_end': end, 'basis': basis,
            'raw_unit': 'INR crore', 'currency': 'INR', 'state': state, 'raw_value': value}

class FinancialPolicyTests(unittest.TestCase):
    def test_missing_states_and_zero_are_distinct(self):
        for state in ['missing','nil','not_applicable','conflicting','unresolved']:
            with self.subTest(state=state):
                result=a.ratio('test',fact(None,state=state),fact('10'))
                self.assertEqual(result['state'],'unavailable')
                self.assertIsNone(result['value'])
        self.assertEqual(a.ratio('test',fact('0',state='explicit_zero'),fact('10'))['value'],'0.0000')
        self.assertIsNone(a.ratio('test',fact('10'),fact('0',state='explicit_zero'))['value'])

    def test_loss_profitability_and_cash_conversion_policy(self):
        self.assertEqual(a.ratio('profit_margin',fact('-20'),fact('100'))['value'],'-20.0000')
        self.assertIsNone(a.ratio('cash_conversion',fact('10'),fact('-20'),Decimal(1))['value'])

    def test_mismatched_basis_unit_period_company_are_ineligible(self):
        for field,value in [('basis','consolidated'),('currency','USD'),('raw_unit','INR million'),('period_end','2025-03-31'),('company_id','other')]:
            with self.subTest(field=field):
                denominator=fact('100');denominator[field]=value
                self.assertEqual(a.ratio('test',fact('50'),denominator)['state'],'unavailable')

    def test_consecutive_yoy_and_elapsed_year_cagr(self):
        first,last=fact('100',end='2024-03-31'),fact('121')
        self.assertEqual(a.cagr(first,last)['value'],'10.0000')
        self.assertEqual(a.growth(last,first)['state'],'unavailable')
        self.assertEqual(a.growth(fact('110'),fact('100',end='2025-03-31'))['value'],'10.0000')
        interim=fact('110');interim['period_start']='2025-10-01'
        self.assertEqual(a.growth(interim,fact('100',end='2025-03-31'))['state'],'unavailable')

    def test_real_secondary_snapshot_and_component_residuals(self):
        snapshot=build()
        self.assertEqual(snapshot['company']['id'],'igx')
        self.assertEqual(len(snapshot['observations']),15)
        self.assertEqual(snapshot['coverage']['primary_reviewed'],0)
        for period in snapshot['periods']:
            residual=next(m for m in period['metrics'] if m['id']=='income_residual')
            self.assertEqual(residual['value'],'0.0000')
        negative=next(f for f in snapshot['observations'] if f['metric_id']=='cfo' and f['period_end']=='2024-03-31')
        self.assertEqual(a.amount(negative),Decimal('-189.82'))
        self.assertEqual(build()['snapshot_id'],snapshot['snapshot_id'])
        self.assertNotEqual(build(reference=True)['snapshot_id'],snapshot['snapshot_id'])
        self.assertEqual(build(reference=True)['company']['status'],'Recent IPO reference')

    def test_scenario_arithmetic_lineage_and_rejected_commands(self):
        snapshot=build()
        command={'company_id':'igx','period_end':'2026-03-31','growth_pct':'10','profit_pct':'50'}
        result=a.scenario(snapshot,command)
        self.assertEqual(result['hypothetical_operating_revenue'],'67.1110')
        self.assertEqual(result['hypothetical_continuing_profit'],'33.5555')
        self.assertEqual(result['snapshot_id'],snapshot['snapshot_id'])
        for key,value in [('growth_pct','NaN'),('profit_pct','Infinity'),('growth_pct',31),('profit_pct',-1),('growth_pct',True),('period_end','2030-03-31'),('company_id','unknown')]:
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                a.scenario(snapshot,{**command,key:value})
        for invalid in [None,[],{**command,'unexpected':1}]:
            with self.assertRaises(ValueError): a.scenario(snapshot,invalid)

class HTTPContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler(build(),build(reference=True)))
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_http_projection_and_invalid_scenario(self):
        with urlopen(self.base+'/api/snapshot',timeout=5) as response:
            self.assertEqual(json.load(response)['company']['id'],'igx')
        for command in [None,[],{'company_id':'unknown'}]:
            request=Request(self.base+'/api/scenario',data=json.dumps(command).encode(),headers={'Content-Type':'application/json'})
            with self.assertRaises(HTTPError) as error: urlopen(request,timeout=5)
            self.assertEqual(error.exception.code,400)
        with self.assertRaises(HTTPError) as error: urlopen(self.base+'/../AGENTS.md',timeout=5)
        self.assertEqual(error.exception.code,404)

if __name__=='__main__': unittest.main()
