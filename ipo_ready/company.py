"""Build one company read model: normalised fields, checks, reconciliation, agent verdicts, metrics."""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from . import agent, metrics as M
from .cash_flow import build_cash_flow
from .issuer import igx_inventory_note, igx_market_activity, igx_operating_scope, read_selected_lines
from .parse_wwipl import map_canonical, parse_financial, parse_overview, parse_number

D = Decimal
FIELD_LABELS = {
    "total_income": "Total income", "revenue_ops": "Revenue from operations", "other_income": "Other income",
    "other_gains": "Other gains / losses", "job_work_revenue": "Revenue from job work",
    "total_expenses": "Total expenses", "finance_cost": "Finance cost", "depreciation": "Depreciation", "pbt": "Profit before tax",
    "tax": "Tax", "pat": "Profit after tax", "total_assets": "Total assets", "total_equity": "Total equity",
    "total_liabilities": "Total liabilities", "current_assets": "Current assets", "current_liabilities": "Current liabilities",
    "inventories": "Inventories", "cash": "Cash & equivalents", "loans": "Loans", "cfo": "Cash from operations",
    "cfi": "Cash from investing", "cff": "Cash from financing", "ebitda": "EBITDA", "eps": "EPS (provider)",
    "shares_outstanding": "Shares outstanding", "pat_pre_associate": "Profit after tax before associate contribution",
    "pat_owners": "Profit attributable to owners", "associate_profit": "Share of associate profit",
    "eps_basic": "Reported basic EPS", "eps_diluted": "Reported diluted EPS",
    "gross_profit": "Gross profit", "operating_profit": "Operating profit", "cost_of_sales": "Cost of sales",
    "trade_receivables": "Trade receivables", "trade_payables": "Trade payables",
    "fixed_assets": "Fixed assets", "borrowings": "Borrowings", "dividend_per_share": "Dividend per share",
    "gross_npa": "Gross NPA", "net_npa": "Net NPA", "nim": "Net interest margin",
    "provision_coverage": "Provision coverage", "capital_adequacy": "Capital adequacy",
    "claims_ratio": "Incurred claims ratio", "combined_ratio": "Combined ratio", "solvency_ratio": "Solvency ratio",
}
NO_CURRENT_SPLIT = {"lender", "insurer"}


def _igx_quick_ratios(doc: dict, recon: dict, evidence) -> dict:
    pdf = Path(doc["abs_path"])
    note = igx_inventory_note(pdf)
    bs = recon["selected"]["statements"]["balance_sheet"]
    lines = bs["lines"]
    if not (note and recon.get("operating_scope") and bs["title_confirmed"]
            and bs["unit_text"] == "Indian Rupees millions" and lines["inventories"]["state"] == "no_line_item"):
        return {}
    raw_source = {"source": "IGX Restated Financial Information", "retrieved_at": doc["retrieved_at"],
                  "source_date": "2026-07-14", "sha256": doc["sha256"], "file": pdf.name,
                  "capture_run": doc["capture_run"], "basis": "issuer_and_esos_trust"}
    by_period = {}
    for period in bs["periods"]:
        metrics = [lines[k] for k in ("current_assets", "current_liabilities")]
        amounts = [line.get("values_inr_crore", {}).get(period) for line in metrics]
        if None in amounts or any(line["raw_values"][period] == "-" for line in metrics):
            continue
        period_source = {**raw_source, "period": period, "period_label": f"31 March {period[2:]}"}
        ids = [evidence.add({**period_source, "url": f'{doc["url"]}#page=5', "page": 5,
                             "raw_label": label, "raw_text": line["raw_values"][period], "raw_unit": "INR million"})
               for label, line in zip(("Total current assets", "Total current liabilities"), metrics)]
        ids.append(evidence.add({**raw_source, "url": f'{doc["url"]}#page=54', "page": 54,
                                 "raw_label": "Analytical ratios · Inventory turnover", "raw_text": note}))
        by_period[period] = {**M.quick_ratio(amounts[0], None, "inapplicable", amounts[1]),
                             "ev": ids, "inventory_state": "assumed_nil", "basis": "issuer_and_esos_trust"}
    return by_period


def _fy_sort(p: str) -> tuple:
    m = re.match(r"FY(\d{4})", p)
    return (int(m.group(1)) if m else 0, p)


