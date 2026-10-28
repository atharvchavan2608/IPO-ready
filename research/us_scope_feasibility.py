"""Bounded source-access check; no extraction or financial validation.

Run from the project root: python research/us_scope_feasibility.py
Each run preserves its own native response bytes and SHA-256 manifest.
"""
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import hashlib
import json
import time

SOURCES = [
    ("U01", "sec_api.html", "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"),
    ("U02", "sec_access.html", "https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data"),
    ("U03", "sec_nonpublic_review.html", "https://www.sec.gov/about/divisions-offices/division-corporation-finance/draft-registration-statement-processing-procedures-expanded"),
    ("U04", "form_f1.pdf", "https://www.sec.gov/files/formf-1.pdf"),
    ("U05", "public_companies.html", "https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/public-companies"),
    ("U06", "reddit_s1_index.html", "https://www.sec.gov/Archives/edgar/data/1713445/000162828024006294/0001628280-24-006294-index.htm"),
    ("U06", "reddit_submissions.json", "https://data.sec.gov/submissions/CIK0001713445.json"),
    ("U06", "reddit_companyfacts.json", "https://data.sec.gov/api/xbrl/companyfacts/CIK0001713445.json"),
]


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    root = Path("research/us_scope_20261022") / stamp
    root.mkdir(parents=True, exist_ok=False)
    records = []
    for source_id, filename, url in SOURCES:
        row = {"source_id": source_id, "url": url,
               "requested_at_utc": datetime.now(timezone.utc).isoformat()}
        req = Request(url, headers={
            "User-Agent": "IPOReadyResearch/0.1 (academic project; bounded source feasibility check)",
            "Accept-Encoding": "identity",
        })
        try:
            with urlopen(req, timeout=12) as response:
                data = response.read()
                row.update(status=response.status, content_type=response.headers.get("Content-Type"),
                           final_url=response.url)
        except HTTPError as exc:
            data = exc.read()
            row.update(status=exc.code, error=str(exc))
            filename += ".error"
        except Exception as exc:
            data = None
            row.update(status="request_failed", error=f"{type(exc).__name__}: {exc}")
        if data is not None:
            (root / filename).write_bytes(data)
            row.update(file=filename, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            if row["status"] == 200 and filename.endswith(".json"):
                try:
                    payload = json.loads(data)
                    row["top_level_keys"] = list(payload)
                    if "filings" in payload:
                        recent = payload["filings"]["recent"]
                        row["recent_filings_count"] = len(recent.get("form", []))
                        row["recent_ipo_form_rows"] = [
                            {key: recent[key][i] for key in
                             ("form", "filingDate", "accessionNumber", "primaryDocument")}
                            for i, form in enumerate(recent.get("form", []))
                            if form in ("S-1", "S-1/A", "F-1", "F-1/A")
                        ]
                        row["older_history_files"] = payload["filings"].get("files", [])
                    if "facts" in payload:
                        row["taxonomy_concept_counts"] = {
                            name: len(facts) for name, facts in payload["facts"].items()
                        }
                except (ValueError, KeyError, TypeError) as exc:
                    row["json_inventory_error"] = str(exc)
        records.append(row)
        # Persist progress even if a later request is interrupted.
        (root / "manifest.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(json.dumps({"file": filename, "status": row["status"], "bytes": row.get("bytes")}))
        time.sleep(0.6)
    print(f"Evidence: {root}")


if __name__ == "__main__":
    main()
