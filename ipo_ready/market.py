"""Market context from NSE official end-of-day files (primary) and Yahoo chart JSON (Sensex, intraday)."""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
from decimal import Decimal
from pathlib import Path

from .config import CAPTURES, load_universe
from .sources import latest_good_items

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def _nse_store(exclude_latest: bool = False) -> tuple[dict, list[str]]:
    store = CAPTURES / "nse_eod" / "store"
    index = json.loads((store / "index.json").read_text(encoding="utf-8")) if (store / "index.json").exists() else {}
    dates = sorted(d for d, v in index.items() if v.get("ok"))
    if exclude_latest and dates:
        dates = dates[:-1]
    return index, dates


def _read_index_file(date: str) -> dict[str, dict]:
    ddmmyyyy = dt.date.fromisoformat(date).strftime("%d%m%Y")
    path = CAPTURES / "nse_eod" / "store" / f"ind_close_all_{ddmmyyyy}.csv"
    out = {}
    with path.open(encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            out[row["Index Name"].strip()] = row
    return out


def _read_bhav(date: str) -> dict[str, dict]:
    ddmmyyyy = dt.date.fromisoformat(date).strftime("%d%m%Y")
    path = CAPTURES / "nse_eod" / "store" / f"bhav_selected_{ddmmyyyy}.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {r["SYMBOL"]: r for r in csv.DictReader(f)}


def _f(x) -> float | None:
    try:
        return float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None


def price_history(symbol: str, dates: list[str]) -> list[dict]:
    out = []
    for d in dates:
        r = _read_bhav(d).get(symbol)
        if r and _f(r["CLOSE_PRICE"]) is not None:
            out.append({"date": d, "close": _f(r["CLOSE_PRICE"]), "deliv_pct": _f(r.get("DELIV_PER")),
                        "turnover_lacs": _f(r.get("TURNOVER_LACS"))})
    return out


SPLIT_FACTORS = (2, 3, 4, 5, 10, 20)


def adjust_splits(series: list[dict]) -> tuple[list[dict], list[dict]]:
    """Bhavcopy closes are not corporate-action adjusted. A one-step fall whose ratio is within 8 %
    of a common split/bonus factor is treated as a split; earlier closes are divided by the factor.
    Returns (adjusted series, list of detected events). The raw close is kept as 'close_raw'."""
    out = [dict(s, close_raw=s["close"]) for s in series]
    events = []
    for i in range(1, len(out)):
        a, b = out[i - 1]["close_raw"], out[i]["close_raw"]
        if not a or not b or b >= a:
            continue
        r = a / b
        k = min(SPLIT_FACTORS, key=lambda f: abs(r - f))
        if abs(r - k) / k < 0.08:
            events.append({"date": out[i]["date"], "factor": k, "before": a, "after": b})
            for j in range(i):
                out[j]["close"] = out[j]["close"] / k
    return out, events


def week_start(day: str) -> dt.date:
    date = dt.date.fromisoformat(day)
    return date - dt.timedelta(days=date.weekday())


def weekly_stats(series: list[dict], *, adjacent_weeks_only: bool = False, min_returns: int = 2) -> dict:
    """Annualised volatility and max drawdown from weekly-sampled closes (Fridays, holiday gaps kept)."""
    if len(series) < 10:
        return {"state": "insufficient_history", "points": len(series)}
    closes = [s["close"] for s in series]
    if any(not math.isfinite(c) or c <= 0 for c in closes):
        return {"state": "insufficient_history", "points": len(series)}
    rets = [math.log(b["close"] / a["close"]) for a, b in zip(series, series[1:])
            if not adjacent_weeks_only or (week_start(b["date"]) - week_start(a["date"])).days == 7]
    if len(rets) < min_returns:
        return {"state": "insufficient_history", "points": len(series), "return_count": len(rets)}
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    peak, mdd = closes[0], 0.0
    for c in closes:
        peak = max(peak, c)
        mdd = min(mdd, c / peak - 1)
    return {"state": "ok", "points": len(series), "return_count": len(rets),
            "ann_vol_pct": round(math.sqrt(var) * math.sqrt(52) * 100, 2),
            "max_drawdown_pct": round(mdd * 100, 2), "return_pct": round((closes[-1] / closes[0] - 1) * 100, 2),
            "from": series[0]["date"], "to": series[-1]["date"], "method": "log returns of weekly closes x sqrt(52)"}


def _weekly_dates(dates: list[str]) -> list[str]:
    """Last available trading date of each ISO week."""
    by_week: dict[tuple, str] = {}
    for d in dates:
        y, w, _ = dt.date.fromisoformat(d).isocalendar()
        by_week[(y, w)] = max(by_week.get((y, w), d), d)
    return sorted(by_week.values())


def _yahoo() -> tuple[dict, list[dict]]:
    items, fallbacks = latest_good_items("yahoo")
    out = {}
    for iid, it in items.items():
        try:
            res = json.loads(Path(it["abs_path"]).read_text(encoding="utf-8"))["chart"]["result"][0]
        except (KeyError, IndexError, json.JSONDecodeError):
            continue
        ts = res.get("timestamp") or []
        closes = res["indicators"]["quote"][0].get("close") or []
        pts = [{"t": dt.datetime.fromtimestamp(t, IST).isoformat(timespec="minutes"), "close": round(c, 2)}
               for t, c in zip(ts, closes) if c is not None]
        meta = res["meta"]
        out[iid] = {"symbol": it["symbol"], "name": it["name"], "range": it["range"], "points": pts,
                    "last": meta.get("regularMarketPrice"), "prev_close": meta.get("chartPreviousClose") or meta.get("previousClose"),
                    "market_time": dt.datetime.fromtimestamp(meta["regularMarketTime"], IST).isoformat(timespec="minutes") if meta.get("regularMarketTime") else None,
                    "retrieved_at": it["retrieved_at"], "url": it["url"], "sha256": it["sha256"], "run": it["run"]}
    return out, fallbacks


def build_market(simulate_failure: bool = False) -> dict:
    uni = load_universe()
    index, dates = _nse_store(exclude_latest=simulate_failure)
    if not dates:
        return {"state": "unavailable", "note": "no NSE end-of-day files captured"}
    latest = dates[-1]
    prev = dates[-2] if len(dates) > 1 else None
    recent = [d for d in dates if d >= (dt.date.fromisoformat(latest) - dt.timedelta(days=35)).isoformat()]
    weekly = _weekly_dates(dates)
    idx_latest, idx_prev = _read_index_file(latest), (_read_index_file(prev) if prev else {})
    indices = []
    for name in uni["market"]["indices"]:
        r = idx_latest.get(name)
        if not r:
            indices.append({"name": name, "state": "not_in_file"})
            continue
        series = []
        for d in recent:
            rr = _read_index_file(d).get(name)
            if rr:
                series.append({"date": d, "close": _f(rr["Closing Index Value"])})
        wk = [{"date": d, "close": _f(_read_index_file(d)[name]["Closing Index Value"])} for d in weekly if name in _read_index_file(d)]
        indices.append({"name": name, "state": "ok", "close": _f(r["Closing Index Value"]), "change_pct": _f(r["Change(%)"]),
                        "points_change": _f(r["Points Change"]), "pe": _f(r.get("P/E")), "pb": _f(r.get("P/B")),
                        "div_yield": _f(r.get("Div Yield")), "date": latest, "series_1m": series, "weekly_stats": weekly_stats(wk),
                        "source": {"name": "NSE Indices end-of-day file (official)", "url": index[latest]["index"]["url"],
                                   "retrieved_at": index[latest]["index"]["retrieved_at"], "sha256": index[latest]["index"].get("sha256")}})
    stocks = []
    for sym in uni["market"]["stocks"]:
        hist = price_history(sym, recent)
        if not hist:
            stocks.append({"symbol": sym, "state": "not_in_file"})
            continue
        last = hist[-1]
        prior = hist[-2]["close"] if len(hist) > 1 else None
        wk, split_events = adjust_splits(price_history(sym, weekly))
        hist, split_1m = adjust_splits(hist)
        last = hist[-1]
        prior = hist[-2]["close"] if len(hist) > 1 else None
        stocks.append({"symbol": sym, "state": "ok", "close": last["close_raw"], "date": last["date"], "split_events": split_events,
                       "change_pct": round((last["close"] / prior - 1) * 100, 2) if prior else None,
                       "deliv_pct": last["deliv_pct"], "series_1m": hist, "weekly": wk, "weekly_stats": weekly_stats(wk),
                       "source": {"name": "NSE equity bhavcopy (official), selected-symbol extract",
                                  "url": index[last["date"]]["bhav"]["url"], "retrieved_at": index[last["date"]]["bhav"]["retrieved_at"],
                                  "original_sha256": index[last["date"]]["bhav"].get("sha256")}})
    yahoo, y_fallbacks = _yahoo()
    if simulate_failure:
        y_fallbacks = y_fallbacks or [{"source": "yahoo", "state": "simulated"}]
    sensex = yahoo.get("bsesn-1y")
    sensex_block = {"name": "S&P BSE Sensex", "state": "unavailable", "note": "no Sensex capture available"}
    if sensex and sensex["points"]:
        pts = sensex["points"]
        intraday = yahoo.get("bsesn-1d")
        sensex_block = {"name": "S&P BSE Sensex", "state": "ok", "close": sensex["last"], "market_time": sensex["market_time"],
                        "change_pct": round((sensex["last"] / pts[-2]["close"] - 1) * 100, 2) if len(pts) > 1 else None,
                        "series_1m": [{"date": p["t"][:10], "close": p["close"]} for p in pts[-23:]],
                        "intraday": intraday["points"] if intraday else [],
                        "source": {"name": "Yahoo Finance chart API (unofficial, delayed)", "url": sensex["url"],
                                   "retrieved_at": sensex["retrieved_at"], "sha256": sensex["sha256"], "run": sensex["run"]}}
    nifty_intraday = yahoo.get("nsei-1d")
    asof = dt.date.fromisoformat(latest)
    return {"state": "ok", "as_of": latest, "previous": prev, "trading_days_in_store": len(dates),
            "simulated_failure": simulate_failure, "indices": indices, "sensex": sensex_block, "stocks": stocks,
            "nifty_intraday": {"points": nifty_intraday["points"], "market_time": nifty_intraday["market_time"],
                               "source": {"name": "Yahoo Finance chart API (unofficial, delayed)", "url": nifty_intraday["url"],
                                          "retrieved_at": nifty_intraday["retrieved_at"]}} if nifty_intraday else None,
            "fallbacks": y_fallbacks,
            "freshness_note": f"End-of-day close for {asof.strftime('%d %b %Y')}; not a live quote."}
