"""Publish the selectable ratio catalogue using scoped source facts and Decimal arithmetic."""
from __future__ import annotations

from . import metrics as M
from .company import Evidence

RATIOS = {
    "Profitability": {
        "pat_margin": ("PAT margin", "%", "PAT / total income"),
        "net_profit_ratio": ("Net profit ratio", "%", "PAT / operating revenue"),
        "gross_margin": ("Gross margin", "%", "gross profit / operating revenue"),
        "operating_margin": ("Operating margin", "%", "operating profit / operating revenue"),
        "ebitda_margin": ("EBITDA margin", "%", "EBITDA / operating revenue"),
        "roe": ("Return on equity", "%", "PAT / average equity"),
        "roa": ("Return on assets", "%", "PAT / average assets"),
        "roce": ("ROCE", "%", "(PBT + finance costs) / (total assets − current liabilities)"),
        "other_income_share": ("Other-income share", "%", "other income / total income"),
    },
    "Growth and per share": {
        "revenue_growth": ("Revenue growth", "%", "operating revenue / prior-year operating revenue − 1"),
        "revenue_cagr": ("Three-year revenue CAGR", "%", "(operating revenue / operating revenue three years earlier)^(1/3) − 1"),
        "diluted_growth": ("Diluted EPS growth", "%", "diluted EPS / prior-year diluted EPS − 1"),
        "eps_basic": ("Reported basic EPS", "₹/share", "reported basic EPS"),
        "eps_diluted": ("Reported diluted EPS", "₹/share", "reported diluted EPS"),
        "book_per_share": ("Book value per share", "₹/share", "equity (₹ crore) × 10,000,000 / period-end shares"),
    },
    "Liquidity and debt": {
        "current_ratio": ("Current ratio", "×", "current assets / current liabilities"),
        "quick_ratio": ("Quick ratio", "×", "(current assets − inventories) / current liabilities"),
        "cash_ratio": ("Cash ratio", "×", "cash and equivalents / current liabilities"),
        "debt_equity": ("Debt-to-equity", "×", "reported debt / equity"),
        "interest_cover": ("Interest coverage", "×", "(PBT + finance costs) / finance costs"),
        "net_debt_ebitda": ("Net debt / EBITDA", "×", "(reported debt − cash and equivalents) / EBITDA"),
        "debt_cover": ("Debt service coverage", "×", "operating cash flow / scheduled principal and interest"),
    },
    "Cash generation": {
        "cfo_to_pat": ("Operating cash flow / profit", "×", "operating cash flow / PAT"),
        "cfo_margin": ("Operating cash flow margin", "%", "operating cash flow / operating revenue"),
        "cfo_current": ("Operating cash flow / current liabilities", "×", "operating cash flow / current liabilities"),
        "fcf_margin": ("Free cash flow margin", "%", "(operating cash flow + signed cash capex) / operating revenue"),
    },
    "Asset and working-capital efficiency": {
        "asset_turnover": ("Asset turnover", "×", "operating revenue / average total assets"),
        "fixed_turnover": ("Fixed-asset turnover", "×", "operating revenue / average fixed assets"),
        "inventory_days": ("Inventory days", "days", "365 × average inventory / cost of sales"),
        "receivable_days": ("Receivable days", "days", "365 × average trade receivables / operating revenue"),
        "payable_days": ("Payable days", "days", "365 × average trade payables / cost of sales"),
        "cash_cycle": ("Cash conversion cycle", "days", "inventory days + receivable days − payable days"),
    },
    "Valuation and distributions": {
        "pe": ("P/E at quote", "×", "dated price / annual EPS"),
        "pb": ("Price-to-book", "×", "indicative market cap / equity"),
        "ps": ("Price-to-sales", "×", "indicative market cap / operating revenue"),
        "ev_ebitda": ("EV / EBITDA", "×", "(market cap + debt − cash) / EBITDA"),
        "ev_revenue": ("EV / revenue", "×", "(market cap + debt − cash) / operating revenue"),
        "dividend_payout": ("Dividend payout ratio", "%", "reported dividend per share / annual basic EPS"),
        "dividend_yield": ("Indicative dividend yield", "%", "reported dividend per share / quoted price"),
        "dividend_per_share": ("Dividend per share", "₹/share", "reported dividend per share"),
    },
    "Lender measures": {
        "nim": ("Net interest margin", "%", "issuer's reported NIM"),
        "gross_npa": ("Gross NPA ratio", "%", "issuer's reported gross NPA ratio"),
        "net_npa": ("Net NPA ratio", "%", "issuer's reported net NPA ratio"),
        "provision_coverage": ("Provision coverage", "%", "issuer's reported coverage"),
        "capital_adequacy": ("Capital adequacy", "%", "issuer's reported capital adequacy"),
    },
    "Insurer measures": {
        "claims_ratio": ("Incurred claims ratio", "%", "issuer's reported claims ratio"),
        "combined_ratio": ("Combined ratio", "%", "issuer's reported combined ratio"),
        "solvency_ratio": ("Solvency ratio", "×", "issuer's reported solvency ratio"),
    },
    "Exchange measures": {
        "volume_growth": ("Traded-volume growth", "%", "matched-contract volume / prior-year volume − 1"),
        "fee_per_unit": ("Transaction fee per unit", "₹/unit", "transaction fee / same-contract traded volume"),
    },
}
DEFAULT = ["revenue_growth", "ebitda_margin", "roce", "cfo_to_pat", "net_debt_ebitda", "pe"]
DEFAULTS = {
    "exchange": ["revenue_growth", "other_income_share", "net_profit_ratio", "volume_growth", "cfo_to_pat", "pe"],
    "lender": ["nim", "gross_npa", "net_npa", "capital_adequacy", "roe", "pe"],
    "insurer": ["claims_ratio", "combined_ratio", "solvency_ratio", "revenue_growth", "roe", "pe"],
}
SECTOR_GROUPS = {"Lender measures": "lender", "Insurer measures": "insurer", "Exchange measures": "exchange"}
NO_CURRENT = {"current_ratio", "quick_ratio", "cash_ratio", "roce", "cfo_current", "net_debt_ebitda",
              "inventory_days", "payable_days", "cash_cycle", "ev_ebitda", "ev_revenue"}


