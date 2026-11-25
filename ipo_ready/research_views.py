"""Evidence-backed comparison cells, company observations and scenario assumptions."""
from __future__ import annotations

from decimal import Decimal

from . import metrics as M

ROWS = {"revenue": ("Operating revenue", "₹ crore"), "margin": ("PAT / operating revenue", "%"),
        "cfo": ("Operating cash flow", "₹ crore"), "pe": ("Indicative P/E", "×")}
BUSINESS = {
    "exchange": "Follow matched-volume and fee disclosures, competition and regulatory developments.",
    "manufacturer": "Follow utilisation, input costs, customer concentration and working capital.",
    "lender": "Follow underwriting, asset quality, funding costs and regulatory capital.",
    "insurer": "Follow claims experience, expense ratios and regulatory solvency.",
}


def build_research(company: dict) -> dict:
    listed = company["identity"]["listing"] == "listed"
    risk = {
        "summary": "Exchange-traded price risk" if listed else "Off-exchange exit risk",
        "business": BUSINESS.get(company["model"], "Follow revenue drivers, cash needs and business-specific disclosures."),
        "liquidity": ("Share price and depth can change before execution." if listed else
                      "Ask for an executable lot and confirm counterparty, settlement and transfer terms."),
        "restriction": ("Check applicable trading restrictions at execution." if listed else
                        "Verified transfer restrictions are unavailable in this scenario."),
        "horizon": ("Review at the next results announcement or within six months." if listed else
                    "Three years is an illiquidity planning assumption. Review at each relevant filing, quote or transfer change."),
    }
    result = {}
    for period, analysis in company["analysis"].items():
        facts, basis = analysis["facts"], analysis["basis"]
        ratios = company["ratios"]["by_period"].get(period, {})
        cells = {
            "revenue": facts.get("revenue_ops", {}), "margin": ratios.get("net_profit_ratio", {}),
            "cfo": facts.get("cfo", {}), "pe": ratios.get("pe", {}),
        }
        compare = {}
        for key, cell in cells.items():
            eps_basis = cell.get("eps_basis")
            comparison_basis = basis
            if key in {"revenue", "margin"} and basis == "issuer_and_esos_trust":
                comparison_basis = "standalone"
            if key == "pe":
                comparison_basis = cell.get("basis") or basis
            compare[key] = {
                "value": cell.get("value"), "state": cell.get("state", "missing_input"),
                "basis": cell.get("basis") or basis, "match_basis": comparison_basis,
                "definition": eps_basis or key, "ev": cell["ev"] if isinstance(cell.get("ev"), list)
                else [cell["ev"]] if cell.get("ev") else [],
            }
        claims = []

        def claim(category, title, interpretation, cell):
            ids = cell.get("ev", [])
            ids = [ids] if isinstance(ids, str) else ids
            if ids:
                claims.append({"category": category, "title": title, "interpretation": interpretation, "ev": ids})

        growth = ratios.get("revenue_growth", {})
        if growth.get("state") == M.OK:
            change = M.dec(growth["value"])
            if change:
                claim("Pro" if change > 0 else "Con", f"Operating revenue changed {change:.2f}% year on year",
                      "Use the matched annual revenue series and check whether volumes, pricing or a one-off drove the movement.", growth)
        volume = ratios.get("volume_growth", {})
        if volume.get("state") == M.OK:
            change = M.dec(volume["value"])
            if change:
                claim("Pro" if change > 0 else "Con", f"Traded gas volume changed {change:.2f}% year on year",
                      "Volume helps explain exchange activity. Fee realisation and mix can move independently.", volume)
        cfo = M.dec(facts.get("cfo", {}).get("value"))
        pat = M.dec(facts.get("pat", {}).get("value"))
        if cfo is not None and pat is not None and cfo < pat:
            claim("Con", "Operating cash flow was below profit",
                  "Inspect timing, receivables and other working capital before interpreting the cash shortfall.",
                  {"ev": [facts[key]["ev"] for key in ("cfo", "pat")]})
        cash = company["cash_flow"]["by_period"].get(period, {}).get("lines", {})
        liabs = cash.get("payables_and_liabilities", {})
        balances = cash.get("settlement_accounts", {})
        liability_inflow = M.dec(liabs.get("value"))
        if basis == "issuer_and_esos_trust" and cfo is not None and liability_inflow is not None and cfo > 0 and liability_inflow > cfo / 2:
            claim("Con", f"Grouped liabilities contributed ₹{liability_inflow:.3f} crore to cash flow",
                  "Review the settlement composition and separate recurring operating cash from timing effects.", liabs)
            if balances.get("value") is not None:
                claim("Context", f"Settlement accounts held ₹{balances['value']} crore at year-end",
                      "Verify which part of the closing cash can be used for general purposes.", balances)
        pe = compare["pe"]
        if pe["value"] is not None:
            claim("Valuation", f"Dated price implies {M.dec(pe['value']):.2f}× earnings",
                  f"Check the {pe['definition'].replace('_', ' ')} basis and update the quote before comparing valuation.", pe)
        docs = company.get("documents", [])
        stage = company.get("ipo_stage")
        if stage:
            receipt = company["evidence"][stage["ev"]]
            event = {"title": stage["milestone"], "url": receipt["url"]}
        elif any(item["id"] == "igx-drhp" for item in docs):
            # Reference the existing captured evidence for the regulatory event.
            event = next(item for item in docs if item["id"] == "igx-drhp")
        else:
            event = None
        revenue = M.dec(compare["revenue"]["value"])
        scenario = None if revenue is None else {
            "base": M.q(revenue, "0.01"), "upside": M.q(revenue * Decimal("1.10"), "0.01"),
            "downside": M.q(revenue * Decimal("0.90"), "0.01"),
            "note": "Illustrative sensitivity of operating revenue to a ±10% change. Review price, volume and margin assumptions after results.",
        }
        result[period] = {"comparison": compare, "claims": claims, "scenario": scenario,
                          "event": event, "financial_risk": ("Review cash versus profit and working capital." if cfo is not None else
                                                             "Same-period cash flow coverage is incomplete."),
                          "valuation_risk": "Recheck the dated price and EPS definition." if pe["value"] is not None else
                                            "Comparable price and/or annual earnings are unavailable."}
    return {"by_period": result, "risk": risk}
