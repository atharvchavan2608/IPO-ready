"""Reviewed inputs for the two pre-IPO case studies and their benchmark context.

Raw figures are transcribed from the pinned source pages and kept in their original
units. The build publishes the same calculation and evidence IDs to both pages.
"""
from __future__ import annotations

from decimal import Decimal as D

from . import metrics as M
from .cash_flow import reviewed_cash_view
from .company import Evidence

CUTOFF = "2026-11-25"
OYO_REPORT = "oyo-annual-fy26"
LEMON_REPORT = "lemontree-fy26"
OYO_BRIDGE_NOTE = (
    "FX on cash is reported separately after the activity subtotal. FY2025 reported closing cash "
    "differs by ₹0.002 crore from the cash composition total on the same page."
)
OYO_FIELDS = {
    "revenue_ops": (164, "Revenue from operations", "93,579.84", "62,528.30"),
    "other_income": (164, "Other income", "3,399.43", "730.58"),
    "total_income": (164, "Total income", "96,979.27", "63,258.88"),
    "total_expenses": (164, "Total expenses", "93,344.96", "66,595.42"),
    "finance_cost": (164, "Finance cost", "14,142.47", "9,591.55"),
    "depreciation": (164, "Depreciation and amortization expense", "10,718.90", "4,835.87"),
    "pbt": (164, "Profit/(loss) before tax", "3,989.32", "(4,893.17)"),
    "tax": (164, "Income tax credit", "(5,952.51)", "(7,341.39)"),
    "pat": (164, "Profit for the year", "9,941.83", "2,448.22"),
    "pat_owners": (164, "Profit attributable to equity holders of the Parent", "9,933.73", "2,467.30"),
    "eps_basic": (164, "Basic earnings per share", "0.68", "0.18"),
    "eps_diluted": (164, "Diluted earnings per share", "0.63", "0.17"),
    "ebitda": (8, "EBITDA (Earnings before Interest, tax, depreciation and amortization)", "25,938.38", "10,834.99"),
    "total_assets": (163, "Total assets", "2,00,199.00", "1,66,953.22"),
    "current_assets": (163, "Current assets subtotal", "29,583.66", "21,262.96"),
    "current_liabilities": (163, "Current liabilities subtotal", "32,025.67", "25,870.09"),
    "total_liabilities": (163, "Total liabilities", "1,42,287.34", "1,29,087.00"),
    "total_equity": (163, "Total equity", "57,911.66", "37,866.22"),
    "cash": (163, "Cash and cash equivalents (balance sheet)", "10,070.75", "6,843.96"),
    "trade_receivables": (163, "Trade receivables", "6,638.80", "4,877.84"),
    "opening": (165, "Cash and cash equivalents at the beginning of the year", "6,857.21", "4,082.19"),
    "cfo": (165, "Net cash flows from operating activities (A)", "25,112.10", "3,212.51"),
    "cfi": (165, "Net cash flows (used in) investing activities (B)", "(13,749.19)", "(42,121.43)"),
    "cff": (165, "Net cash flows from / (used in) financing activities (C)", "(8,665.22)", "41,598.45"),
    "other_effects": (165, "Effect of exchange fluctuation on cash and cash equivalents", "520.43", "85.49"),
    "net_change": (165, "Net increase in cash and cash equivalents (A+B+C)", "2,697.69", "2,689.54"),
    "closing": (165, "Cash and cash equivalents at the end of the year", "10,075.33", "6,857.23"),
    "receivables": (165, "(Increase) in trade receivables", "(1,111.44)", "(1,561.11)"),
    "tax_paid": (165, "Taxes paid (net of refund)", "(339.01)", "(277.19)"),
    "debt_principal": (165, "Repayment of long term borrowings", "(2,275.56)", "(37,901.77)"),
    "lease_principal": (165, "Principal repayment of lease liabilities", "(5,700.66)", "(3,205.16)"),
    "lease_interest": (165, "Interest paid on lease liabilities", "(3,734.10)", "(1,288.95)"),
    "debt_interest": (165, "Interest paid on borrowings", "(9,819.68)", "(7,570.43)"),
    "ppe_capex": (165, "Purchase of property, plant and equipment and CWIP (net)", "(376.35)", "(561.36)"),
    "intangible_capex": (165, "Purchase of intangible assets", "(1,396.66)", "(972.33)"),
    "gbv": (9, "Gross Booking Value", "306,832.25", "162,787.75"),
    "g6_gbv": (9, "G6 GBV", "141,071.32", "35,290.75"),
    "hotel_gbv": (9, "GBV from Hotels (ex-G6)", "109,386.11", "80,127.28"),
    "deferred_tax": (164, "Deferred tax credit", "(6,776.44)", "(7,675.58)"),
}
LEMON_FIELDS = {
    "revenue_ops": (152, "Revenue from operations", "1,44,450.33", "1,28,607.77"),
    "ebitda": (152, "Profit before finance cost, finance income, depreciation and amortization and tax (EBITDA)", "69,933.01", "63,645.69"),
    "pat": (152, "Profit for the year", "28,831.82", "24,314.54"),
    "pbt": (152, "Profit before tax", "35,913.54", "29,622.64"),
    "total_assets": (152, "Total assets", "4,28,469.63", "4,08,178.66"),
    "total_equity": (152, "Total equity", "2,07,917.87", "1,78,960.14"),
    "cash": (152, "Cash and cash equivalents", "5,809.60", "5,542.32"),
    "cfo": (153, "Net cash flows generated from operating activities (A)", "54,161.30", "54,157.50"),
    "cfi": (153, "Net cash flow used in investing activities (B)", "(16,889.53)", "(12,744.97)"),
    "cff": (153, "Net cash flow used in financing activities (C)", "(37,004.49)", "(39,234.65)"),
    "net_change": (153, "Net increase in cash and cash equivalents (A+B+C)", "267.28", "2,177.88"),
    "opening": (153, "Cash and cash equivalents at the beginning of the year", "5,542.32", "3,364.44"),
    "closing": (153, "Cash and cash equivalents at the end of the year", "5,809.60", "5,542.32"),
}
DATES = {
    "igx-drhp": "2026-07-14", "igx-sebi-observation": "2026-10-13",
    "oyo-udrhp": "2026-06-29", "oyo-addendum": "2026-10-21",
    OYO_REPORT: "2026-07-31", LEMON_REPORT: "2026-08-26",
}