def _issuer_facts(company: dict) -> dict:
    recon = company.get("reconciliation") or {}
    if not recon.get("operating_scope"):
        return {}
    evidence = Evidence()
    evidence.items = company["evidence"]
    result = {}
    for name in ("income_statement", "balance_sheet"):
        statement = recon["selected"]["statements"][name]
        if not statement["title_confirmed"] or statement["unit_text"] != "Indian Rupees millions":
            continue
        for field, line in statement["lines"].items():
            for period, token in line.get("raw_values", {}).items():
                state = "dash" if token == "-" else "reported"
                eid = evidence.add({
                    "source": "IGX Restated Financial Information", "url": f'{recon["url"]}#page={statement["page"]}',
                    "source_date": "2026-07-14", "retrieved_at": recon["retrieved_at"], "sha256": recon["sha256"],
                    "file": recon["file"], "capture_run": recon["capture_run"], "page": statement["page"],
                    "raw_label": line["matched_text"], "raw_text": token, "period": period,
                    "period_label": f"31 March {period[2:]}", "basis": "issuer_and_esos_trust",
                    "raw_unit": "INR per share" if field.startswith("eps") else "INR million",
                })
                result.setdefault(period, {})[{"eps": "eps_basic"}.get(field, field)] = {
                    "value": None if state == "dash" else line["values_inr_crore"][period], "state": state, "ev": eid,
                }
    return result


