"""Assemble Page 3 instrument evidence and price-risk inputs."""

from __future__ import annotations

import datetime as dt
import math
import re
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .market import IST, _nse_store, week_start, weekly_stats
from .portfolio_terms import TERMS_SOURCES


LISTED = (
    ("HDFCBANK", "HDFC Bank", "Bank equity", "Medium", None,
     "Single-company exposure to banking earnings and credit conditions."),
    ("GOLDBEES", "Nippon India ETF Gold BeES", "Physical gold ETF", "Gold exposure", "goldbees-product",
     "Tracks the domestic gold price through physical gold. The fund has tracking risk."),
    ("MCX", "Multi Commodity Exchange of India", "Commodity exchange equity", "High volatility", "mcx-split",
     "Shares in a commodity derivatives exchange. Holding an unlisted exchange alongside it adds sector concentration."),
)
MCX_SPLIT = {"date": "2026-01-02", "factor": 5, "evidence": "mcx-split"}
MIN_WEEKLY_RETURNS = 40
HISTORY_METHOD = ("Sample standard deviation of adjacent weekly log returns × √52. "
                  "Drawdown uses sampled closing prices and can miss intraweek declines. "
                  "Prices exclude dividends and ETF distributions. The ETF series uses exchange prices.")
LIQUID_FUND = ("LIQUIDBEES", "Nippon India ETF Nifty 1D Rate Liquid BeES", "Overnight money market ETF",
               "Lower market risk", "liquidbees-sid", "Overnight repo exposure, with exchange trading and reinvested distributions.")


def _terms_evidence(term_id: str, terms: dict) -> dict:
    source = TERMS_SOURCES[term_id]
    item = terms.get(term_id, {})
    return {"state": "captured" if item else "unavailable",
            **{key: source[key] for key in ("url", "source", "source_date", "anchor")},
            "retrieved_at": item.get("retrieved_at"), "capture_run": item.get("run"),
            "sha256": item.get("sha256"), "file": item.get("path")}


def _bond(terms: dict, as_of: dt.date) -> dict:
    start, end = "2026-07-01", "2026-12-31"
    coupon_source = terms.get("frsb-coupon-2026h2")
    coupon, coupon_raw = None, None
    if coupon_source:
        page = BeautifulSoup(Path(coupon_source["abs_path"]).read_bytes(), "lxml")
        text = " ".join(page.get_text(" ", strip=True).split())
        match = re.search(r"coupon rate on FRSB 2020 \(T\) for the period July 01, 2026, to December 31, 2026,"
                          r" and payable on January 01, 2027, remains at (\d+\.\d+)%", text)
        if match:
            coupon, coupon_raw = float(match[1]), match[0]
    coupon_state = "unavailable" if coupon is None else "reported"
    if coupon is not None and not start <= as_of.isoformat() <= end:
        coupon_state = "outside_effective_period"
    scheme = "frsb-scheme" in terms
    operations = "frsb-operations" in terms
    evidence = {tid: _terms_evidence(tid, terms) for tid in ("frsb-coupon-2026h2", "frsb-scheme", "frsb-operations")}
    evidence["frsb-coupon-2026h2"].update(raw_label="Coupon rate", raw_text=coupon_raw)
    return {
        "id": "FRSB2020T", "name": "Floating Rate Savings Bonds 2020 (Taxable)",
        "kind": "sovereign_bond", "exposure": "Government of India bond", "risk_band": "Lower credit risk",
        "description": "Government of India debt with taxable interest that resets every six months.",
        "liquidity": {"state": "locked" if scheme else "unavailable", "tenor_years": 7 if scheme else None,
                      "face_value_inr": 1000 if operations else None,
                      "note": "Seven-year term. No secondary market. Early redemption is limited to eligible seniors."
                      if scheme else "Scheme liquidity terms unavailable."},
        "coupon": {"state": coupon_state, "rate_pct_pa": coupon, "from": start, "to": end,
                   "payment_date": "2027-01-01", "basis": "Annual coupon rate before tax"},
        "history": {"state": "not_exchange_traded", "points": 0}, "evidence": evidence,
    }


def _nse_evidence(source: dict, symbol: str, date: str, latest: dict) -> dict:
    return {"source": "NSE daily equity bhavcopy", "url": source["url"], "retrieved_at": source["retrieved_at"],
            "sha256": source["sha256"], "file": source["path"], "anchor": f"{date}, {symbol}, CLOSE_PRICE / TURNOVER_LACS",
            "raw_label": "CLOSE_PRICE (INR) / TURNOVER_LACS (₹ lakh)",
            "raw_text": f"{latest['close_raw']} / {latest['turnover_lacs']}",
            "file_note": "SHA-256 of original exchange file. The local CSV contains selected symbols."}