def _source(doc: dict, page: int, label: str, raw: str, unit: str, **extra) -> dict:
    return {
        "source": doc["title"], "source_id": doc["id"], "url": f'{doc["url"]}#page={page}',
        "source_date": DATES[doc["id"]], "retrieved_at": doc["retrieved_at"],
        "sha256": doc.get("original_sha256", doc["sha256"]), "file": doc["path"], "page": page,
        "raw_label": label, "raw_text": raw, "raw_unit": unit, **extra,
        **({"retained_sha256": doc["sha256"], "retained_page": doc["original_pages"].index(page) + 1}
           if "original_pages" in doc else {}),
    }


def _evidence(company: dict) -> Evidence:
    evidence = Evidence()
    evidence.items = company["evidence"]
    return evidence


def _reported(evidence: Evidence, doc: dict, raw_rows: dict, unit: str) -> dict:
    result = {}
    for i, period in enumerate(("FY2026", "FY2025"), 2):
        facts = {}
        for key, row in raw_rows.items():
            page, label, raw = row[0], row[1], row[i]
            is_eps = key.startswith("eps_")
            original_unit = "INR per share" if is_eps else unit
            value = D(raw.replace(",", "").replace("(", "-").replace(")", ""))
            if not is_eps:
                value /= 10 if unit == "INR million" else 100
            eid = evidence.add(_source(doc, page, label, raw, original_unit, basis="consolidated",
                                       period=period, period_label=f"31 March {period[2:]}",
                                       period_end=f"{period[2:]}-03-31"))
            facts[key] = {"value": str(value), "state": "explicit_zero" if not value else "reported", "ev": eid}
        result[period] = facts
    return result


def _publish_financials(company: dict, doc: dict, facts: dict, *, effects_after_net: bool, note: str) -> None:
    company["basis"] = "consolidated"
    company["periods"] = sorted(facts)
    company["statement_provider"] = doc["title"]
    company["layout"] = "audited annual statements"
    company["raw_units"] = ["INR million" if doc["id"] == OYO_REPORT else "INR lakh"]
    company["metrics"] = {period: {} for period in facts}
    for key, field in company["fields"].items():
        field["by_period"] = {period: rows.get(key, {"value": None, "state": "not_in_source"})
                              for period, rows in facts.items()}
    company["cash_flow"]["by_period"] = {
        period: reviewed_cash_view(rows, report=doc["title"], effects_after_net=effects_after_net, note=note)
        for period, rows in facts.items()
    }
    company["coverage_gaps"] = [
        {"field": key, "state": "not_in_source", "label": company["fields"][key]["label"]}
        for key in ("inventories", "shares_outstanding") if key in company["fields"]
    ]