def _major_section(section: str) -> str | None:
    for part in reversed(section.split(" > ")):
        p = part.lower().strip(" :")
        if re.search(r"non[- ]?current", p):
            return "noncurrent"
        if re.search(r"\bcurrent\b", p):
            return "current_" + ("assets" if "asset" in p else "liabilities")
        if p == "equity":
            return "equity"
    return None


def derive_section_totals(observations: list[dict], canonical: dict) -> dict:
    """Detailed-layout pages list current items without a total. Sum them, labelled as derived."""
    derived: dict[str, dict] = {}
    groups = {"current_assets": "current_assets", "current_liabilities": "current_liabilities", "total_equity": "equity"}
    for field, major in groups.items():
        if field in canonical:
            continue
        sums: dict[str, list] = {}
        for o in observations:
            if o["statement"] != "balance_sheet" or o["unit"] != "INR crore" or o["value"] is None:
                continue
            if _major_section(o.get("section", "")) == major and not re.search(r"non[- ]?controlling|^total", o["raw_label"], re.I):
                sums.setdefault(o["period"], []).append(o)
        for period, obs in sums.items():
            total = sum(D(o["value"]) for o in obs)
            derived.setdefault(field, {})[period] = {
                "value": format(total, "f"), "state": "derived", "raw_label": f"Sum of {len(obs)} lines under '{major.replace('_', ' ')}'",
                "basis": obs[0]["basis"], "period": period, "unit": "INR crore", "raw_unit": obs[0]["raw_unit"],
                "components": [{"label": o["raw_label"], "value": o["value"]} for o in obs], "anchor": obs[0]["anchor"],
                "statement": "balance_sheet", "derived": True}
    return derived


class Evidence:
    """Collects evidence records; figures refer to them by id."""

    def __init__(self):
        self.items: dict[str, dict] = {}

    def add(self, rec: dict) -> str:
        eid = f"ev{len(self.items) + 1}"
        self.items[eid] = rec
        return eid