def _listed(spec: tuple, stock: dict, index: dict, terms: dict, common: set[str]) -> dict:
    symbol, name, exposure, risk_band, term_id, description = spec
    evidence = {term_id: _terms_evidence(term_id, terms)} if term_id else {}
    points = [{"date": p["date"], "close_raw": p["close_raw"], "close": p["close_raw"]}
              for p in stock.get("weekly", []) if p["date"] in common]
    split = MCX_SPLIT if symbol == "MCX" and points and points[0]["date"] < MCX_SPLIT["date"] <= points[-1]["date"] else None
    verified = split if split and split["evidence"] in terms else None
    if verified:
        for p in points:
            if p["date"] < verified["date"]:
                p["close"] /= verified["factor"]
    actions = stock.get("split_events", [])
    unverified = [a for a in actions if points and points[0]["date"] < a["date"] <= points[-1]["date"]
                  and (not verified or a["date"] != verified["date"] or a["factor"] != verified["factor"])]
    history = weekly_stats(points, adjacent_weeks_only=True, min_returns=MIN_WEEKLY_RETURNS)
    if unverified or (split and not verified):
        history = {"state": "corporate_action_review", "points": len(points)}
    history.update(price_points=points, split_candidates=unverified, verified_split=verified, method=HISTORY_METHOD)
    quote = {"state": "unavailable"}
    liquidity = {"state": "exchange_traded", "turnover_lacs": None, "turnover_crore": None,
                 "note": "NSE trading depends on market hours, market depth and available orders."}
    if recent := stock.get("series_1m"):
        last = recent[-1]
        if math.isfinite(last["close_raw"]) and last["close_raw"] > 0:
            quote = {"state": "reported", "price_inr": last["close_raw"], "as_of": last["date"], "basis": "NSE end-of-day close"}
        turnover = last["turnover_lacs"]
        if turnover is not None and math.isfinite(turnover) and turnover >= 0:
            liquidity.update(turnover_lacs=turnover, turnover_crore=round(turnover / 100, 2), as_of=last["date"])
        evidence["nse-close"] = _nse_evidence(index[last["date"]]["bhav"], symbol, last["date"], last)
    kind = {"GOLDBEES": "gold_etf", "LIQUIDBEES": "money_market_etf"}.get(symbol, "listed_equity")
    return {"id": symbol, "name": name, "kind": kind,
            "exposure": exposure, "risk_band": risk_band, "description": description,
            "liquidity": liquidity, "history": history, "quote": quote, "evidence": evidence}


def _liquid_fund(stock: dict, index: dict, terms: dict) -> dict:
    fund = _listed(LIQUID_FUND, stock, index, terms, set())
    fund["liquidity"]["lot_verified"] = False
    fund["history"] = {"state": "distribution_history_unavailable"}
    item = terms.get("liquidbees-sid")
    if not item:
        return fund
    try:
        reader = PdfReader(item["abs_path"])
        purchase = " ".join((reader.pages[4].extract_text() or "").split()) if len(reader.pages) > 4 else ""
        performance = " ".join((reader.pages[12].extract_text() or "").split()) if len(reader.pages) > 12 else ""
    except (OSError, PyPdfError):
        return fund
    fund["liquidity"].update(
        lot_verified="1 (one) Unit and in multiples thereof" in purchase,
        note="Trades in whole units on NSE. Price can differ from NAV, and selling requires market liquidity and settlement. "
             "Daily distributions are reinvested. Fractional reinvested units cannot trade on NSE.",
    )
    match = re.search(r"as on September 30, 2025\).*?Returns for the last 1 year (\d+\.\d+)\b", performance)
    if match:
        fund["history"] = {"state": "issuer_reported", "return_pct": float(match[1]), "as_of": "2025-09-30",
                           "basis": "1-year fund return with gross IDCW reinvested",
                           "url": TERMS_SOURCES["liquidbees-sid"]["url"] + "#page=13"}
    return fund