def build_ratios(company: dict) -> dict:
    """Only combine values with the selected period's reporting scope."""
    issuer = _issuer_facts(company)
    fields = company["fields"]
    by_period = {}
    analysis = {}
    catalogue = {key: (group, *spec) for group, specs in RATIOS.items() for key, spec in specs.items()}
    for period in company["periods"]:
        cash = company["cash_flow"]["by_period"].get(period, {})
        restated = issuer.get(period)
        basis = "issuer_and_esos_trust" if restated else company["basis"]
        facts = dict(restated) if restated else {key: field["by_period"].get(period, {}) for key, field in fields.items()}
        if cash.get("basis") == basis:
            facts.update({key: cell for key, cell in cash["lines"].items() if key in ("cfo", "cfi", "cff", "capex")})
        analysis[period] = {"basis": basis, "facts": facts}
        if not (period.startswith("FY") and not period.endswith("?")):
            by_period[period] = {}
            continue
        year = int(period[2:])
        prior = f"FY{year - 1}"
        start = f"FY{year - 3}"
        results = {}

        def fact(key, p=period):
            if p == period:
                cell = facts.get(key, {})
            elif restated:
                cell = issuer.get(p, {}).get(key, {})
            else:
                cell = fields.get(key, {}).get("by_period", {}).get(p, {})
            record = company["evidence"].get(cell.get("ev"), {})
            if record.get("basis") and record["basis"] != basis:
                return None, None
            return M.dec(cell.get("value")), cell.get("ev")

        def value(key, p=period):
            return fact(key, p)[0]

        def evidence(*keys):
            return list(dict.fromkeys(eid for key in keys if (eid := fact(*key)[1] if isinstance(key, tuple) else fact(key)[1])))

        def ratio(key, a, b, inputs):
            label, unit, formula = catalogue[key][1:]
            r = M.ratio(a, b, formula, unit=unit, pct=unit == "%")
            if b is not None and b < 0:
                r = M.result(None, M.NEG_BASE, formula, r["inputs"], "Requires a positive denominator.", unit)
            results[key] = {**r, "ev": evidence(*inputs), "basis": basis}

        def pair(key, a, b):
            ratio(key, value(a), value(b), (a, b))

        def avg(key):
            return M.average(value(key), value(key, prior))

        def total(a, b, subtract=False):
            return (a - b if subtract else a + b) if a is not None and b is not None else None

        rev, other = value("revenue_ops"), value("other_income")
        total_income = value("total_income") if value("total_income") is not None else total(rev, other)
        for key, num in (("pat_margin", "pat"), ("other_income_share", "other_income")):
            ratio(key, value(num), total_income, (num, "total_income", "revenue_ops", "other_income"))
        for key, num in (("net_profit_ratio", "pat"), ("gross_margin", "gross_profit"),
                         ("operating_margin", "operating_profit"), ("ebitda_margin", "ebitda"),
                         ("cfo_margin", "cfo")):
            pair(key, num, "revenue_ops")
        for key, num, denom in (("roa", "pat", "total_assets"), ("roe", "pat", "total_equity"),
                                 ("asset_turnover", "revenue_ops", "total_assets"),
                                 ("fixed_turnover", "revenue_ops", "fixed_assets")):
            ratio(key, value(num), avg(denom), (num, denom, (denom, prior)))
        for key, num, denom in (("current_ratio", "current_assets", "current_liabilities"),
                                 ("cash_ratio", "cash", "current_liabilities"), ("debt_equity", "borrowings", "total_equity"),
                                 ("cfo_current", "cfo", "current_liabilities"), ("cfo_to_pat", "cfo", "pat"),
                                 ("dividend_payout", "dividend_per_share", "eps_basic")):
            pair(key, num, denom)
        ebit = total(value("pbt"), value("finance_cost"))
        ratio("roce", ebit, total(value("total_assets"), value("current_liabilities"), True),
              ("pbt", "finance_cost", "total_assets", "current_liabilities"))
        ratio("interest_cover", ebit, value("finance_cost"), ("pbt", "finance_cost"))
        net_debt = total(value("borrowings"), value("cash"), True)
        ratio("net_debt_ebitda", net_debt, value("ebitda"), ("borrowings", "cash", "ebitda"))
        ratio("fcf_margin", total(value("cfo"), value("capex")), rev, ("cfo", "capex", "revenue_ops"))
        results["fcf_margin"]["note"] = "Requires operating cash flow and paid cash capex for the same period and basis."
        quick = company["metrics"].get(period, {}).get("quick_ratio")
        if quick:
            results["quick_ratio"] = {**quick, "basis": quick.get("basis", company["basis"])}
        for key, metric, historic in (("revenue_growth", "revenue_ops", prior), ("revenue_cagr", "revenue_ops", start),
                                      ("diluted_growth", "eps_diluted", prior)):
            r = M.cagr(value(metric), value(metric, historic), 3) if historic == start else M.growth(value(metric), value(metric, historic))
            results[key] = {**r, "basis": basis, "ev": evidence(metric, (metric, historic))}
        activity = company.get("market_activity", {})
        if period in activity:
            volume = activity[period]["volume"]
            fees = activity[period]["fees"]
            earlier_volume = activity.get(prior, {}).get("volume", {})
            results["volume_growth"] = {**M.growth(volume["value"], earlier_volume.get("value")),
                                        "basis": "IGX trading venue", "ev": [volume["ev"]] + ([earlier_volume["ev"]] if earlier_volume else [])}
            results["fee_per_unit"] = {**M.ratio(fees["value"], volume["value"],
                                               "transaction fees net of reversals (₹ million) / traded volume (million MMBtu)",
                                               ("net_transaction_fees", "volume"), "₹/MMBtu"),
                                       "basis": "IGX trading venue", "ev": [fees["ev"], volume["ev"]]}
        for key, series, denominator in (("inventory_days", "inventories", "cost_of_sales"),
                                          ("payable_days", "trade_payables", "cost_of_sales"),
                                          ("receivable_days", "trade_receivables", "revenue_ops")):
            mean = avg(series)
            ratio(key, mean * 365 if mean is not None else None, value(denominator), (series, (series, prior), denominator))
        results["receivable_days"]["note"] = "Operating revenue proxies for credit sales; uses 365 days."
        results["payable_days"]["note"] = "Cost of sales proxies for supplier purchases; uses 365 days."
        days = [results[key] for key in ("inventory_days", "receivable_days", "payable_days")]
        if all(d["state"] == "ok" for d in days):
            result = M.dec(days[0]["value"]) + M.dec(days[1]["value"]) - M.dec(days[2]["value"])
            results["cash_cycle"] = {**M.result(result, M.OK, catalogue["cash_cycle"][3], {}, unit="days"),
                                     "ev": list(dict.fromkeys(eid for d in days for eid in d["ev"])), "basis": basis}
        shares = value("shares_outstanding")
        equity = value("total_equity")
        ratio("book_per_share", equity * 10_000_000 if equity is not None else None, shares, ("total_equity", "shares_outstanding"))
        for key in ("eps_basic", "eps_diluted", "dividend_per_share", *RATIOS["Lender measures"], *RATIOS["Insurer measures"]):
            shown = value(key)
            source = company["evidence"].get(fact(key)[1], {})
            unit = catalogue[key][2]
            if unit in ("%", "×") and source.get("raw_unit") != ("%" if unit == "%" else "x"):
                shown = None
            results[key] = {**M.result(shown, M.OK if shown is not None else M.MISSING, catalogue[key][3], {key: shown}, unit=unit),
                            "ev": evidence(key), "basis": basis}
        if period == company["periods"][-1]:
            valuation = company["valuation"]
            for key in ("pe", "pb", "ps"):
                results[key] = {"basis": company["basis"], **valuation[key]}
            quote = company["quote"]
            price = M.dec(quote["price_inr"]) if valuation["market_cap"]["state"] != "suspect_quote" else None
            ratio("dividend_yield", value("dividend_per_share"), price, ("dividend_per_share",))
            if quote["ev"]:
                results["dividend_yield"]["ev"].append(quote["ev"])
            cap = M.dec(valuation["market_cap"]["value"]) if valuation["market_cap"]["state"] == M.OK else None
            enterprise = total(cap, net_debt)
            for key, den in (("ev_ebitda", "ebitda"), ("ev_revenue", "revenue_ops")):
                ratio(key, enterprise, value(den), ("borrowings", "cash", den))
                results[key]["note"] = "Requires market cap and debt/cash on the same basis; no adjustment for undisclosed debt."
        for key, (group, _, unit, formula) in catalogue.items():
            sector = SECTOR_GROUPS.get(group)
            model = company["model"]
            if (sector and model != sector) or (model in {"lender", "insurer"} and key in NO_CURRENT) or (
                model == "exchange" and key in {"inventory_days", "cash_cycle"}
            ):
                results[key] = M.result(None, M.INAPPLICABLE, formula, {}, "The measure does not apply to this business model.", unit)
            results.setdefault(key, M.result(None, M.MISSING, formula, {}, unit=unit))
            results[key].setdefault("basis", basis)
            results[key].setdefault("unit", unit)
            if results[key]["state"] == M.MISSING:
                results[key].setdefault("note", "Required comparable inputs are unavailable.")
        by_period[period] = results
    company["analysis"] = analysis
    return {
        "defaults": DEFAULTS.get(company["model"], DEFAULT),
        "groups": {group: [{"id": key, "label": spec[0], "unit": spec[1], "formula": spec[2]} for key, spec in entries.items()]
                   for group, entries in RATIOS.items()},
        "by_period": by_period,
    }
