"""Curate 15 whitelisted observations from one retained WWIPL HTML capture.

This is an offline, source-specific reviewed transcription adapter. It does not
collect websites, reconcile issuer filings, or approve accounting definitions.
"""
from datetime import date
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / 'research/unlisted_sources_20261112/20261112T111129759444Z'
IGX_CAPTURE = ROOT / 'research/unlisted_sources_20261112/20261112T111648125604Z'

class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.table, self.row, self.cell = [], None, None, None
    def handle_starttag(self, tag, attrs):
        if tag == 'table': self.table = []
        elif tag == 'tr' and self.table is not None: self.row = []
        elif tag in ('td', 'th') and self.row is not None: self.cell = []
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(' '.join(' '.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None

# Reviewed exact source lexemes, newest first; changes require a new evidence review.
EXPECTED = {
    'operating_revenue': ('Revenue from operations', ['16,601.31', '17,140.68', '14,780.01']),
    'provider_total_income': ('Revenue', ['18,713.37', '19,176.83', '16,433.61']),
    'other_income': ('Other income', ['2,112.06', '2,036.15', '1,653.60']),
    'continuing_profit': ('Profit (Loss) for the period from continuing Operations', ['10,179.53', '11,605.75', '8,305.94']),
    'cfo': ('Net cash from/(used in) operating activities', ['23,836.18', '4,091.49', '29,744.30']),
}
IGX_EXPECTED = {
    'operating_revenue': ('Revenue from operations', ['61.01', '48.80', '34.85']),
    'provider_total_income': ('Revenue', ['84.84', '69.08', '54.62']),
    'other_income': ('Other income', ['23.83', '20.28', '19.77']),
    'continuing_profit': ('Profit (Loss) for the period from continuing Operations', ['42.02', '30.95', '23.05']),
    'cfo': ('Net cash from/(used in) operating activities', ['156.89', '3.29', '-189.82']),
}

def prepare(capture, company_id, expected_values, source_id):
    manifest = json.loads((capture / 'manifest.json').read_text())
    key = 'wwipl-igx-financials' if company_id == 'igx' else 'wwipl-nse-financials'
    source = next(r for r in manifest if r['id'] == key)
    body = (capture / source['path']).read_bytes()
    assert sha256(body).hexdigest() == source['sha256'], 'Native evidence hash changed'
    parser = Tables()
    parser.feed(body.decode('utf-8'))
    income = next(t for t in parser.tables if any(r and r[0] == EXPECTED['continuing_profit'][0] for r in t))
    cash = next(t for t in parser.tables if any(r and r[0] == 'Net increase /(decrease) in cash and cash equivalents' for r in t))
    observations = []
    for metric, (label, expected) in expected_values.items():
        table = cash if metric == 'cfo' else income
        assert table[0][:4] == ['Particulars', '2025-26', '2024-25', '2023-24']
        matches = [r for r in table if r and r[0] == label]
        assert len(matches) == 1 and matches[0][1:4] == expected, (metric, matches)
        for i, value in enumerate(expected):
            year = 2026 - i
            observations.append({
                'id': f'{company_id}-fy{year}-{metric}-wwipl-v1', 'company_id': company_id,
                'metric_id': metric, 'source_label': label, 'raw_value': value,
                'state': 'reported', 'raw_unit': 'INR crore', 'currency': 'INR',
                'period_start': date(year - 1, 4, 1).isoformat(), 'period_end': date(year, 3, 31).isoformat(),
                'basis': 'unspecified', 'accounting_standard': None, 'dimensions': None,
                'source_id': source_id, 'source_url': source['url'], 'source_date': None,
                'retrieved_at': source['retrieved_at'],
                'evidence_path': str((capture / source['path']).relative_to(ROOT)).replace('\\', '/'),
                'evidence_sha256': source['sha256'],
                'locator': {'table': 'CashFlow Statement' if metric == 'cfo' else 'Income Statement', 'row': label, 'column': table[0][i + 1]},
                'review_state': 'transcription_checked',
            })
    return observations

def main():
    observations = prepare(IGX_CAPTURE, 'igx', IGX_EXPECTED, 'N05')
    nse_observations = prepare(CAPTURE, 'nse-india', EXPECTED, 'N02')
    dataset = {'contract_version': 'portal-contract-v1',
        'company': {'id': 'igx', 'name': 'Indian Gas Exchange', 'short_name': 'IGX',
                    'sector': 'Gas market infrastructure', 'market': 'India', 'status': 'Pre-IPO candidate',
                    'status_basis': 'IEX 30 October 2026 earnings call, filed 5 November: IGX IPO process in progress; not a confirmed listing schedule',
                    'status_source_id': 'N06', 'status_source_url': 'https://nsearchives.nseindia.com/corporate/IEX_05112026110840_IEX_Intimation_EarningCall_Transcript_Q2_Sep26Signed.pdf',
                    'status_source_anchor': 'PDF physical page 7, transcript printed page 6, IGX DRHP paragraph'},
        'observations': observations,
        'reference_dataset': {'company': {'id': 'nse-india', 'name': 'National Stock Exchange of India', 'short_name': 'NSE India',
                    'sector': 'Securities market infrastructure', 'market': 'India', 'status': 'Recent IPO reference',
                    'status_basis': 'Issuer November 2026 filing states BSE listing on 24 September 2026; provider unlisted category is stale',
                    'status_source_id': 'N07', 'listing_date': '2026-09-24'}, 'observations': nse_observations},
        'references': [{'id': 'nsdl', 'name': 'National Securities Depository', 'short_name': 'NSDL',
                        'role': 'Recent IPO reference candidate', 'listing_date': '2025-08-06',
                        'source_id': 'N04', 'source_url': 'https://www.msei.in/SX-Content/Listing/Annual-Reports/2025/NSDL-2025.pdf',
                        'source_anchor': "Annual report 2024-25, printed page 61, Update on Listing of Shares of NSDL",
                        'review_basis': 'Selected web-extracted annual-report section; primary bytes not retained',
                        'comparison_state': 'excluded', 'reason': 'Depository business differs from an exchange; no reviewed compatible financial dataset in M1'}],
        'limitations': [
            'Secondary provider observations; source table does not specify standalone or consolidated basis.',
            'Transcription checked against retained HTML; issuer filing reconciliation and accounting review remain pending.',
            'Annual FY24-FY26 slice reconstructed on 12 November 2026. Later interim disclosures are not included.',
            'Public availability/source date is unknown; retrieval date is not an historical availability date.',
            'CFO may include clearing/settlement and client-money movements; cash conversion is descriptive pending review.',
            'No reviewed market price, share basis, peer cohort or primary-approved earnings: valuation and ranking unavailable.',
            'NSE is a recent IPO reference, not currently unlisted. Provider category labels can be stale.',
        ]}
    target = ROOT / 'portal/data/observations.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'active_observations': len(observations), 'reference_observations': len(nse_observations), 'periods': 3, 'output': str(target)}))

if __name__ == '__main__': main()
