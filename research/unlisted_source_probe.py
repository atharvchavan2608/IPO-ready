"""Bounded free-source capture. No login, challenge bypass or crawler discovery.

Each run preserves HTTP bodies (including error bodies) and their SHA-256.
An HTTP 200 is access evidence, not proof of financial accuracy or reuse rights.
"""
from datetime import datetime, timezone
import argparse
from hashlib import sha256
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SOURCES = {
    'wwipl-nse-financials': 'https://wwipl.com/unlisted-shares/nse-india-unlisted-shares-price/financial',
    'unlistedzone-nse': 'https://unlistedzone.com/shares/nse-india-limited-unlisted-shares',
    'nse-financials-index': 'https://www.nseindia.com/static/investor-relations/financials',
    'nsdl-reports-index': 'https://nsdl.com/annual-reports',
}
FOLLOWUP = {
    'wwipl-igx-financials': 'https://wwipl.com/unlisted-shares/indian-gas-exchange-share-price/financial',
    'nse-listing-status': 'https://nsearchives.nseindia.com/web/pressrelease/2026-11/PR_cc_03112026_20261103175822.pdf',
    'igx-parent-transcript': 'https://nsearchives.nseindia.com/corporate/IEX_05112026110840_IEX_Intimation_EarningCall_Transcript_Q2_Sep26Signed.pdf',
    'chittorgarh-home': 'https://www.chittorgarh.com/',
    'chittorgarh-hosted-nsdl-note': 'https://www.chittorgarh.net/reports/ipo_notes/national-securities-depository-ltd-ipo-retail-note.pdf',
    'icici-hdb-note': 'https://www.icicidirect.com/mailcontent/idirect_hdbfinancials_iporeview.pdf',
}
EDITORIAL = {'chittorgarh-review-index': 'https://www.chittorgarh.com/report/ipo-review-and-rating-india/73/mainboard/'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--followup', action='store_true')
    parser.add_argument('--editorial', action='store_true')
    parser.add_argument('--issuer-status', action='store_true')
    args = parser.parse_args()
    run = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = Path(__file__).parent / 'unlisted_sources_20261112' / run
    target.mkdir(parents=True, exist_ok=False)
    rows = []
    selected = {'nse-listing-status': FOLLOWUP['nse-listing-status']} if args.issuer_status else EDITORIAL if args.editorial else FOLLOWUP if args.followup else SOURCES
    limit = 16_000_000 if args.issuer_status else 5_000_000
    for name, url in selected.items():
        row = {'id': name, 'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
               'source_date': None, 'timeout_seconds': 12, 'max_capture_bytes': limit, 'evidence_type': 'HTTP access experiment'}
        try:
            req = Request(url, headers={'User-Agent': 'IPO-Ready-research/0.1 (bounded public academic research)'})
            with urlopen(req, timeout=12) as response:
                body = response.read(limit + 1)
                if len(body) > limit:
                    raise ValueError(f'Response exceeds bounded {limit} byte capture')
                row.update(status=response.status, final_url=response.url,
                           content_type=response.headers.get('Content-Type'))
        except HTTPError as exc:
            body = exc.read(5_000_000)
            row.update(status=exc.code, error=str(exc), evidence_type='HTTP error body, not financial evidence')
        except Exception as exc:
            row.update(status=None, error=str(exc))
            rows.append(row)
            continue
        extension = '.pdf' if row.get('content_type', '').startswith('application/pdf') else '.html'
        name_on_disk = name + (extension if row['status'] == 200 else '.error')
        (target / name_on_disk).write_bytes(body)
        row.update(path=name_on_disk, bytes=len(body), sha256=sha256(body).hexdigest())
        rows.append(row)
    (target / 'manifest.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'directory': str(target), 'outcomes': [{k: r.get(k) for k in ['id', 'status', 'error', 'bytes']} for r in rows]}, indent=2))

if __name__ == '__main__':
    main()
