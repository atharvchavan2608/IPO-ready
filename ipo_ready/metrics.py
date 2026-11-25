"""Deterministic financial metrics with explicit result states.

Every function returns a Result dict: {"value": str|None, "state": ..., "formula": ..., "inputs": {...},
"note": ...}. States: ok, missing_input, zero_denominator, negative_base, inapplicable.
Arithmetic uses Decimal; values are serialised as strings rounded for display only at the edge.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

OK, MISSING, ZERO_DEN, NEG_BASE, INAPPLICABLE = "ok", "missing_input", "zero_denominator", "negative_base", "inapplicable"

D = Decimal


def dec(x) -> Decimal | None:
    if x is None:
        return None
    if isinstance(x, Decimal):
        return x
    return D(str(x))


def q(x: Decimal | None, places: str = "0.0001") -> str | None:
    return None if x is None else format(x.quantize(D(places), rounding=ROUND_HALF_UP), "f")


def result(value, state, formula, inputs, note=None, unit=None) -> dict:
    r = {"value": q(value) if isinstance(value, Decimal) else value, "state": state, "formula": formula,
         "inputs": {k: (None if v is None else format(v, "f") if isinstance(v, Decimal) else v) for k, v in inputs.items()}}
    if note:
        r["note"] = note
    if unit:
        r["unit"] = unit
    return r


def ratio(num, den, formula, names=("numerator", "denominator"), unit="x", pct=False) -> dict:
    n, d = dec(num), dec(den)
    inputs = {names[0]: n, names[1]: d}
    if n is None or d is None:
        return result(None, MISSING, formula, inputs, unit=unit)
    if d == 0:
        return result(None, ZERO_DEN, formula, inputs, "denominator is zero", unit=unit)
    v = n / d * (100 if pct else 1)
    return result(v, OK, formula, inputs, unit=unit)


def growth(curr, prev, formula="(current / previous) - 1") -> dict:
    c, p = dec(curr), dec(prev)
    inputs = {"current": c, "previous": p}
    if c is None or p is None:
        return result(None, MISSING, formula, inputs, unit="%")
    if p == 0:
        return result(None, ZERO_DEN, formula, inputs, "previous value is zero", unit="%")
    if p < 0:
        return result(None, NEG_BASE, formula, inputs, "growth from a negative base is not meaningful", unit="%")
    return result((c / p - 1) * 100, OK, formula, inputs, unit="%")


def cagr(end, start, years: int) -> dict:
    e, s = dec(end), dec(start)
    formula = f"(end / start)^(1/{years}) - 1"
    inputs = {"end": e, "start": s, "years": years}
    if e is None or s is None:
        return result(None, MISSING, formula, inputs, unit="%")
    if years <= 0:
        return result(None, ZERO_DEN, formula, inputs, "elapsed years must be positive", unit="%")
    if s <= 0 or e <= 0:
        return result(None, NEG_BASE, formula, inputs, "CAGR needs positive start and end values", unit="%")
    v = (D(float(e / s) ** (1 / years)) - 1) * 100
    return result(v, OK, formula, inputs, unit="%")


def average(a, b) -> Decimal | None:
    a, b = dec(a), dec(b)
    if a is None and b is None:
        return None
    if a is None or b is None:
        return None
    return (a + b) / 2


def quick_ratio(current_assets, inventories_value, inventories_state, current_liabilities) -> dict:
    """(Current assets - inventories) / current liabilities.

    inventories_state: 'reported' (use value), 'inapplicable' (issuer evidence that the business has
    no inventory: treat as 0 and say so), anything else -> the ratio is unavailable.
    """
    formula = "(current assets - inventories) / current liabilities"
    ca, cl = dec(current_assets), dec(current_liabilities)
    if inventories_state == "reported":
        inv = dec(inventories_value)
        note = None
    elif inventories_state == "inapplicable":
        inv = D(0)
        note = "inventories treated as nil: issuer states inventory ratios are not applicable and the balance sheet has no inventories line"
    else:
        return result(None, MISSING, formula, {"current_assets": ca, "inventories": None, "current_liabilities": cl},
                      "inventories not disclosed in the available source; quick ratio withheld", unit="x")
    inputs = {"current_assets": ca, "inventories": inv, "current_liabilities": cl}
    if ca is None or cl is None or inv is None:
        return result(None, MISSING, formula, inputs, unit="x")
    if cl == 0:
        return result(None, ZERO_DEN, formula, inputs, "current liabilities are zero", unit="x")
    return result((ca - inv) / cl, OK, formula, inputs, note, unit="x")


def market_cap_cr(price_inr, shares) -> dict:
    p, s = dec(price_inr), dec(shares)
    formula = "price (INR) x shares outstanding / 1e7"
    inputs = {"price_inr": p, "shares": s}
    if p is None or s is None:
        return result(None, MISSING, formula, inputs, unit="INR crore")
    return result(p * s / D(10_000_000), OK, formula, inputs, unit="INR crore")


def eps_from(pat_cr, shares) -> dict:
    p, s = dec(pat_cr), dec(shares)
    formula = "PAT (INR crore) x 1e7 / shares outstanding"
    inputs = {"pat_cr": p, "shares": s}
    if p is None or s is None:
        return result(None, MISSING, formula, inputs, unit="INR")
    if s == 0:
        return result(None, ZERO_DEN, formula, inputs, unit="INR")
    return result(p * D(10_000_000) / s, OK, formula, inputs, unit="INR")


def pe(price_inr, eps) -> dict:
    p, e = dec(price_inr), dec(eps)
    formula = "price / EPS"
    inputs = {"price_inr": p, "eps": e}
    if p is None or e is None:
        return result(None, MISSING, formula, inputs, unit="x")
    if e == 0:
        return result(None, ZERO_DEN, formula, inputs, "EPS is zero", unit="x")
    if e < 0:
        return result(None, NEG_BASE, formula, inputs, "loss-making: P/E not meaningful", unit="x")
    return result(p / e, OK, formula, inputs, unit="x")
