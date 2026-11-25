"""Cash-flow statement projections. Keep issuer and provider observations separate."""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from .issuer import NUM, igx_operating_scope, page_texts

ACTIVITIES = ("cfo", "cfi", "cff")
TOTALS = ("opening", *ACTIVITIES, "other_effects", "net_change", "closing")
DETAILS = (
    "before_working_capital", "receivables", "other_assets", "payables_and_liabilities", "tax_paid",
    "capex", "net_investment_purchases", "debt_principal", "lease_principal", "lease_interest",
    "overdraft_interest", "share_proceeds", "dividends", "current_accounts", "settlement_accounts",
)
IGX_ROWS = {
    "opening": r"E\. Cash and cash equivalents at the beginning of the year",
    "cfo": r"Net cash generated from/\(used in\) operating activities",
    "cfi": r"Net cash \(used in\)/ generated from investing activities",
    "cff": r"Net cash \(used in\) financing activities",
    "net_change": r"D\. Net decrease in cash and cash equivalents during the year \(A\+B\+C\)",
    "closing": r"F\. Cash and cash equivalents as at the end of the year \(D\+E\)",
    "before_working_capital": r"Operating profit before working capital changes",
    "receivables": r"\(Increase\) / Decrease in trade receivables",
    "other_assets": r"\(Increase\) /Decrease in other financial assets and other assets",
    "payables_and_liabilities": r"Increase / \(Decrease\) in trade payables, other financial liabilities, provisions and other liabilities",
    "tax_paid": r"Income tax paid \(net of refund\)",
    "capex": r"Purchase of Property, plant and equipment, capital work in progress, other intangible assets and Intangible asset under development",
    "net_investment_purchases": r"\(Outflow\) / Inflow from purchase / sale of investments \(net\)",
    "lease_principal": r"Principal repayment of lease liabilities",
    "lease_interest": r"Interest paid on lease liabilities",
    "overdraft_interest": r"Interest paid on overdraft and others",
    "share_proceeds": r"Proceeds from issue of equity shares",
    "dividends": r"Payment of dividend 17",
    "current_accounts": r"In current accounts",
    "settlement_accounts": r"In settlement accounts",
}


def _empty_lines() -> dict:
    return {key: {"state": "not_in_source", "value": None} for key in (*TOTALS, *DETAILS)}


def _issuer_cell(token: str, ev: str) -> dict:
    if token == "-":
        return {"state": "dash", "value": None, "ev": ev}
    number = Decimal(token.strip("()").replace(",", ""))
    if token.startswith("("):
        number = -number
    return {"state": "explicit_zero" if number == 0 else "reported",
            "value": format(number / 10, ".3f"), "ev": ev}


def _reconcile(lines: dict, *, effects_after_net: bool = False, tolerance: Decimal = Decimal(0)) -> dict:
    keys = ("opening", *ACTIVITIES, "net_change", "closing")
    if any(lines[key]["value"] is None for key in keys) or (
        lines["other_effects"]["value"] is None and lines["other_effects"]["state"] != "included_in_activity_totals"
    ):
        return {"state": "partial"}
    amounts = {key: Decimal(lines[key]["value"]) for key in keys}
    movement = sum(amounts[key] for key in ACTIVITIES)
    effects = Decimal(lines["other_effects"]["value"] or "0")
    if not effects_after_net:
        movement += effects
    activity_residual = movement - amounts["net_change"]
    balance_residual = amounts["opening"] + amounts["net_change"] - amounts["closing"]
    if effects_after_net:
        balance_residual += effects
    state = "conflict"
    if activity_residual == balance_residual == 0:
        state = "reconciled"
    elif max(abs(activity_residual), abs(balance_residual)) <= tolerance:
        state = "rounding_difference"
    return {
        "state": state,
        "activity_residual": format(activity_residual, ".3f"),
        "balance_residual": format(balance_residual, ".3f"),
    }