def _stage(company: dict, evidence: Evidence, doc: dict, label: str, text: str) -> None:
    if company.get("ipo_stage") or not doc:
        return
    company["ipo_stage"] = {"state": "verified", "label": "Pre-IPO", "milestone": label,
                            "as_of": CUTOFF, "ev": evidence.add(_source(doc, 1, label, text, "document"))}


def _section(question: str, finding: str, change: str, *eids: str) -> dict:
    return {"question": question, "finding": finding, "review_trigger": change,
            "ev": list(dict.fromkeys(eid for eid in eids if eid))}


def _benchmark(company_id: str, label: str, scope: str, rationale: str) -> dict:
    return {"id": company_id, "label": label, "scope": scope, "rationale": rationale}


def _v(rows: dict, key: str) -> D:
    return D(rows[key]["value"])


def _format(value, digits=2) -> str:
    number = D(M.q(D(value), str(D(1).scaleb(-digits))))
    return f"{number:,.{digits}f}".replace("-", "−")


def _apply_quote_valuation(company: dict, shares: str, share_eid: str, eps: dict, diluted: dict,
                           basis: str, note: str, *, conditional: bool = False,
                           valuation_facts: dict | None = None) -> None:
    quote = company["quote"]
    price = quote["price_inr"]
    valuation = company["valuation"]
    pe = M.pe(price, eps["value"])
    cap = M.market_cap_cr(price, shares)
    if conditional:
        cap.update(state="conditional_share_count" if price is not None else M.MISSING)
    cap.update(ev=[eid for eid in (quote["ev"], share_eid) if eid], note=note)
    pe.update(eps_basis="reported_basic", basis=basis, ev=[eid for eid in (quote["ev"], eps["ev"]) if eid],
              note=note)
    eps_evidence = {"value": eps["value"], "state": M.OK, "ev": [eps["ev"]], "basis": basis,
                    "formula": "Reported annual basic EPS", "unit": "INR per share", "inputs": {}}
    valuation.update(shares_used=shares, shares_source="draft share capital",
                     eps=eps_evidence, eps_reported_basic=eps["value"], eps_reported_diluted=diluted["value"],
                     market_cap=cap, pe=pe, pe_reported=pe,
                     pe_proxy=M.result(None, M.MISSING, "price / PAT per ending share", {},
                                       "Reported EPS is available for the issuer."),
                     note=note)
    for key, fact, label in (("pb", "total_equity", "total equity"), ("ps", "revenue_ops", "operating revenue")):
        cell = (valuation_facts or {}).get(fact, {})
        valuation[key] = M.ratio(cap["value"], cell.get("value"), f"Indicative market cap / {label}")
        valuation[key].update(ev=[eid for eid in (*cap["ev"], cell.get("ev")) if eid], basis=basis, note=note)