def build_company(c: dict, fin_item: dict | None, ov_item: dict | None, docs: dict) -> dict:
    ev = Evidence()
    out: dict = {"id": c["id"], "name": c["name"], "short": c["short"], "hierarchy": c["hierarchy"], "model": c["model"],
                 "listed_peers": c["listed_peers"], "status_note": c.get("status_note"), "market_status": c.get("market_status")}
    coverage_gaps: list[dict] = []
    checks: list[dict] = []

    # ---- overview (quote, identity) ----
    ov = parse_overview(Path(ov_item["abs_path"])) if ov_item else {}
    ov_src = None
    if ov_item:
        ov_src = {"source": "WWIPL company overview", "url": ov_item["url"], "retrieved_at": ov_item["retrieved_at"],
                  "sha256": ov_item["sha256"], "capture_run": ov_item["run"], "file": Path(ov_item["abs_path"]).name}
    price, pstate, _ = parse_number(ov.get("price_raw", ""))
    out["quote"] = {"price_inr": None if price is None else format(price, "f"), "state": pstate if ov_item else "unavailable",
                    "change_raw": ov.get("price_change_raw"), "kind": "unlisted dealer quote (indicative, not an exchange trade)",
                    "as_of": ov_item["retrieved_at"] if ov_item else None,
                    "high_52w": ov.get("high_52w"), "low_52w": ov.get("low_52w"),
                    "ev": ev.add({**ov_src, "raw_label": "Last Traded Price", "raw_text": ov.get("price_raw")}) if ov_src else None}
    out["profile"] = {k: ov.get(k) for k in ("provider_sector", "isin", "cin", "registration_date", "face_value", "lot_size",
                                              "drhp_filed", "depository", "rofr", "description", "share_details_as_of")}
    out["profile"]["ev"] = ev.add({**ov_src, "raw_label": "Company fundamentals block"}) if ov_src else None

    # ---- statements ----
    fin_src = None
    canonical, observations, tables = {}, [], []
    if fin_item:
        parsed = parse_financial(Path(fin_item["abs_path"]), c["id"])
        observations, tables = parsed["observations"], parsed["tables"]
        canonical = map_canonical(observations)
        canonical.update(derive_section_totals(observations, canonical))
        fin_src = {"source": "WWIPL financial statements page", "url": fin_item["url"], "retrieved_at": fin_item["retrieved_at"],
                   "sha256": fin_item["sha256"], "capture_run": fin_item["run"], "file": Path(fin_item["abs_path"]).name}
    else:
        coverage_gaps.append({"field": "statements", "state": "unavailable", "note": "no successful capture of the provider financial page"})

    periods = sorted({o["period"] for o in observations if o["period"].startswith("FY") and not o["period"].endswith("?")} |
                     {o["period"] for o in observations if o["period"].endswith("?")}, key=_fy_sort)
    bases = sorted({t["basis"] for t in tables if t["statement"] != "ratios"})
    out["periods"] = periods
    out["basis"] = bases[0] if len(bases) == 1 else ("mixed: " + ", ".join(bases) if bases else "unknown")
    out["raw_units"] = sorted({t["raw_unit"] for t in tables if t.get("raw_unit")})
    out["layout"] = "five-year summary" if len(periods) >= 4 else "detailed statements"

    fields: dict[str, dict] = {}
    for f, label in FIELD_LABELS.items():
        per = canonical.get(f, {})
        row = {}
        for p in periods:
            o = per.get(p)
            if o is None:
                row[p] = {"value": None, "state": "not_in_source"}
                continue
            eid = ev.add({**(fin_src or {}), "raw_label": o["raw_label"], "raw_text": o.get("raw_text"), "raw_unit": o.get("raw_unit"),
                          "period": p, "period_label": o.get("period_label"), "basis": o.get("basis"), "anchor": o["anchor"],
                          "statement": o["statement"], "derived": o.get("derived", False), "components": o.get("components")})
            row[p] = {"value": o["value"], "state": o["state"], "ev": eid}
        units = {o["unit"] for o in per.values()}
        fields[f] = {"label": label, "unit": next(iter(units)) if len(units) == 1 else "INR crore", "by_period": row}
    out["fields"] = fields
    out["cash_flow"] = build_cash_flow(out, docs.get("igx-restated-financials") if c["id"] == "igx" else None, ev)

    def val(f, p):
        cell = fields.get(f, {}).get("by_period", {}).get(p)
        return None if not cell or cell["value"] is None else D(cell["value"])

    def evs(*pairs):
        return [fields[f]["by_period"][p]["ev"] for f, p in pairs if fields.get(f, {}).get("by_period", {}).get(p, {}).get("ev")]

    # ---- checks ----
    for p in periods:
        ta, te, tl = val("total_assets", p), val("total_equity", p), val("total_liabilities", p)
        if None not in (ta, te, tl):
            # Exchanges show the Core Settlement Guarantee Fund as its own block between equity and liabilities.
            csgf = next((D(o["value"]) for o in observations if o["statement"] == "balance_sheet" and o["period"] == p
                         and o["value"] is not None and re.search(r"settlement guarantee fund", o["raw_label"], re.I)), D(0))
            diff = ta - (te + tl + csgf)
            extra = f" + core SGF {csgf}" if csgf else ""
            tol = max(D("0.05"), abs(ta) * D("0.00001"))  # 2-dp rounding across many lines on large totals
            checks.append({"check": "balance_identity", "period": p, "result": "pass" if abs(diff) <= tol else "fail",
                           "detail": f"assets {ta} - (equity {te}{extra} + liabilities {tl}) = {diff}"})
        ti, ro, oi = val("total_income", p), val("revenue_ops", p), val("other_income", p)
        if None not in (ti, ro, oi):
            extra_income = sum((val(field, p) or D(0) for field in ("other_gains", "job_work_revenue")), D(0))
            diff = ti - (ro + oi + extra_income)
            checks.append({"check": "income_identity", "period": p, "result": "pass" if abs(diff) <= D("0.05") else "fail",
                           "detail": f"total income {ti} - (operations {ro} + other {oi} + separate income lines {extra_income}) = {diff}"})
        if fields["pat"]["by_period"][p]["state"] == "conflict":
            checks.append({"check": "profit_row_conflict", "period": p, "result": "conflict",
                           "detail": "Repeated profit labels have different values in the same annual table. Inspect both source rows."})
    share_vals = {}
    for k in ("shares_fundamentals", "shares_details"):
        v, s, _ = parse_number(ov.get(k, "") or "")
        if v is not None:
            share_vals[k] = v
    if periods and val("shares_outstanding", periods[-1]) is not None:
        share_vals["summary_latest_fy"] = val("shares_outstanding", periods[-1])
    if len(set(share_vals.values())) > 1:
        lo, hi = min(share_vals.values()), max(share_vals.values())
        checks.append({"check": "shares_outstanding_consistency", "result": "conflict" if (hi - lo) / hi > D("0.005") else "pass",
                       "detail": {k: format(v, "f") for k, v in share_vals.items()}})
    if periods and not re.match(r"FY202[56]", periods[-1]):
        checks.append({"check": "freshness", "result": "stale", "detail": f"latest period {periods[-1]} is older than FY2025"})

    # Shares for valuation: the dated 'share details' block first, then the summary table, then the
    # fundamentals block (on IGX the fundamentals figure equals authorised capital / face value).
    # A candidate more than 100x away from another is a unit mismatch (e.g. NSE summary in crore shares).
    shares, shares_src = None, None
    for k in ("shares_details", "summary_latest_fy", "shares_fundamentals"):
        if k in share_vals:
            others = [v for kk, v in share_vals.items() if kk != k and v > 0]
            if others and share_vals[k] > 0 and max(max(others) / share_vals[k], share_vals[k] / max(others)) > 100:
                checks.append({"check": "shares_unit_mismatch", "result": "conflict",
                               "detail": f"{k}={format(share_vals[k], 'f')} differs >100x from other share counts; not used"})
                continue
            shares, shares_src = share_vals[k], k
            break

    # ---- issuer reconciliation ----
    company_docs = {k: v for k, v in docs.items() if v.get("company") == c["id"]}
    out["documents"] = [{"id": k, "title": v.get("title"), "url": v["url"], "retrieved_at": v["retrieved_at"], "sha256": v["sha256"],
                         "bytes": v.get("bytes"), "referrer": v.get("referrer")} for k, v in company_docs.items()]
    recon = None
    igx_quick = {}
    restated = next((v for k, v in company_docs.items() if "restated" in k), None)
    if restated:
        sel = read_selected_lines(Path(restated["abs_path"]))
        rows = []
        for stmt, s in sel["statements"].items():
            for f, line in s["lines"].items():
                if line["state"] != "reported":
                    rows.append({"field": f, "statement": stmt, "page": s["page"], "state": line["state"]})
                    continue
                for p, iv in line["values_inr_crore"].items():
                    pv = val(f, p) if f in fields else None
                    diff = None if pv is None else D(iv) - pv
                    tol = D("0.006") if f != "eps" else D("0.006")
                    rows.append({"field": f, "label": FIELD_LABELS.get(f, f.replace("_", " ")), "statement": stmt, "page": s["page"],
                                 "period": p, "issuer_value": iv, "provider_value": None if pv is None else format(pv, "f"),
                                 "difference": None if diff is None else format(diff, "f"),
                                 "result": "issuer_only" if pv is None else ("match" if abs(diff) <= tol else "differs"),
                                 "matched_text": line["matched_text"]})
        compared = [r for r in rows if r.get("result") in ("match", "differs")]
        recon = {"document": restated["id"], "url": restated["url"], "sha256": restated["sha256"],
                 "retrieved_at": restated["retrieved_at"], "capture_run": restated["capture_run"], "file": Path(restated["abs_path"]).name,
                 "unit_note": "issuer reports INR million; converted to INR crore (/10). Provider reports INR crore to 2 dp, so a tolerance of 0.006 crore is used.",
                 "rows": rows, "summary": {"compared": len(compared), "match": sum(r["result"] == "match" for r in compared),
                                           "differs": sum(r["result"] == "differs" for r in compared)},
                 "selected": sel}
        if restated["id"] == "igx-restated-financials":
            recon["operating_scope"] = igx_operating_scope(Path(restated["abs_path"]))
            igx_quick = _igx_quick_ratios(restated, recon, ev)
        # issuer shares: equity share capital / face value is in the DRHP; use EPS cross-check only
        if (ov.get("drhp_filed") or "").strip().lower() == "no" and any("drhp" in k for k in company_docs):
            checks.append({"check": "ipo_status", "result": "conflict",
                           "detail": "provider shows 'DRHP Filed? No' but the issuer's investor-relations page links a Draft Red Herring Prospectus"})
    out["reconciliation"] = recon
    if "igx-drhp" in company_docs:
        out["market_activity"] = igx_market_activity(company_docs["igx-drhp"], ev)

    # ---- agent ----
    agent_out = {f: agent.run(c, canonical, f, docs) for f in agent.FIELDS}
    out["agent"] = agent_out

    # ---- metrics per period ----
    inv_status = agent_out["inventories"]["status"]
    rows = {}
    for i, p in enumerate(periods):
        prev = periods[i - 1] if i > 0 else None
        r = {}
        r["revenue_growth"] = {**M.growth(val("revenue_ops", p), val("revenue_ops", prev) if prev else None), "ev": evs(("revenue_ops", p), ("revenue_ops", prev)) if prev else evs(("revenue_ops", p))}
        r["pat_margin"] = {**M.ratio(val("pat", p), val("total_income", p), "PAT / total income x 100", ("pat", "total_income"), "%", True), "ev": evs(("pat", p), ("total_income", p))}
        r["net_profit_ratio"] = {**M.ratio(val("pat", p), val("revenue_ops", p), "PAT / revenue from operations x 100", ("pat", "revenue_ops"), "%", True), "ev": evs(("pat", p), ("revenue_ops", p))}
        r["other_income_share"] = {**M.ratio(val("other_income", p), val("total_income", p), "other income / total income x 100", ("other_income", "total_income"), "%", True), "ev": evs(("other_income", p), ("total_income", p))}
        if c["model"] in NO_CURRENT_SPLIT:
            na = M.result(None, M.INAPPLICABLE, "current assets / current liabilities", {},
                          "lenders and insurers present the balance sheet by liquidity without a current / non-current split", "x")
            r["current_ratio"], r["quick_ratio"] = {**na, "ev": []}, {**na, "ev": []}
        else:
            r["current_ratio"] = {**M.ratio(val("current_assets", p), val("current_liabilities", p), "current assets / current liabilities", ("current_assets", "current_liabilities")), "ev": evs(("current_assets", p), ("current_liabilities", p))}
            inv_cell = fields["inventories"]["by_period"].get(p, {})
            inv_state = "reported" if inv_cell.get("state") in ("reported", "explicit_zero") else ("inapplicable" if inv_status == "inapplicable" else "missing")
            r["quick_ratio"] = {**M.quick_ratio(val("current_assets", p), inv_cell.get("value"), inv_state, val("current_liabilities", p)),
                                "ev": evs(("current_assets", p), ("current_liabilities", p), ("inventories", p))}
            if c["id"] == "igx":
                if p in igx_quick:
                    r["quick_ratio"] = igx_quick[p]
                elif inv_state != "reported":
                    r["quick_ratio"] = {**M.quick_ratio(val("current_assets", p), None, "missing", val("current_liabilities", p)),
                                        "ev": r["quick_ratio"]["ev"], "note": "Period-specific inventory evidence is unavailable."}
        avg_eq = M.average(val("total_equity", p), val("total_equity", prev)) if prev else None
        r["roe"] = {**M.ratio(val("pat", p), avg_eq, "PAT / average of opening and closing equity x 100", ("pat", "average_equity"), "%", True), "ev": evs(("pat", p), ("total_equity", p)) + (evs(("total_equity", prev)) if prev else [])}
        ebit = None if val("pbt", p) is None or val("finance_cost", p) is None else val("pbt", p) + val("finance_cost", p)
        ce = None if val("total_assets", p) is None or val("current_liabilities", p) is None else val("total_assets", p) - val("current_liabilities", p)
        r["roce"] = {**M.ratio(ebit, ce, "(PBT + finance cost) / (total assets - current liabilities) x 100", ("ebit", "capital_employed"), "%", True), "ev": evs(("pbt", p), ("finance_cost", p), ("total_assets", p), ("current_liabilities", p))}
        r["cfo_to_pat"] = {**M.ratio(val("cfo", p), val("pat", p), "cash from operations / PAT", ("cfo", "pat")), "ev": evs(("cfo", p), ("pat", p))}
        if r["cfo_to_pat"]["state"] == "ok" and c["model"] in ("exchange", "broker"):
            r["cfo_to_pat"]["note"] = "exchange/broker CFO includes member settlement and margin flows; swings are not earnings quality by themselves"
        rows[p] = r
    out["metrics"] = rows

    # ---- valuation at the quote ----
    latest = periods[-1] if periods else None
    pat_l = val("pat", latest) if latest else None
    eps_r = M.eps_from(pat_l, shares)
    basic = val("eps_basic", latest) if latest else None
    dil = val("eps_diluted", latest) if latest else None
    basic_evidence = evs(("eps_basic", latest))
    valuation_basis = out["basis"]
    if recon and recon.get("operating_scope"):
        income = recon["selected"]["statements"]["income_statement"]
        if income["title_confirmed"]:
            restated_eps = income["lines"]["eps"]
            raw_eps = restated_eps.get("raw_values", {}).get(latest)
            if raw_eps and raw_eps != "-":
                basic = D(restated_eps["values_inr_crore"][latest])
                valuation_basis = recon["operating_scope"]["basis"]
                basic_evidence = [ev.add({"source": "IGX Restated Financial Information", "url": f'{recon["url"]}#page=6',
                                          "page": 6, "retrieved_at": recon["retrieved_at"], "source_date": "2026-07-14",
                                          "sha256": recon["sha256"], "raw_label": "Basic EPS", "raw_text": raw_eps,
                                          "raw_unit": "INR per share", "basis": valuation_basis, "period": latest,
                                          "period_label": f"31 March {latest[2:]}"})]
                restated_dil = income["lines"]["eps_diluted"]
                if restated_dil.get("raw_values", {}).get(latest) not in (None, "-"):
                    dil = D(restated_dil["values_inr_crore"][latest])
    reported_pe = {**M.pe(price, basic), "eps_basis": "reported_basic", "basis": valuation_basis, "ev": basic_evidence}
    proxy_eps = pat_l * D(10_000_000) / shares if eps_r["value"] is not None else None
    proxy_pe = {**M.pe(price, proxy_eps), "eps_basis": "pat_share_proxy", "basis": out["basis"], "ev": evs(("pat", latest))}
    selected_pe = reported_pe if basic is not None else proxy_pe
    pe_note = ("Uses reported annual basic EPS." if basic is not None
               else "Uses a calculated proxy of annual PAT divided by shares outstanding.")
    for multiple in (reported_pe, proxy_pe):
        if out["quote"]["ev"]:
            multiple["ev"].append(out["quote"]["ev"])
    eq_l = val("total_equity", latest) if latest else None
    out["valuation"] = {
        "period": latest, "shares_used": None if shares is None else format(shares, "f"), "shares_source": shares_src,
        "market_cap": M.market_cap_cr(price, shares),
        "eps": eps_r,
        "eps_reported_basic": None if basic is None else format(basic, "f"),
        "eps_reported_diluted": None if dil is None else format(dil, "f"),
        "pe": {**selected_pe, "note": f'{pe_note} {selected_pe.get("note", "")}'.strip()},
        "pe_reported": reported_pe,
        "pe_proxy": proxy_pe,
        "pb": M.ratio(None if price is None or shares is None else price * shares / D(10_000_000), eq_l, "market cap / total equity", ("market_cap", "total_equity")),
        "ps": M.ratio(None if price is None or shares is None else price * shares / D(10_000_000), val("revenue_ops", latest) if latest else None, "market cap / operating revenue", ("market_cap", "operating_revenue")),
        "provider": {"pe": ov.get("pe_provider"), "mcap": ov.get("mcap_provider"), "eps": ov.get("eps_ttm")},
        "note": "Valued at an indicative unlisted dealer quote against the latest fiscal-year PAT; not a traded market price.",
    }
    # Quote sanity: a sub-rupee quote or P/E below 1 indicates a placeholder or stale price, not a valuation.
    pe_v = out["valuation"]["pe"]["value"]
    if price is not None and (price < D("1") or (pe_v is not None and D(pe_v) < 1)):
        checks.append({"check": "quote_sanity", "result": "conflict",
                       "detail": f"quote INR {price} gives P/E {pe_v}; treated as unreliable, valuation withheld"})
        for k in ("market_cap", "pe", "pe_reported", "pe_proxy", "pb", "ps"):
            out["valuation"][k] = {**out["valuation"][k], "value": None, "state": "suspect_quote",
                                   "note": "provider quote failed the sanity check"}
    for f in ("inventories", "cash", "eps", "shares_outstanding", "current_assets"):
        if all(v["state"] == "not_in_source" for v in fields[f]["by_period"].values()):
            coverage_gaps.append({"field": f, "state": "not_in_source", "label": FIELD_LABELS[f]})
    out["coverage_gaps"] = coverage_gaps
    out["checks"] = checks
    out["provider_ratios"] = {o["raw_label"]: {} for o in observations if o["statement"] == "ratios"}
    for o in observations:
        if o["statement"] == "ratios":
            out["provider_ratios"][o["raw_label"]][o["period"]] = {"raw_text": o["raw_text"], "state": o["state"]}
    out["evidence"] = ev.items
    return out
