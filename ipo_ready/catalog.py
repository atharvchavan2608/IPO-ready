"""Shared company records for listed, unlisted and identity-only issuers."""
from __future__ import annotations

import json
from pathlib import Path

from . import metrics as M
from .cash_flow import build_cash_flow
from .company import Evidence, FIELD_LABELS
from .config import ROOT
from .issuer import sha256_file
from .parse_screener import parse_screener

LISTED = {
    "IEX": ("Indian Energy Exchange Limited", "Exchange", "exchange"),
    "MCX": ("Multi Commodity Exchange of India Limited", "Exchange", "exchange"),
    "AETHER": ("Aether Industries Limited", "Specialty chemicals", "manufacturer"),
}
EXTRA_FIELDS = {
    "fixed_assets": "Fixed assets", "borrowings": "Borrowings", "net_change": "Net change in cash",
    "provider_roce": "Provider ROCE",
}


def _period(date: str) -> str:
    return "FY" + date[:4] if date.endswith("-03-31") else "PE:" + date


def build_listed_company(symbol: str, item: dict | None, stock: dict | None, *,
                         identity: dict | None = None, classification: tuple[str, str] | None = None) -> dict:
    if identity:
        sector, model = classification or ("Sector unclassified", "unknown")
        name = identity["name"]
    else:
        name, sector, model = LISTED[symbol]
    evidence = Evidence()
    raw = parse_screener(item) if item else {}
    source = raw.get("source", {})
    annual = raw.get("annual", {}) if raw.get("state") == "ok" else {}
    basis = raw.get("basis") or "unknown"
    periods = [_period(period) for period in sorted(annual)]
    identity_ev = None
    if identity:
        identity_ev = evidence.add(identity["evidence"])
    elif symbol == "AETHER":
        directory = ROOT / "research" / "xbrl_stage2_20261022"
        manifest = directory / "aether_q2_fy26.manifest.json"
        aether_source = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
        native = directory / "aether_q2_fy26.pdf"
        if native.is_file() and aether_source.get("sha256") == sha256_file(native):
            identity_ev = evidence.add({
                "source": "Aether Industries · results filed with NSE and BSE", "url": aether_source["url"] + "#page=1",
                "raw_label": "NSE symbol and issuer name", "raw_text": "AETHER · Aether Industries Limited",
                "file": native.name, "sha256": aether_source["sha256"], "retrieved_at": aether_source.get("retrieved_on"),
                "page": 1,
            })
    if identity_ev is None and stock and stock.get("state") == "ok":
        quote_source = stock["source"]
        identity_ev = evidence.add({**quote_source, "source": "NSE end-of-day file", "raw_label": "Symbol",
                                    "raw_text": symbol, "anchor": {"symbol": symbol, "field": "SYMBOL"}})
    quote = {"price_inr": None, "as_of": None, "state": "unavailable", "ev": None, "kind": "NSE end-of-day close"}
    if stock and stock.get("state") == "ok" and stock.get("close"):
        quote.update(price_inr=str(stock["close"]), as_of=stock["date"], state="reported",
                     ev=evidence.add({**stock["source"], "source": "NSE end-of-day file", "raw_label": "Close price",
                                      "raw_text": str(stock["close"]), "raw_unit": "INR per share",
                                      "anchor": {"symbol": symbol, "field": "CLOSE_PRICE"}}))
    fields = {}
    for key, label in (FIELD_LABELS | EXTRA_FIELDS).items():
        cells = {}
        for date, facts in sorted(annual.items()):
            p = _period(date)
            raw_cell = facts.get(key)
            if not raw_cell or raw_cell["basis"] != basis:
                cells[p] = {"value": None, "state": "conflict" if raw_cell else "not_in_source"}
                continue
            eid = evidence.add({**source, "source": "Screener.in annual financials", "capture_run": source["run"],
                                **raw_cell, "period": p, "period_end": date})
            cells[p] = {"value": raw_cell["value"], "state": raw_cell["state"], "ev": eid}
        unit = "INR per share" if key.startswith("eps") else "%" if key == "provider_roce" else "INR crore"
        fields[key] = {"label": label, "unit": unit, "by_period": cells}
    latest = periods[-1] if periods else None
    eps = fields["eps"]["by_period"].get(latest, {})
    valuation = {key: M.result(None, M.MISSING, "", {}) for key in ("market_cap", "pb", "ps", "eps", "pe_reported", "pe_proxy")}
    valuation["pe"] = {**M.pe(quote["price_inr"], eps.get("value")), "eps_basis": "provider_annual_eps",
                       "note": "Annual EPS from Screener.in. The source does not specify basic or diluted EPS.",
                       "ev": [key for key in (eps.get("ev"), quote["ev"]) if key]}
    record = {
        "id": identity["id"] if identity else f"nse-{symbol.lower()}", "name": name, "short": symbol,
        "hierarchy": ["Listed", sector],
        "model": model, "market_status": "Listed on NSE", "status_note": None, "periods": periods,
        "basis": basis, "layout": "annual statements" if periods else "identity record",
        "statement_provider": "Screener.in", "raw_units": ["INR crore"] if periods else [],
        "fields": fields, "metrics": {p: {} for p in periods}, "valuation": valuation,
        "profile": {"ev": identity_ev, "description": ""}, "quote": quote, "documents": [], "news": {},
        "checks": [], "coverage_gaps": [] if periods else [{"field": "statements and quote", "state": "unavailable"}],
        "agent": {}, "discovery": [], "reconciliation": None, "evidence": evidence.items,
        "identity": {"key": f"NSE:{symbol}", "state": "verified" if identity_ev else "unavailable",
                     "listing": "listed", "ev": identity_ev, "symbol": symbol,
                     **({"isin": identity["isin"]} if identity else {"isin": "INE0BWX01014"} if symbol == "AETHER" else {})},
    }
    record["cash_flow"] = build_cash_flow(record, None, evidence)
    return record


def catalog_row(company: dict) -> dict:
    periods = company["periods"]
    return {key: company[key] for key in ("id", "name", "short", "hierarchy", "model", "identity", "basis")} | {
        "periods": periods, "latest_period": periods[-1] if periods else None,
        "price_inr": company["quote"]["price_inr"], "quote_as_of": company["quote"]["as_of"],
        "coverage": "annual" if periods else "identity_only", "ipo_stage": company.get("ipo_stage"),
    }


def build_catalog(companies: dict, screener: dict, market: dict) -> tuple[dict, list[dict]]:
    """Keep Page 1 and the workspace on one per-company fact file."""
    stocks = {s["symbol"]: s for s in market["stocks"]}
    listed = {symbol: build_listed_company(symbol, screener.get(f"{symbol}-standalone"), stocks.get(symbol))
              for symbol in LISTED}
    for co in companies.values():
        profile = co["profile"]
        is_reference = co["id"] == "nse"
        external_id = profile.get("isin") or profile.get("cin")
        co["identity"] = {"key": external_id or co["id"], "isin": profile.get("isin"), "cin": profile.get("cin"),
                          "listing": "reference" if is_reference else "unlisted",
                          "state": "provider_identity" if external_id else "catalog_identity", "ev": profile["ev"]}
    rows = [catalog_row(company) for company in [*companies.values(), *listed.values()]]
    return {company["id"]: company for company in listed.values()}, rows