def _build_igx(company: dict, docs: dict) -> None:
    draft = docs.get("igx-drhp")
    if not draft:
        return
    evidence = _evidence(company)
    observation = docs.get("igx-sebi-observation")
    if observation:
        _stage(company, evidence, observation, "SEBI observations received · 12 Oct 2026",
               "IEX reports receipt of SEBI's October 12 observation letter on the IGX draft.")
    else:
        _stage(company, evidence, draft, "Draft prospectus filed",
               "Draft Red Herring Prospectus dated July 14, 2026.")
    shares_ev = evidence.add(_source(draft, 86, "Paid-up share capital before the offer", "75,000,000", "shares"))
    offer_ev = evidence.add(_source(draft, 3, "Offer for sale", "16,710,000", "shares"))
    activity = company.get("market_activity", {})
    cash = company["cash_flow"]["by_period"].get("FY2026", {}).get("lines", {})
    cfo = cash.get("cfo", {})
    liabilities = cash.get("payables_and_liabilities", {})
    annual = company.get("reconciliation") or {}
    basic = annual.get("selected", {}).get("statements", {}).get("income_statement", {}).get("lines", {})
    basic_value = basic.get("eps", {}).get("raw_values", {}).get("FY2026")
    restated = docs.get("igx-restated-financials")
    reported_pe = company["valuation"]["pe_reported"]
    if restated and basic_value and reported_pe["basis"] == "issuer_and_esos_trust":
        eps_id = reported_pe["ev"][0]
        quote_note = ("WWIPL dealer indication and FY2026 reported basic EPS. The DRHP lists 75 million issued shares. "
                      "The draft offer consists of existing shares sold by IEX. The official offer price is pending.")
        valuation_facts = {}
        for field, page in (("total_equity", 5), ("revenue_ops", 6)):
            line = next((r for r in annual["rows"] if r["field"] == field and r.get("period") == "FY2026"), None)
            if line:
                valuation_facts[field] = {"value": line["issuer_value"], "ev": evidence.add({
                    "source": restated["title"], "url": f'{restated["url"]}#page={page}', "page": page,
                    "source_date": "2026-07-14", "retrieved_at": restated["retrieved_at"], "sha256": restated["sha256"],
                    "raw_label": line["label"], "raw_text": line["matched_text"], "raw_unit": "INR million",
                    "basis": "issuer_and_esos_trust", "period": "FY2026", "period_label": "31 March 2026",
                })}
        _apply_quote_valuation(company, "75000000", shares_ev, {"value": basic_value, "ev": eps_id},
                               {"value": company["valuation"]["eps_reported_diluted"]},
                               "issuer_and_esos_trust", quote_note, valuation_facts=valuation_facts)
    prior_cash_lines = company["cash_flow"]["by_period"].get("FY2025", {}).get("lines", {})
    cash25 = prior_cash_lines.get("cfo", {})
    prior_group = prior_cash_lines.get("payables_and_liabilities", {})
    settlement = cash.get("settlement_accounts", {})
    if not {"FY2025", "FY2026"} <= activity.keys() or any(
        cell.get("value") is None for cell in (cfo, liabilities, cash25, prior_group, settlement)
    ):
        return
    current, prior = activity["FY2026"], activity["FY2025"]
    volume_effect = (_v(current, "volume") - _v(prior, "volume")) * _v(prior, "fees") / _v(prior, "volume")
    fee_effect = _v(current, "fees") - _v(prior, "fees") - volume_effect
    rate = _v(current, "fees") / _v(current, "volume")
    cash_ex_line = D(cfo["value"]) - D(liabilities["value"])
    pe = company["valuation"]["pe"]["value"]
    cap = company["valuation"]["market_cap"]["value"]
    benchmarks = [
        _benchmark("nse-iex", "Indian Energy Exchange", "operating",
                   "Both run energy marketplaces. Use matched annual operating rows. IEX is IGX's promoter and accounts for IGX as an associate in consolidated results."),
        _benchmark("nse-mcx", "MCX", "context",
                   "An exchange operating model offers context. Derivatives, clearing and trade units differ from physically delivered gas."),
    ]
    company["issuer_case"] = {"period": "FY2026", "basis": "Restated issuer and employee share trust", "benchmarks": benchmarks,
        "metrics": {"fee_volume_effect_inr_million": str(volume_effect), "fee_rate_mix_effect_inr_million": str(fee_effect),
                    "cfo_less_grouped_liabilities_cr": str(cash_ex_line), "indicated_pe": pe, "indicative_equity_cr": cap},
        "sections": [
            _section("What drives growth?",
                     f"Gas volume rose from {_format(_v(prior, 'volume'))}m to {_format(_v(current, 'volume'))}m MMBtu. "
                     f"At the prior fee per unit, volume accounts for ₹{_format(volume_effect / 10)} crore of the fee increase. "
                     f"Fee and mix account for a residual of ₹{_format(fee_effect / 10, 3)} crore. FY2026 realised fee averaged ₹{_format(rate, 3)} per MMBtu.",
                     "Review contract mix and fee changes. The bridge holds the prior rate fixed while varying volume.",
                     *(cell["ev"] for row in (prior, current) for cell in row.values())),
            _section("Is profit turning into cash?",
                     f"Operating cash was ₹{_format(cash25['value'], 3)} crore in FY2025 and ₹{_format(cfo['value'], 3)} crore in FY2026. "
                     f"The grouped liabilities line swung from ₹{_format(prior_group['value'], 3)} crore to ₹{_format(liabilities['value'], 3)} crore. "
                     f"Removing only that FY2026 line leaves ₹{_format(cash_ex_line, 3)} crore as a sensitivity. Settlement accounts held "
                     f"₹{_format(cash['settlement_accounts']['value'], 3)} crore of closing cash.",
                     "Verify customer settlement timing and how much cash is available for general use.",
                     cash25.get("ev"), prior_group.get("ev"), cfo["ev"], liabilities["ev"], settlement["ev"]),
            _section("Which listed benchmarks fit?",
                     "IEX provides same-year operating scale and margin context. MCX adds exchange context. Gas, power and derivatives have distinct trade units and settlement arrangements.",
                     "Revisit the comparison if the exchange disclosures support matched fee units or comparable cash classifications.",
                     offer_ev, current["volume"]["ev"]),
            _section("What does the quote imply?",
                     (f"A dated dealer quote implies {_format(pe)}× FY2026 basic EPS and ₹{_format(cap)} crore on 75 million draft shares. "
                      if pe is not None and cap is not None else "An indicative multiple requires a dated quote and reported basic EPS. ")
                     + "The draft is an offer for sale of up to 16.71 million shares. An official price band and executable transfer terms are pending.",
                     "Recompute from the final offer price, updated share count and any verified off-exchange lot terms.",
                     company["quote"]["ev"], shares_ev, offer_ev, *company["valuation"]["pe_reported"]["ev"]),
        ]}