def reviewed_cash_view(facts: dict, *, report: str, effects_after_net: bool, note: str) -> dict:
    lines = _empty_lines()
    lines.update({key: facts[key] for key in lines if key in facts})
    if "debt_interest" in facts:
        lines["debt_interest"] = facts["debt_interest"]
    return {
        "basis": "consolidated", "origin": "issuer_audited", "provider_name": report,
        "lines": lines, "effects_after_net": effects_after_net, "note": note, "provider_comparison": None,
        "reconciliation": _reconcile(lines, effects_after_net=effects_after_net, tolerance=Decimal("0.001")),
    }


def _igx_statement(doc: dict, evidence) -> dict:
    pdf = Path(doc["abs_path"])
    texts = page_texts(pdf)
    if texts["sha256"] != doc["sha256"] or not igx_operating_scope(pdf):
        return {}
    page = " ".join(texts["pages"][6].split())
    if "Annexure III: Restated Statement of Cash flows" not in page or "in Indian Rupees millions" not in page:
        return {}
    years = re.findall(r"For the year ended 31 March (\d{4})", page.partition("A. Cash flows")[0])
    if len(years) != 3 or len(set(years)) != 3:
        return {}
    source = {
        "source": "IGX Restated Financial Information", "source_id": doc["id"], "url": f'{doc["url"]}#page=7',
        "source_date": "2026-07-14", "retrieved_at": doc["retrieved_at"], "sha256": doc["sha256"],
        "capture_run": doc["capture_run"], "file": pdf.name, "page": 7, "raw_unit": "INR million",
        "basis": "issuer_and_esos_trust", "statement": "cash_flow",
    }
    by_period = {f"FY{year}": _empty_lines() for year in years}
    for key, label in IGX_ROWS.items():
        matches = list(re.finditer(rf"(?<!\S)({label}) ({NUM}) ({NUM}) ({NUM})(?!\S)", page))
        if len(matches) != 1:
            if len(matches) > 1:
                for lines in by_period.values():
                    lines[key]["state"] = "conflict"
            continue
        match = matches[0]
        for year, token in zip(years, match.groups()[1:]):
            period = f"FY{year}"
            ev = evidence.add({**source, "raw_label": match[1], "raw_text": token, "period": period,
                               "period_label": f"31 March {year}", "period_end": f"{year}-03-31",
                               "anchor": f"Physical page 7 · {match[1]}"})
            by_period[period][key] = _issuer_cell(token, ev)
    for lines in by_period.values():
        # The filing explicitly defines net change as A+B+C and closing as D+E.
        if lines["net_change"].get("ev") and lines["closing"].get("ev"):
            lines["other_effects"] = {"state": "included_in_activity_totals", "value": None,
                                      "ev": lines["net_change"]["ev"]}
    return by_period


def build_cash_flow(company: dict, doc: dict | None, evidence) -> dict:
    """A single company projection for Page 1 and the future workspace detail."""
    issuer_periods = _igx_statement(doc, evidence) if doc else {}
    periods = dict.fromkeys([*company["periods"], *issuer_periods])
    for period in periods:
        provider = _empty_lines()
        for key in (*ACTIVITIES, "net_change"):
            provider[key] = company["fields"].get(key, {}).get("by_period", {}).get(period, provider[key])
        issuer = issuer_periods.get(period)
        lines = issuer if issuer is not None else provider
        basis = "issuer_and_esos_trust" if issuer is not None else company["basis"]
        differences = {}
        if issuer is not None:
            for key in ACTIVITIES:
                a, b = issuer[key]["value"], provider[key]["value"]
                if a is not None and b is not None:
                    delta = Decimal(a) - Decimal(b)
                    differences[key] = {"issuer_minus_provider": format(delta, ".3f"),
                                        "state": "within_provider_rounding" if abs(delta) <= Decimal("0.005") else "differs"}
        periods[period] = {
            "basis": basis, "origin": "issuer_restated" if issuer is not None else "provider",
            "provider_name": company.get("statement_provider", "WWIPL"),
            "lines": lines, "reconciliation": _reconcile(lines),
            "provider_comparison": {"lines": {key: provider[key] for key in ACTIVITIES},
                                    "differences": differences} if issuer is not None else None,
        }
    return {"unit": "INR crore", "by_period": periods}
