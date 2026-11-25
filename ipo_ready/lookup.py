"""On-demand NSE identity, source capture and local company projection."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, quote, urlsplit
from uuid import uuid4

import requests
from bs4 import BeautifulSoup

from .catalog import build_listed_company, catalog_row
from .config import CAPTURES, ROOT, USER_AGENT
from .market import _nse_store, _read_bhav
from .ratios import build_ratios
from .research_views import build_research
from .sources import latest_good_items

SOURCE_ROOT = CAPTURES / "company_lookup"
RECORDS = ROOT / "data" / "derived" / "company_lookup"
DIRECTORY = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
BHAVCOPY = "https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{}.csv"
FINANCIALS = "https://www.screener.in/company/{}/"
SYMBOL = re.compile(r"[A-Z0-9][A-Z0-9&-]{0,19}")
IDENTIFIER = re.compile(r"nse-[a-z0-9-]{1,42}")
ISIN = re.compile(r"IN[A-Z0-9]{10}")
WRITE_LOCK = Lock()
SECTORS = {
    "ASTRAL": ("Building products", "manufacturer"),
    "SUNPHARMA": ("Pharmaceutical manufacturing", "manufacturer"),
    "HDFCBANK": ("Banking", "lender"),
    "HINDALCO": ("Metals", "manufacturer"),
    "BSE": ("Exchange", "exchange"),
    "CDSL": ("Depository", "depository"),
}
ARCHIVE_NAMES = {"BSE": "BSE Limited", "CDSL": "Central Depository Services (India) Limited",
                 "HDFCBANK": "HDFC Bank Limited", "HINDALCO": "Hindalco Industries Limited",
                 "IEX": "Indian Energy Exchange Limited", "MCX": "Multi Commodity Exchange of India Limited"}


class LookupError(Exception):
    """A lookup attempt with an explicit availability state."""

    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.status = status


def _id(symbol: str) -> str:
    if "&" in symbol:
        return "nse-" + symbol.lower().replace("&", "-") + "-" + hashlib.sha256(symbol.encode()).hexdigest()[:8]
    return f"nse-{symbol.lower()}"


def _capture(key: str, url: str, kind: str, online: bool) -> dict | None:
    """Reuse a verified body or retain a public source response with its receipt."""
    folder = SOURCE_ROOT / key
    for manifest in sorted(folder.glob("*/receipt.json"), reverse=True):
        record = _retained(manifest)
        if record:
            return record
    if not online:
        return None
    with WRITE_LOCK:
        for manifest in sorted(folder.glob("*/receipt.json"), reverse=True):
            record = _retained(manifest)
            if record:
                return record
            age = dt.datetime.now().timestamp() - manifest.stat().st_mtime
            if age < 60:
                return None
        now = dt.datetime.now(dt.timezone.utc)
        run = now.strftime("%Y%m%dT%H%M%S%fZ")
        target = folder / run
        target.mkdir(parents=True, exist_ok=True)
        record = {"url": url, "retrieved_at": now.isoformat(timespec="seconds"), "run": run}
        try:
            with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=(4, 7), stream=True,
                              allow_redirects=False) as response:
                record["status"] = response.status_code
                record["content_type"] = response.headers.get("Content-Type", "")
                if response.status_code == 200:
                    deadline = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10)
                    body = bytearray()
                    for chunk in response.iter_content(chunk_size=65_536):
                        body.extend(chunk)
                        if len(body) > 3_000_000 or dt.datetime.now(dt.timezone.utc) > deadline:
                            raise ValueError("Capture exceeded bounded read")
                    path = target / f"source.{kind}"
                    path.write_bytes(body)
                    record.update(file=path.name, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        except (requests.RequestException, ValueError) as exc:
            record["error"] = type(exc).__name__
        receipt = target / "receipt.json"
        receipt.write_text(json.dumps(record, indent=2), encoding="utf-8")
        result = _retained(receipt)
        return {**result, "mode": "fetched"} if result else None


@lru_cache(maxsize=96)
def _checked_body(path: Path, sha256: str, revision: tuple[int, int]) -> bytes:
    body = path.read_bytes()
    return body if hashlib.sha256(body).hexdigest() == sha256 else b""


def _retained(receipt: Path) -> dict | None:
    try:
        record = json.loads(receipt.read_text(encoding="utf-8"))
        if record.get("status") != 200 or record.get("file") not in {"source.csv", "source.html"}:
            return None
        path = receipt.parent / record["file"]
        stat = path.stat()
        body = _checked_body(path, record["sha256"], (stat.st_size, stat.st_mtime_ns))
        if body:
            return {**record, "body": body, "abs_path": str(path), "mode": "retained"}
    except (OSError, ValueError, KeyError):
        pass
    return None


def _rows(record: dict, columns: set[str]) -> list[dict]:
    reader = csv.DictReader(io.StringIO(record["body"].decode("utf-8-sig", errors="replace")), skipinitialspace=True)
    if not columns <= set(reader.fieldnames or ()):
        return []
    return [{key: (row.get(key) or "").strip() for key in columns} for row in reader]


def _archived_close(symbol: str, date: str) -> dict | None:
    index, dates = _nse_store()
    if date not in dates:
        return None
    row = _read_bhav(date).get(symbol)
    if not row or row.get("SERIES") != "EQ":
        return None
    path = CAPTURES / "nse_eod" / index[date]["bhav"]["path"]
    info = index[date]["bhav"]
    source = {"url": info["url"], "retrieved_at": info["retrieved_at"], "file": path.name,
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "native_sha256": info.get("sha256")}
    return {"symbol": symbol, "close": row["CLOSE_PRICE"], "date": date, "source": source,
            "mode": "retained", "state": "ok"}


def _directory(online: bool) -> tuple[list[dict], dict]:
    capture = _capture("nse-equities", DIRECTORY, "csv", online)
    if capture:
        try:
            return _directory_rows(capture["abs_path"], capture["sha256"], capture["body"]), capture
        except LookupError:
            pass
    _, dates = _nse_store()
    rows = _read_bhav(dates[-1]) if dates else {}
    records = [{"id": _id(symbol), "symbol": symbol, "name": name, "isin": None}
               for symbol, name in ARCHIVE_NAMES.items() if rows.get(symbol, {}).get("SERIES") == "EQ"]
    if not records:
        raise LookupError("The NSE directory is unavailable. Existing dashboard companies remain accessible.", 503)
    evidence = _archived_close(records[0]["symbol"], dates[-1])["source"]
    return records, {**evidence, "mode": "retained_nse_closes"}


@lru_cache(maxsize=4)
def _directory_rows(path: str, sha256: str, body: bytes) -> list[dict]:
    columns = {"SYMBOL", "NAME OF COMPANY", "SERIES", "ISIN NUMBER"}
    result = {}
    for row in _rows({"body": body}, columns):
        symbol, isin = row["SYMBOL"], row["ISIN NUMBER"]
        if row["SERIES"] == "EQ" and SYMBOL.fullmatch(symbol) and ISIN.fullmatch(isin) and row["NAME OF COMPANY"]:
            result.setdefault(symbol, {"id": _id(symbol), "symbol": symbol, "name": row["NAME OF COMPANY"], "isin": isin})
    if not result:
        raise LookupError("The captured NSE directory does not contain recognised equity records.", 503)
    return list(result.values())


def search(query: str, *, online: bool = True) -> dict:
    name = re.sub(r"^NSE:\s*", "", " ".join(query.split()), flags=re.I).strip()
    if not 2 <= len(name) <= 96 or not re.fullmatch(r"[\w .&()'-]+", name):
        raise LookupError("Enter at least two characters from a name, NSE symbol or ISIN.", 400)
    key = name.casefold()
    rows, directory = _directory(online)
    matches = [row for row in rows if any(key in (row[k] or "").casefold() for k in ("name", "symbol", "isin"))]
    matches.sort(key=lambda row: (not any(key == (row[k] or "").casefold() for k in ("symbol", "isin", "name")),
                                  not row["symbol"].casefold().startswith(key), row["name"].casefold()))
    return {"matches": matches[:8], "count": len(matches), "retrieved_at": directory["retrieved_at"], "mode": directory["mode"]}


def _financials(symbol: str, online: bool) -> dict | None:
    symbol_url = quote(symbol, safe="-")
    retained, _ = latest_good_items("screener")
    for basis, suffix in (("standalone", ""), ("consolidated", "consolidated/")):
        key, url = _id(symbol) + "-" + basis, FINANCIALS.format(symbol_url) + suffix
        record = _capture(key, url, "html", False)
        legacy = retained.get(f"{symbol}-{basis}")
        if record is None and legacy:
            path = Path(legacy["abs_path"])
            stat = path.stat()
            body = _checked_body(path, legacy["sha256"], (stat.st_size, stat.st_mtime_ns))
            if body:
                record = {**legacy, "body": body, "mode": "retained"}
        if record is None:
            record = _capture(key, url, "html", online)
        if not record:
            continue
        soup = BeautifulSoup(record["body"], "lxml")
        section = soup.select_one("#profit-loss p")
        if not section or not section.get_text(" ", strip=True).startswith(basis.title()):
            continue
        for link in soup.select('a[href*="/get-quotes/equity"]'):
            target = urlsplit(link["href"])
            if target.hostname == "www.nseindia.com" and parse_qs(target.query).get("symbol") == [symbol]:
                return {**record, "basis": basis}
    return None


def _price(symbol: str, date: str, online: bool) -> dict | None:
    retained = _archived_close(symbol, date)
    if retained:
        return retained
    day = dt.date.fromisoformat(date)
    record = _capture("nse-close-" + day.strftime("%Y%m%d"), BHAVCOPY.format(day.strftime("%d%m%Y")), "csv", online)
    if not record:
        return None
    for row in _rows(record, {"SYMBOL", "SERIES", "DATE1", "CLOSE_PRICE"}):
        if (row["SYMBOL"], row["SERIES"], row["DATE1"].upper()) != (symbol, "EQ", day.strftime("%d-%b-%Y").upper()):
            continue
        try:
            close = Decimal(row["CLOSE_PRICE"])
        except InvalidOperation:
            return None
        if not close.is_finite() or close <= 0:
            return None
        source = {key: record[key] for key in ("url", "retrieved_at", "sha256", "run", "file")}
        return {"symbol": symbol, "close": format(close, "f"), "date": date, "state": "ok", "source": source,
                "mode": record["mode"]}
    return None


def read_acquired(identifier: str) -> dict | None:
    if not IDENTIFIER.fullmatch(identifier):
        return None
    try:
        return json.loads((RECORDS / f"{identifier}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def overlay_catalog(catalog: dict) -> dict:
    if "screen_rows" not in catalog:
        return catalog
    ids = {row["id"] for row in catalog["companies"]}
    isins = {row["identity"].get("isin") for row in catalog["companies"] if row["identity"].get("isin")}
    added = []
    for path in sorted(RECORDS.glob("nse-*.json")):
        receipt = read_acquired(path.stem)
        isin = receipt["row"]["identity"].get("isin") if receipt else None
        if receipt and receipt["row"]["id"] not in ids and (not isin or isin not in isins):
            added.append(receipt)
            if isin:
                isins.add(isin)
    return {**catalog, "companies": [*catalog["companies"], *(item["row"] for item in added)],
            "screen_rows": [*catalog["screen_rows"], *(item["screen"] for item in added)]}


def acquire(symbol: str, *, online: bool = True, history_sessions: int = 1) -> tuple[dict, str]:
    symbol = symbol.strip().upper()
    if not SYMBOL.fullmatch(symbol):
        raise LookupError("Select a valid NSE symbol from the directory results.", 400)
    identifier = _id(symbol)
    saved = read_acquired(identifier)
    if saved and (saved["row"]["coverage"] == "annual" and saved["row"]["price_inr"] is not None or not online):
        return saved, "already_added"
    rows, directory = _directory(online)
    row = next((candidate for candidate in rows if candidate["symbol"] == symbol), None)
    if row is None:
        raise LookupError("That symbol is not in the retained NSE equity directory.", 404)
    directory_source = directory["mode"] != "retained_nse_closes"
    identity = row | {"evidence": {
        "source": "NSE securities available for equity trading" if directory_source else "NSE end-of-day equity data",
        "url": directory["url"],
        "retrieved_at": directory["retrieved_at"], "sha256": directory["sha256"], "file": directory["file"],
        "capture_run": directory.get("run"), "raw_label": f"Equity segment · {symbol}",
        "raw_text": f'{row["name"]} · {row["isin"]}' if row["isin"] else symbol,
        "anchor": "EQUITY_L.csv · EQ series" if directory_source else f"SYMBOL = {symbol} · EQ series",
    }}
    financials = _financials(symbol, online)
    _, dates = _nse_store()
    close_rows = []
    for date in reversed(dates[-max(1, min(history_sessions, 5)):]):
        close = _price(symbol, date, online)
        if close:
            close_rows.append(close)
    close = close_rows[0] if close_rows else None
    company = build_listed_company(symbol, financials, close, identity=identity, classification=SECTORS.get(symbol))
    company["price_history"] = [{"date": item["date"], "close": item["close"]} for item in reversed(close_rows)]
    company["ratios"] = build_ratios(company)
    company["research"] = build_research(company)
    company["lookup"] = {
        "identity": directory["mode"], "financials": financials["mode"] if company["periods"] else "unavailable",
        "quote": close["mode"] if close else "unavailable",
    }
    if close and close["date"] != dates[-1]:
        company["lookup"]["quote"] = "older_retained_close"
    for name, state in company["lookup"].items():
        if state in {"unavailable", "older_retained_close"}:
            company["coverage_gaps"].append({"field": f"lookup {name}", "state": state})
    from .pipeline import summary_row

    record = {"row": catalog_row(company), "company": company, "screen": summary_row(company, {}) | {"listing": "listed"}}
    with WRITE_LOCK:
        previous = read_acquired(identifier)
        if previous and (previous["row"]["coverage"] == "annual" and record["row"]["coverage"] != "annual"
                         or previous["row"]["price_inr"] is not None and close is None):
            return previous, "retained"
        RECORDS.mkdir(parents=True, exist_ok=True)
        temp = RECORDS / f".{uuid4().hex}.tmp"
        try:
            temp.write_text(json.dumps(record, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            temp.replace(RECORDS / f"{identifier}.json")
        finally:
            temp.unlink(missing_ok=True)
    return record, "added"


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("symbols", nargs="+")
    cli.add_argument("--offline", action="store_true")
    cli.add_argument("--history-sessions", type=int, default=1)
    args = cli.parse_args()
    for symbol in args.symbols:
        record, state = acquire(symbol, online=not args.offline, history_sessions=args.history_sessions)
        print(json.dumps({"state": state, "row": record["row"], "sources": record["company"]["lookup"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