def _build_oyo(company: dict, docs: dict) -> None:
    evidence = _evidence(company)
    addendum, draft, report = (docs.get(key) for key in ("oyo-addendum", "oyo-udrhp", OYO_REPORT))
    _stage(company, evidence, addendum or draft,
           "Updated draft · October addendum" if addendum else "Updated draft filed",
           "Fresh offer revised to up to ₹3,350 crore. Proposed pre-IPO placement removed." if addendum
           else "Updated draft filed with SEBI and the stock exchanges.")
    for key in ("market_cap", "pe", "pe_reported", "pe_proxy", "pb", "ps", "eps"):
        company["valuation"][key].update(value=None, state=M.MISSING,
                                        note="Provider share count omits the proposed preference conversion. A reviewed valuation basis is required.")
    if not report:
        return
    facts = _reported(evidence, report, OYO_FIELDS, "INR million")
    for period, row in facts.items():
        capex = _v(row, "ppe_capex") + _v(row, "intangible_capex")
        eid = evidence.add(_source(report, 165, "Cash capex (PPE/CWIP and intangibles)", str(capex * 10),
                                   "INR million", period=period, period_label=f"31 March {period[2:]}", basis="consolidated",
                                   derived=True, components=[
                                       {"label": evidence.items[row[k]["ev"]]["raw_label"],
                                        "value": str(_v(row, k) * 10)} for k in ("ppe_capex", "intangible_capex")
                                   ]))
        row["capex"] = {"value": str(capex), "state": "reported", "ev": eid}
    _publish_financials(company, report, facts, effects_after_net=True, note=OYO_BRIDGE_NOTE)
    company["valuation"]["period"] = "FY2026"
    current, prior = facts["FY2026"], facts["FY2025"]
    if draft:
        shares_ev = evidence.add(_source(draft, 132, "Pre-offer shares after preference conversion", "15,053,791,264", "shares"))
        _apply_quote_valuation(company, "15053791264", shares_ev, current["eps_basic"], current["eps_diluted"],
                               "consolidated", "Quote is indicative. Equity value assumes conversion of preference shares at draft terms, before the new issue; the final share count and price band are pending.",
                               conditional=True)
    else:
        shares_ev = None
    contribution = (_v(current, "g6_gbv") - _v(prior, "g6_gbv")) / (_v(current, "gbv") - _v(prior, "gbv")) * 100
    rev_growth = (_v(current, "revenue_ops") / _v(prior, "revenue_ops") - 1) * 100
    cash_keys = ("cfo", "capex", "debt_interest", "lease_interest", "lease_principal")
    cash = sum(_v(current, key) for key in cash_keys)
    prior_cash = sum(_v(prior, key) for key in cash_keys)
    pe = company["valuation"]["pe"]["value"]
    cap = company["valuation"]["market_cap"]["value"]
    dealer = company["quote"]["price_inr"]
    offer_ev = evidence.add(_source(addendum, 1, "Fresh issue and borrowing repayment", "33,500.00 / 25,125.00", "INR million")) if addendum else None
    benchmark = _benchmark("nse-lemontree", "Lemon Tree Hotels", "context",
                           "The FY2026 third-party management and franchise fees illustrate one shared business activity. Lemon Tree also owns and leases hotels. The group margins, cash conversion and quote multiples are not peer benchmarks.")
    lemon = docs.get(LEMON_REPORT)
    fee_ev = evidence.add(_source(lemon, 31, "Third-party management and franchise fees", "73.9", "INR crore",
                                    period="FY2026", period_label="31 March 2026")) if lemon else None
    company["issuer_case"] = {"period": "FY2026", "basis": "Audited consolidated", "benchmarks": [benchmark] if lemon else [],
        "metrics": {"g6_pct_of_gbv_increase": str(contribution), "cash_after_capex_interest_and_leases_cr": str(cash),
                    "prior_cash_after_capex_interest_and_leases_cr": str(prior_cash),
                    "indicated_pe": pe, "conditional_equity_cr": cap},
        "sections": [
            _section("What drives growth?",
                     f"FY2026 operating revenue grew {_format(rev_growth, 1)}%. G6 supplied {_format(contribution, 1)}% of the increase in gross booking value as its first full year entered the comparison. Ex-G6 hotel bookings also grew.",
                     "Use a full-year G6 same-store bridge and separate gross bookings from the revenue Oravel recognises.",
                     current["revenue_ops"]["ev"], prior["revenue_ops"]["ev"], *(
                         row[key]["ev"] for row in (current, prior) for key in ("g6_gbv", "gbv", "hotel_gbv"))),
            _section("Is profit turning into cash?",
                     f"Operating cash reached ₹{_format(_v(current, 'cfo'))} crore. After cash capex, borrowing interest and lease payments, "
                     f"₹{_format(cash, 3)} crore remained versus ₹{_format(prior_cash, 3)} crore in FY2025. "
                     f"Reported FY2026 PAT includes a net tax credit of ₹{_format(-_v(current, 'tax'))} crore. "
                     "The cash sensitivity still excludes debt principal and acquisition payments.",
                     "Review repeatability of working-capital movements, acquisition integration and refinancing.",
                     current["tax"]["ev"], *(row[key]["ev"] for row in (current, prior) for key in cash_keys)),
            _section("Which listed benchmarks fit?",
                     ("Lemon Tree discloses ₹73.9 crore from third-party management and franchise fees in FY2026. That is contextual evidence for the fee model. "
                      if lemon else "A dated listed fee benchmark is unavailable from retained sources. ")
                     + "Oravel combines global franchise, principal hotel and home-agent revenues, and acquired G6.",
                     "Require matched third-party franchise fee and property definitions before comparing monetisation.",
                     fee_ev, current["g6_gbv"]["ev"], current["hotel_gbv"]["ev"]),
            _section("What does the quote imply?",
                     (f"The ₹{_format(dealer)} dealer indication gives {_format(pe)}× reported basic EPS and about ₹{_format(cap, 0)} crore on the draft's converted pre-issue share count. "
                      if pe is not None and cap is not None else "A dated dealer quote and verified share basis are needed for valuation. ")
                     + "Tax credits, preference conversion and eventual new shares affect interpretation. "
                     + ("The October addendum revises the fresh issue to up to ₹3,350 crore and earmarks ₹2,512.50 crore for borrowing repayment. " if addendum else "")
                     + "The official price band remains pending.",
                     "Refresh with executable quote terms, final capitalization, updated debt uses and the offer price.",
                     company["quote"]["ev"], current["eps_basic"]["ev"], shares_ev, offer_ev),
        ]}


