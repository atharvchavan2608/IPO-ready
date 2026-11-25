"""Bounded source capture.

Every request goes to an explicit URL built from ipo_ready/universe.json. Each run writes
native bytes, a SHA-256 and the HTTP outcome (including failures) into
data/captures/<source>/<run_id>/manifest.json. Nothing here parses or interprets content.

Usage: python -m ipo_ready.capture [--sources wwipl,news,screener,nse_eod,issuer]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import time
from pathlib import Path
from urllib.parse import quote_plus

import requests

from .config import CAPTURES, MAX_BYTES, REQUEST_DELAY_S, TIMEOUT_S, USER_AGENT, load_universe
from .peer_context import CONTEXT_SOURCES
from .portfolio_terms import TERMS_SOURCES

SESSION = requests.Session()
SESSION.headers["User-Agent"] = USER_AGENT

ISSUER_DOCS = {
    "igx": {
        "referrer": "https://www.igxindia.com/investor-relation",
        "docs": {
            "igx-restated-financials": ("https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf",
                                        "Restated Financial Information (FY24-FY26), auditor's examination report"),
            "igx-abridged-prospectus": ("https://testwebcms.igxindia.com/files/draft-abridged-prospectus-fDGrlKdPZUzDwuNSY2ee.pdf",
                                        "Draft abridged prospectus"),
            "igx-drhp": ("https://testwebcms.igxindia.com/files/drhp-6w0Qkr9JEHUyvsQQbc1.pdf",
                         "Draft Red Herring Prospectus"),
        },
    }
}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def run_id() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def fetch(url: str, max_bytes: int = MAX_BYTES) -> dict:
    """GET one URL with a byte cap. Returns a record; never raises."""
    rec: dict = {"url": url, "retrieved_at": utc_now().isoformat(timespec="seconds")}
    try:
        r = SESSION.get(url, timeout=TIMEOUT_S, stream=True)
        rec["status"] = r.status_code
        rec["final_url"] = r.url
        rec["content_type"] = r.headers.get("content-type")
        buf = bytearray()
        for chunk in r.iter_content(65536):
            buf.extend(chunk)
            if len(buf) > max_bytes:
                rec["error"] = f"response exceeds {max_bytes} byte cap"
                return rec
        rec["_body"] = bytes(buf)
        rec["bytes"] = len(buf)
        rec["sha256"] = hashlib.sha256(buf).hexdigest()
        if r.status_code != 200:
            rec["error"] = f"HTTP {r.status_code}"
    except requests.RequestException as exc:  # network failure is data, not a crash
        rec["status"] = None
        rec["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
    return rec


def _save(folder: Path, name: str, rec: dict) -> dict:
    body = rec.pop("_body", None)
    if body is not None and rec.get("status") == 200:
        (folder / name).write_bytes(body)
        rec["path"] = name
    return rec


def _write_manifest(folder: Path, source: str, items: list[dict], extra: dict | None = None) -> Path:
    ok = sum(1 for i in items if i.get("status") == 200 and "error" not in i)
    manifest = {"source": source, "run_id": folder.name, "items": items,
                "summary": {"attempted": len(items), "ok": ok, "failed": len(items) - ok}}
    if extra:
        manifest.update(extra)
    p = folder / "manifest.json"
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def capture_wwipl(rid: str, companies: list[str] | None = None) -> Path:
    universe = load_universe()["unlisted"]
    if companies is not None and not set(companies) <= {c["id"] for c in universe}:
        raise ValueError("Unknown unlisted company in capture selection")
    folder = CAPTURES / "wwipl" / rid
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    for c in universe:
        if companies is not None and c["id"] not in companies:
            continue
        for kind, suffix in (("overview", ""), ("financial", "/financial")):
            url = f"https://wwipl.com/unlisted-shares/{c['wwipl_slug']}{suffix}"
            rec = fetch(url, 2_000_000)
            rec.update(id=f"{c['id']}-{kind}", company=c["id"], kind=kind)
            items.append(_save(folder, f"{c['id']}-{kind}.html", rec))
            print(f"  wwipl {c['id']:16s} {kind:9s} {rec.get('status')} {rec.get('error', '')}")
            time.sleep(REQUEST_DELAY_S)
    return _write_manifest(folder, "wwipl", items, {"robots_note": "wwipl.com/robots.txt (2026-11-23) does not disallow /unlisted-shares/"})


def capture_news(rid: str, companies: list[str] | None = None) -> Path:
    uni = load_universe()
    folder = CAPTURES / "news" / rid
    folder.mkdir(parents=True, exist_ok=True)
    queries = [(c["id"], c["news_query"]) for c in uni["unlisted"]] + [("_market", uni["general_news_query"])]
    items = []
    for cid, q in queries:
        if companies is not None and cid not in companies:
            continue
        url = f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-IN&gl=IN&ceid=IN:en"
        rec = fetch(url, 2_000_000)
        rec.update(id=f"news-{cid}", company=cid, query=q)
        items.append(_save(folder, f"news-{cid}.xml", rec))
        print(f"  news  {cid:16s} {rec.get('status')} {rec.get('error', '')}")
        time.sleep(REQUEST_DELAY_S)
    return _write_manifest(folder, "news", items, {"note": "Google News RSS search: headline, publisher, date and link only"})


def capture_screener(rid: str, symbols: list[str] | None = None) -> Path:
    configured = {s for c in load_universe()["unlisted"] for s in c["listed_peers"]}
    selected = configured if symbols is None else set(symbols)
    if not selected <= configured:
        raise ValueError(f"Unknown listed symbols: {sorted(selected - configured)}")
    folder = CAPTURES / "screener" / rid
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    for sym in sorted(selected):
        for basis, suffix in (("consolidated", "consolidated/"), ("standalone", "")):
            url = f"https://www.screener.in/company/{sym}/{suffix}"
            rec = fetch(url, 3_000_000)
            rec.update(id=f"{sym}-{basis}", symbol=sym, basis=basis)
            items.append(_save(folder, f"{sym}-{basis}.html", rec))
            print(f"  scr   {sym:12s} {basis:12s} {rec.get('status')} {rec.get('error', '')}")
            time.sleep(REQUEST_DELAY_S)
    return _write_manifest(folder, "screener", items, {"robots_note": "screener.in/robots.txt (2026-11-23) does not disallow /company/<symbol>/"})


def capture_peer_context(rid: str, source_ids: list[str] | None = None) -> Path:
    if source_ids is not None and not set(source_ids) <= CONTEXT_SOURCES.keys():
        raise ValueError("Unknown company disclosure or reporting source")
    folder = CAPTURES / "peer_context" / rid
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    for source_id, (url, ext, limit) in CONTEXT_SOURCES.items():
        if source_ids is not None and source_id not in source_ids:
            continue
        record = fetch(url, limit)
        record["id"] = source_id
        items.append(_save(folder, f"{source_id}.{ext}", record))
        print(f"  peer context {source_id:20s} {record.get('status')} {record.get('error', '')}")
        time.sleep(REQUEST_DELAY_S)
    return _write_manifest(folder, "peer_context", items)


def _nse_dates(today: dt.date, daily_days: int, weeks: int) -> list[dt.date]:
    dates = set()
    for k in range(daily_days):
        d = today - dt.timedelta(days=k)
        if d.weekday() < 5:
            dates.add(d)
    # weekly samples: each Friday going back (holiday fallback handled at fetch time)
    last_friday = today - dt.timedelta(days=(today.weekday() - 4) % 7)
    for w in range(weeks + 1):
        dates.add(last_friday - dt.timedelta(weeks=w))
    return sorted(dates)


def capture_nse_eod(rid: str, today: dt.date | None = None) -> Path:
    """Official NSE end-of-day archives. Incremental: a date already stored is not refetched.

    Index file kept whole (small). The full equity bhavcopy (~400 KB) is reduced to the selected
    symbols; the original file's SHA-256 and size are recorded so the extract can be re-verified.
    """
    uni = load_universe()
    store = CAPTURES / "nse_eod" / "store"
    store.mkdir(parents=True, exist_ok=True)
    folder = CAPTURES / "nse_eod" / rid
    folder.mkdir(parents=True, exist_ok=True)
    index_path = store / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    today = today or utc_now().date()
    wanted = set(uni["market"]["stocks"])
    items = []
    for d in _nse_dates(today, uni["market"]["daily_lookback_days"], uni["market"]["weekly_lookback_weeks"]):
        key = d.isoformat()
        if key in index and index[key].get("ok"):
            continue
        ddmmyyyy = d.strftime("%d%m%Y")
        entry = {"date": key}
        rec_i = fetch(f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{ddmmyyyy}.csv", 1_000_000)
        time.sleep(REQUEST_DELAY_S / 2)
        if rec_i.get("status") == 200 and rec_i.get("_body", b"").startswith(b"Index Name"):
            (store / f"ind_close_all_{ddmmyyyy}.csv").write_bytes(rec_i.pop("_body"))
            rec_i["path"] = f"store/ind_close_all_{ddmmyyyy}.csv"
            rec_b = fetch(f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{ddmmyyyy}.csv", 3_000_000)
            time.sleep(REQUEST_DELAY_S / 2)
            body = rec_b.pop("_body", b"")
            if rec_b.get("status") == 200 and body:
                rows = list(csv.reader(io.StringIO(body.decode("utf-8", "replace"))))
                header = [h.strip() for h in rows[0]]
                keep = [r for r in rows[1:] if r and r[0].strip() in wanted and r[1].strip() in ("EQ", "BE")]
                out = io.StringIO()
                w = csv.writer(out, lineterminator="\n")
                w.writerow(header)
                w.writerows([[x.strip() for x in r] for r in keep])
                (store / f"bhav_selected_{ddmmyyyy}.csv").write_text(out.getvalue(), encoding="utf-8")
                rec_b["path"] = f"store/bhav_selected_{ddmmyyyy}.csv"
                rec_b["derived"] = f"extract of {len(keep)} selected symbol rows from original file (sha256 above)"
            entry.update(ok=True, index=rec_i, bhav=rec_b)
        else:
            rec_i.pop("_body", None)
            entry.update(ok=False, index=rec_i, reason="no index file (market holiday, weekend or not yet published)")
        items.append(entry)
        index[key] = entry
        print(f"  nse   {key} {'ok' if entry.get('ok') else 'none'}")
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    ok = sum(1 for i in items if i.get("ok"))
    manifest = {"source": "nse_eod", "run_id": rid, "items": items,
                "summary": {"attempted_dates": len(items), "ok": ok, "stored_dates": sum(1 for v in index.values() if v.get("ok"))}}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return folder / "manifest.json"


def capture_issuer(rid: str, force: bool = False) -> Path:
    """Issuer documents. Skips a document already captured (same URL, hash on file) unless force."""
    folder = CAPTURES / "issuer" / rid
    folder.mkdir(parents=True, exist_ok=True)
    previous = {}
    for m in sorted((CAPTURES / "issuer").glob("*/manifest.json")):
        for it in json.loads(m.read_text(encoding="utf-8"))["items"]:
            if it.get("sha256") and it.get("status") == 200:
                previous[it["url"]] = (m.parent.name, it)
    items = []
    for cid, spec in ISSUER_DOCS.items():
        for doc_id, (url, title) in spec["docs"].items():
            if url in previous and not force:
                prev_run, it = previous[url]
                items.append({**it, "id": doc_id, "company": cid, "title": title, "reused_from_run": prev_run})
                print(f"  iss   {doc_id} reused from {prev_run}")
                continue
            rec = fetch(url, 40_000_000)
            rec.update(id=doc_id, company=cid, title=title, referrer=spec["referrer"])
            items.append(_save(folder, f"{doc_id}.pdf", rec))
            print(f"  iss   {doc_id} {rec.get('status')} {rec.get('error', '')}")
            time.sleep(REQUEST_DELAY_S)
    return _write_manifest(folder, "issuer", items)


YAHOO_SYMBOLS = {"^BSESN": "S&P BSE Sensex", "^NSEI": "Nifty 50"}


def capture_yahoo(rid: str) -> Path:
    """Unofficial Yahoo Finance chart JSON (delayed). Used for Sensex, which has no free official
    machine-readable file verified in this build, and for an intraday Nifty line. Owner direction
    2026-11-23: robots.txt is not a blocker at prototype stage; requests stay bounded."""
    folder = CAPTURES / "yahoo" / rid
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    for sym, name in YAHOO_SYMBOLS.items():
        for rng, interval in (("1y", "1d"), ("1d", "5m")):
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote_plus(sym)}?range={rng}&interval={interval}"
            rec = fetch(url, 2_000_000)
            safe = sym.strip("^").lower()
            rec.update(id=f"{safe}-{rng}", symbol=sym, name=name, range=rng, interval=interval)
            items.append(_save(folder, f"{safe}-{rng}.json", rec))
            print(f"  yahoo {sym} {rng} {rec.get('status')} {rec.get('error', '')}")
            time.sleep(REQUEST_DELAY_S)
    return _write_manifest(folder, "yahoo", items, {"note": "unofficial endpoint; delayed quotes; fallback to last good capture"})


def capture_portfolio_terms(rid: str) -> Path:
    folder = CAPTURES / "portfolio_terms" / rid
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    for item_id, source in TERMS_SOURCES.items():
        rec = fetch(source["url"])
        rec["id"] = item_id
        body = rec.get("_body", b"")
        if rec.get("status") == 200 and source["marker"] not in body:
            rec["error"] = "response does not contain the expected document marker"
            rec.pop("_body", None)
        items.append(_save(folder, f"{item_id}.{source['extension']}", rec))
    return _write_manifest(folder, "portfolio_terms", items)


CAPTURERS = {"wwipl": capture_wwipl, "news": capture_news, "screener": capture_screener,
             "nse_eod": capture_nse_eod, "issuer": capture_issuer, "yahoo": capture_yahoo,
             "peer_context": capture_peer_context, "portfolio_terms": capture_portfolio_terms}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", default=",".join(CAPTURERS))
    args = ap.parse_args(argv)
    rid = run_id()
    for s in args.sources.split(","):
        print(f"[capture] {s} run {rid}")
        CAPTURERS[s](rid)


if __name__ == "__main__":
    main()
