"""Illustrative holding-level price paths and portfolio horizon arithmetic."""
from decimal import Decimal, ROUND_HALF_UP


CASES = ("downside", "base", "upside")
ASSUMPTIONS = {
    "money_market_etf": (2, 5, 7),
    "gold_etf": (-15, 5, 15),
    "listed_equity": (-20, 8, 20),
    "high_volatility_equity": (-30, 10, 30),
    "unlisted_equity": (-35, 0, 30),
    "cash": (0, 0, 0),
}


def return_scenarios(holdings: list[dict], amount: Decimal, horizon: int) -> dict:
    years = Decimal(horizon) / 12
    paise = Decimal("0.01")
    totals = {case: Decimal(0) for case in CASES}
    for row in holdings:
        kind = row["kind"]
        invested = row["amount_inr"]
        coupon_rate = row.get("coupon_rate")
        if kind == "sovereign_bond":
            assumptions = (6, coupon_rate if coupon_rate is not None else 7, 9)
        else:
            assumptions = ASSUMPTIONS[kind]
        cases = {}
        for case, rate in zip(CASES, assumptions):
            rate = Decimal(str(rate))
            growth = 1 + rate * years / 100 if kind == "sovereign_bond" else (1 + rate / 100) ** years
            exit_haircut = row.get("downside_exit_haircut_pct", Decimal(0)) if case == "downside" else Decimal(0)
            end = (invested * growth * (1 - exit_haircut / 100)).quantize(paise, rounding=ROUND_HALF_UP)
            cases[case] = {"annual_assumption_pct": rate, "ending_value_inr": end}
            totals[case] += end
        row["return_scenarios"] = cases
    return {case: {"ending_value_inr": total, "gain_inr": total - amount,
                  "horizon_return_pct": ((total - amount) * 100 / amount).quantize(paise, rounding=ROUND_HALF_UP),
                  "annualized_return_pct": (((total / amount) ** (1 / years) - 1) * 100).quantize(paise, rounding=ROUND_HALF_UP)}
            for case, total in totals.items()}