def enrich_pre_ipo(company: dict, docs: dict) -> None:
    if company["id"] == "igx":
        _build_igx(company, docs)
    elif company["id"] == "oyo":
        _build_oyo(company, docs)


def enrich_lemon_tree(company: dict, doc: dict) -> None:
    evidence = _evidence(company)
    facts = _reported(evidence, doc, LEMON_FIELDS, "INR lakh")
    for row in facts.values():
        row["other_effects"] = {"value": None, "state": "included_in_activity_totals", "ev": row["net_change"]["ev"]}
    _publish_financials(company, doc, facts, effects_after_net=False, note="Consolidated financial statements. Standalone hotel results are a separate scope.")
    company["documents"] = [{key: doc[key] for key in ("id", "title", "url", "retrieved_at", "sha256")}]
    fee = evidence.add(_source(doc, 31, "Third-party management and franchise fees", "73.9", "INR crore", period="FY2026"))
    company["profile"]["description"] = "Owns, leases, manages and franchises hotels. FY2026 third-party management and franchise fees were ₹73.9 crore, up 23% year on year."
    company["issuer_case"] = {"period": "FY2026", "basis": "Audited consolidated", "benchmarks": [], "metrics": {},
                              "sections": [_section("What is comparable to Oravel?",
                                                    company["profile"]["description"],
                                                    "Compare third-party fees only once both issuers disclose identical fee and property scopes.", fee)]}