def _workspace_price_history(stocks: dict, index: dict, terms: dict, dates: set[str]) -> dict:
    """Retained NSE sample for shortlisted names outside the fixed portfolio sleeves."""
    histories = {}
    for symbol, stock in stocks.items():
        if symbol == "LIQUIDBEES":
            continue
        record = _listed((symbol, symbol, "", "", None, ""), stock, index, terms, dates)
        history = {key: value for key, value in record["history"].items() if key != "price_points"}
        history["basis"] = "Sampled NSE price return, before dividends and fees"
        history["sources"] = {date: index[date]["bhav"]["url"] for date in (history.get("from"), history.get("to"))
                              if date in index}
        histories[symbol] = {"history": history, "liquidity": record["liquidity"]}
    return histories


def _unlisted(company: dict) -> dict:
    quote, profile = company["quote"], company["profile"]
    value = float(quote["price_inr"]) if quote["price_inr"] is not None else None
    state = quote["state"]
    if company["valuation"]["market_cap"]["state"] == "suspect_quote":
        state = "suspect_quote"
    valid = state == "reported" and value is not None and math.isfinite(value) and value > 0
    evidence = {"dealer-quote": company["evidence"][quote["ev"]]} if quote["ev"] else {}
    lot_raw = profile["lot_size"]
    if profile["ev"]:
        evidence["dealer-lot"] = {**company["evidence"][profile["ev"]], "raw_label": "Lot size", "raw_text": lot_raw}
    lot = lot_raw.replace(",", "") if lot_raw else ""
    lot_shares = int(lot) if re.fullmatch(r"[1-9][0-9]*", lot) else None
    return {"id": company["id"], "name": company["name"], "kind": "unlisted_equity", "status_note": company["market_status"],
            "business_model": company["model"],
            "risk_band": "Limited exit evidence", "history": {"state": "no_verified_trade_series", "points": 0},
            "quote": {"state": state, "price_inr": quote["price_inr"] if valid else None, "as_of": quote["as_of"],
                      "basis": "Indicative dealer quote; date is capture time"},
            "liquidity": {"state": "off_exchange", "lot_raw": lot_raw, "lot_shares": lot_shares,
                          "note": "An exit depends on finding a counterparty and confirming price, lot size and transfer terms."},
            "evidence": evidence}


def build_portfolio(market: dict, companies: list[dict], default_company: str, terms: dict, fallbacks: list[dict],
                    build_id: str) -> dict:
    as_of = dt.datetime.now(IST).date()
    index, _ = _nse_store()
    stocks = {stock["symbol"]: stock for stock in market.get("stocks", [])}
    # Anchor the replay window to the retained market close so an offline rebuild
    # does not discard valid observations merely because the machine date changed.
    market_day = dt.date.fromisoformat(market["as_of"]) if market.get("as_of") else as_of
    window_start = market_day - dt.timedelta(weeks=53)
    sets = []
    for symbol, *_ in LISTED:
        dates = {p["date"] for p in stocks.get(symbol, {}).get("weekly", [])
                 if p["close_raw"] > 0 and math.isfinite(p["close_raw"]) and dt.date.fromisoformat(p["date"]) >= window_start
                 and (week_start(p["date"]) < week_start(market_day.isoformat()) or dt.date.fromisoformat(p["date"]).weekday() >= 4)}
        if dates:
            sets.append(dates)
    common = set.intersection(*sets) if sets else set()
    ordered = sorted(common)
    missing = (week_start(ordered[-1]) - week_start(ordered[0])).days // 7 + 1 - len(ordered) if ordered else None
    weekly_sources = {date: {key: index[date]["bhav"][key] for key in ("url", "retrieved_at", "sha256", "path")}
                      for date in ordered}
    return {
        "build_id": build_id, "as_of": as_of.isoformat(), "market_date": market.get("as_of"), "default_company": default_company,
        "using_previous_market_capture": market.get("simulated_failure", False), "terms_fallbacks": fallbacks,
        "instruments": [_bond(terms, as_of), *[_listed(spec, stocks.get(spec[0], {}), index, terms, common) for spec in LISTED]],
        "workspace_instruments": [_liquid_fund(stocks.get("LIQUIDBEES", {}), index, terms)],
        "listed_history": _workspace_price_history(stocks, index, terms, common),
        "unlisted": [_unlisted(co) for co in sorted(companies, key=lambda co: co["name"].casefold())],
        "history_coverage": {"from": ordered[0] if ordered else None, "to": ordered[-1] if ordered else None,
                             "points": len(ordered), "missing_weeks": missing, "min_returns": MIN_WEEKLY_RETURNS,
                             "method": HISTORY_METHOD, "sources": weekly_sources},
    }
