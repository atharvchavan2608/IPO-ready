"""Source -> dashboard pipeline.

  python -m ipo_ready.pipeline                      # capture all sources online, then build
  python -m ipo_ready.pipeline --offline            # rebuild from retained captures only
  python -m ipo_ready.pipeline --offline --simulate-failure market,wwipl:igx-overview

Build output: site/data/builds/<build_id>/*.json, copied to site/data/current/ (what the pages read).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

from . import capture
from .catalog import build_catalog, build_listed_company, catalog_row
from .company import build_company
from .config import BUILDS, CURRENT, ROOT, load_universe
from .issuer import latest_issuer_docs
from .market import build_market
from .portfolio import build_portfolio
from .news import build_news
from .parse_wwipl import map_canonical, parse_financial
from .peers import build_peers
from .peer_context import build_updates, read_autoaxles_annual, read_cial_annual
from .pre_ipo import LEMON_REPORT, enrich_lemon_tree, enrich_pre_ipo
from .ratios import build_ratios
from .research_views import build_research
from .sources import latest_good_items, write_simulated_failure

PIPELINE_VERSION = "0.10.0"
V1_LAST_BUILD = "20261123T191506Z"
KEEP_BUILDS = 10


def provider_fields_for(cid: str) -> dict:
    items, _ = latest_good_items("wwipl")
    it = items.get(f"{cid}-financial")
    return map_canonical(parse_financial(Path(it["abs_path"]), cid)["observations"]) if it else {}


def _code_hash() -> str:
    h = hashlib.sha256()
    for p in sorted((ROOT / "ipo_ready").glob("*.py")) + [ROOT / "ipo_ready" / "universe.json"]:
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def _num(x):
    return None if x is None else float(x)


def summary_row(co: dict, news: dict) -> dict:
    p = co["periods"][-1] if co["periods"] else None
    m = co.get("ratios", {}).get("by_period", co["metrics"]).get(p, {}) if p else {}
    f = co["fields"]
    v = co["valuation"]
    analysis = co.get("analysis", {}).get(p, {})

    def source_cell(name):
        return analysis.get("facts", {}).get(name) or f[name]["by_period"].get(p, {})

    def fv(name):
        return _num(source_cell(name).get("value"))

    def mv(name):
        r = m.get(name) or {}
        return {"value": _num(r.get("value")), "state": r.get("state", "missing_input"),
                **({"basis": r["basis"]} if "basis" in r else {})}

    n = news.get(co["id"], {}).get("items", [])
    return {
        "id": co["id"], "name": co["name"], "short": co["short"], "hierarchy": co["hierarchy"], "model": co["model"],
        "latest_period": p, "basis": analysis.get("basis", co["basis"]), "layout": co["layout"],
        "price_inr": _num(co["quote"]["price_inr"]), "quote_as_of": co["quote"]["as_of"],
        "drhp_filed": "Yes" if co.get("ipo_stage") else co["profile"].get("drhp_filed"),
        "ipo_stage": co.get("ipo_stage"),
        "has_issuer_docs": bool(co["documents"]),
        "metrics": {
            "market_cap_cr": {"value": _num(v["market_cap"]["value"]), "state": v["market_cap"]["state"]},
            **{key: {"value": _num(v[key]["value"]), "state": v[key]["state"], "basis": v[key].get("eps_basis")}
               for key in ("pe", "pe_reported", "pe_proxy")},
            "pb": {"value": _num(v["pb"]["value"]), "state": v["pb"]["state"]},
            "ps": {"value": _num(v["ps"]["value"]), "state": v["ps"]["state"]},
            "revenue_cr": {"value": fv("revenue_ops"), "state": "ok" if fv("revenue_ops") is not None else "missing_input"},
            "pat_cr": {"value": fv("pat"), "state": "ok" if fv("pat") is not None else
                       source_cell("pat").get("state", "missing_input")},
            "revenue_growth_pct": mv("revenue_growth"), "pat_margin_pct": mv("pat_margin"), "roe_pct": mv("roe"),
            "roce_pct": mv("roce"), "current_ratio": mv("current_ratio"), "quick_ratio": mv("quick_ratio"),
        },
        "checks_flagged": [c["check"] for c in co["checks"] if c["result"] in ("fail", "conflict", "stale")],
        "news_latest": n[0] if n else None, "news_count": len(n),
    }


def discovery_for(co: dict, rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if r["id"] == co["id"]:
            continue
        reasons, score = [], 0
        if r["hierarchy"][:3] == co["hierarchy"][:3]:
            reasons.append(f"same business: {r['hierarchy'][2]}")
            score += 3
        elif r["hierarchy"][:2] == co["hierarchy"][:2]:
            reasons.append(f"same industry: {r['hierarchy'][1]}")
            score += 1
        if (r.get("drhp_filed") or "").lower() == "yes":
            reasons.append("provider reports DRHP filed (IPO research lead)")
            score += 2
        if r.get("news_latest") and (r["news_latest"].get("date") or "") >= "2026-10-01":
            reasons.append(f"in the news {r['news_latest']['date']}")
            score += 1
        if reasons:
            out.append({"id": r["id"], "short": r["short"], "name": r["name"], "reasons": reasons, "score": score,
                        "price_inr": r["price_inr"], "latest_period": r["latest_period"]})
    return sorted(out, key=lambda x: (-x["score"], x["short"]))[:6]


def build(simulate: set[str], offline: bool) -> Path:
    t0 = time.perf_counter()
    uni = load_universe()
    build_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = BUILDS / build_id
    (out / "company").mkdir(parents=True, exist_ok=True)

    wwipl, wwipl_fb = latest_good_items("wwipl")
    docs = latest_issuer_docs()
    news = build_news()
    market = build_market(simulate_failure="market" in simulate)
    screener, screener_fb = latest_good_items("screener")
    context, context_fb = latest_good_items("peer_context")
    companies, rows = {}, []
    for c in uni["unlisted"]:
        co = build_company(c, wwipl.get(f"{c['id']}-financial"), wwipl.get(f"{c['id']}-overview"), docs)
        co["news"] = news["by_company"].get(c["id"], {"state": "unavailable", "items": []})
        companies[c["id"]] = co
    companies["cial"]["peer_annual"] = read_cial_annual(context.get("cial-annual-2026"))
    autoaxles = read_autoaxles_annual(context.get("autoaxles-annual-2026"))
    peers = build_peers(companies, screener, market, screener_fb, build_id, uni["default_company"],
                        uni["demo_domains"], build_updates(context, docs),
                        {"AUTOAXLES-standalone": autoaxles} if autoaxles else {})
    for co in companies.values():
        co["peer_reviewed"] = co["id"] in peers["cohorts"]
        enrich_pre_ipo(co, docs)
        co["ratios"] = build_ratios(co)
        rows.append(summary_row(co, news["by_company"]))
    reference_ids = {company["id"] for company in uni["unlisted"] if company.get("screen_exclusion")}
    discovery_rows = [row for row in rows if row["id"] not in reference_ids]
    terms, terms_fb = latest_good_items("portfolio_terms")
    portfolio = build_portfolio(market, [companies[row["id"]] for row in discovery_rows],
                                uni["default_company"], terms, terms_fb, build_id)
    listed, catalog = build_catalog(companies, screener, market)
    if lemon_report := docs.get(LEMON_REPORT):
        lemon_tree = build_listed_company("LEMONTREE", None, None, identity={
            "id": "nse-lemontree", "name": "Lemon Tree Hotels Limited", "isin": "INE970X01018",
            "evidence": {"source": "Lemon Tree Hotels Annual Report filed with NSE",
                         "url": lemon_report["url"], "sha256": lemon_report["sha256"],
                         "retrieved_at": lemon_report["retrieved_at"], "file": lemon_report["path"],
                         "raw_label": "NSE-listed issuer annual report", "raw_text": "Lemon Tree Hotels Limited"},
        }, classification=("Travel & Hospitality", "hotel_operator"))
        enrich_lemon_tree(lemon_tree, lemon_report)
        listed[lemon_tree["id"]] = lemon_tree
        catalog.append(catalog_row(lemon_tree))
    for co in listed.values():
        co["ratios"] = build_ratios(co)
    for co in [*companies.values(), *listed.values()]:
        co["research"] = build_research(co)
    for co in companies.values():
        co["discovery"] = discovery_for(co, discovery_rows)
        co["fallbacks"] = [f for f in wwipl_fb if f["item"].startswith(co["id"] + "-")]
        (out / "company" / f"{co['id']}.json").write_text(json.dumps(co, indent=1, ensure_ascii=False), encoding="utf-8")
    for co in listed.values():
        (out / "company" / f"{co['id']}.json").write_text(json.dumps(co, indent=1, ensure_ascii=False), encoding="utf-8")
    screen_rows = [*rows, *(summary_row(co, {}) for co in listed.values())]
    listing_by_id = {row["id"]: row["identity"]["listing"] for row in catalog}
    screen_rows = [row | {"listing": listing_by_id[row["id"]]} for row in screen_rows]
    (out / "catalog.json").write_text(json.dumps({"build_id": build_id, "companies": catalog, "screen_rows": screen_rows},
                                                indent=1, ensure_ascii=False), encoding="utf-8")

    (out / "companies.json").write_text(json.dumps({"default": uni["default_company"], "catalog_available": True, "build_id": build_id,
                                                   "companies": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "market.json").write_text(json.dumps(market, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "news.json").write_text(json.dumps({"market": news["by_company"].get("_market"), "fallbacks": news["fallbacks"]}, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "peers.json").write_text(json.dumps(peers, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "portfolio.json").write_text(json.dumps(portfolio, indent=1, ensure_ascii=False, allow_nan=False), encoding="utf-8")

    inputs = {}
    for src in ("wwipl", "news", "yahoo", "peer_context", "portfolio_terms"):
        items, _ = latest_good_items(src)
        inputs[src] = {k: {"run": v["run"], "sha256": v["sha256"], "retrieved_at": v["retrieved_at"]} for k, v in items.items()}
    inputs["issuer"] = {k: {"run": v["capture_run"], "sha256": v["sha256"],
                             **{key: v[key] for key in ("original_sha256", "original_pages") if key in v}}
                        for k, v in docs.items()}
    inputs["screener"] = {k: {"run": screener[k]["run"], "sha256": screener[k]["sha256"], "retrieved_at": screener[k]["retrieved_at"]}
                          for k in peers["capture_audit"]}
    inputs["nse_eod"] = {"latest_date": market.get("as_of"), "trading_days": market.get("trading_days_in_store")}
    inputs["listed_identity"] = {
        co["id"]: {key: item.get(key) for key in ("url", "sha256", "retrieved_at", "file")}
        for co in listed.values() if (item := co["evidence"].get(co["identity"]["ev"]))
    }
    all_checks = [dict(company=co["id"], **ch) for co in companies.values() for ch in co["checks"]]
    manifest = {
        "build_id": build_id, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": "offline" if offline else "online", "simulated_failures": sorted(simulate),
        "pipeline_version": PIPELINE_VERSION, "code_hash": _code_hash(), "python": sys.version.split()[0],
        "inputs": inputs,
        "fallbacks": wwipl_fb + news["fallbacks"] + market.get("fallbacks", []) + peers["fallbacks"] + context_fb + terms_fb,
        "checks_summary": {r: sum(1 for ch in all_checks if ch["result"] == r) for r in ("pass", "fail", "conflict", "stale")},
        "checks": all_checks,
        "companies": len(companies), "duration_s": round(time.perf_counter() - t0, 2),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    if CURRENT.exists():
        shutil.rmtree(CURRENT)
    shutil.copytree(out, CURRENT)
    for old_build in sorted(p for p in BUILDS.iterdir() if p.is_dir() and p.name > V1_LAST_BUILD)[:-KEEP_BUILDS]:
        shutil.rmtree(old_build, ignore_errors=True)
    return out


def main(argv: list[str] | None = None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip capture; build from retained captures")
    ap.add_argument("--sources", default=",".join(capture.CAPTURERS))
    ap.add_argument("--simulate-failure", default="", help="comma list: market | yahoo | news | wwipl:<item-id> | screener:<item-id> | portfolio_terms:<item-id>")
    args = ap.parse_args(argv)
    simulate = {s for s in args.simulate_failure.split(",") if s}
    drill_dirs: list[Path] = []
    if not args.offline:
        rid = capture.run_id()
        for s in args.sources.split(","):
            print(f"[capture] {s}")
            capture.CAPTURERS[s](rid)
    for s in simulate:
        if s in ("market", "yahoo"):
            items, _ = latest_good_items("yahoo")
            drill_dirs.append(write_simulated_failure("yahoo", list(items)).parent)
            print("[simulate] yahoo run failed:", drill_dirs[-1].name)
        elif s == "news":
            items, _ = latest_good_items("news")
            drill_dirs.append(write_simulated_failure("news", list(items)).parent)
            print("[simulate] news run failed:", drill_dirs[-1].name)
        elif s.startswith(("wwipl:", "screener:", "portfolio_terms:")):
            source, item_id = s.split(":", 1)
            drill_dirs.append(write_simulated_failure(source, [item_id]).parent)
            print(f"[simulate] {source} item failed:", drill_dirs[-1].name)
    try:
        out = build(simulate, args.offline)
    finally:
        for d in drill_dirs:  # simulated failures must not affect later builds
            shutil.rmtree(d, ignore_errors=True)
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    print(f"[build] {man['build_id']} mode={man['mode']} companies={man['companies']} checks={man['checks_summary']} "
          f"fallbacks={len(man['fallbacks'])} duration={man['duration_s']}s")
    print(f"[deliver] {out.relative_to(ROOT)} -> {CURRENT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
