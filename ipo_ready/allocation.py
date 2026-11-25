"""Deterministic scenario sizing with whole lots, concentration and stress limits."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP

from .scenario_returns import return_scenarios


PAISE = Decimal("0.01")
MAX_AMOUNT = Decimal("100000000")
DEFAULT_AMOUNT = "500000"
DEFAULT_TOLERANCE = "balanced"
EXCHANGE_CAP_PCT = 25
UNLISTED_SHOCK_PCT = Decimal(35)
EXIT_HAIRCUT_PCT = Decimal(25)
UNLISTED_LOSS_PCT = UNLISTED_SHOCK_PCT + (100 - UNLISTED_SHOCK_PCT) * EXIT_HAIRCUT_PCT / 100
METHOD_VERSION = "1.0"

# Listed risk buckets and scenario shock floors. These are demo assumptions.
INSTRUMENTS = {
    "FRSB2020T": ("low", 0),
    "HDFCBANK": ("medium", 30),
    "GOLDBEES": ("medium", 22),
    "MCX": ("high", 30),
}
PROFILES = {
    "conservative": {"targets": {"FRSB2020T": 55, "HDFCBANK": 25, "GOLDBEES": 15, "MCX": 5},
                     "max_loss_pct": 13, "unlisted_cap_pct": 5},
    "balanced": {"targets": {"FRSB2020T": 35, "HDFCBANK": 30, "GOLDBEES": 20, "MCX": 15},
                 "max_loss_pct": 19, "unlisted_cap_pct": 10},
    "growth": {"targets": {"FRSB2020T": 20, "HDFCBANK": 30, "GOLDBEES": 25, "MCX": 25},
               "max_loss_pct": 25, "unlisted_cap_pct": 20},
}
WORKSPACE_TARGETS = {
    "conservative": {"FRSB2020T": 40, "HDFCBANK": 20, "GOLDBEES": 15, "MCX": 5},
    "balanced": {"FRSB2020T": 30, "HDFCBANK": 22, "GOLDBEES": 20, "MCX": 13},
    "growth": {"FRSB2020T": 20, "HDFCBANK": 28, "GOLDBEES": 22, "MCX": 20},
}
LIQUID_SHOCK_PCT = Decimal(1)
TURNOVER_PARTICIPATION_PCT = Decimal(1)


class AllocationInputError(ValueError):
    """An invalid user-supplied scenario parameter."""


def validate_parameters(amount: str, tolerance: str, include_unlisted: str) -> tuple[Decimal, bool]:
    if not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", amount) or not 1 <= Decimal(amount) <= MAX_AMOUNT:
        raise AllocationInputError("Amount must be ₹1 to ₹10 crore, with up to two decimal places and no commas.")
    if tolerance not in PROFILES:
        raise AllocationInputError("Risk tolerance must be conservative, balanced or growth.")
    if include_unlisted not in ("true", "false"):
        raise AllocationInputError("include_unlisted must be true or false.")
    return Decimal(amount).quantize(PAISE), include_unlisted == "true"


def _money(value: Decimal) -> Decimal:
    # Flooring reported modeled loss to paise keeps rounded totals within the stress limit.
    return value.quantize(PAISE, rounding=ROUND_DOWN)


def _price(value) -> Decimal | None:
    try:
        price = Decimal(str(value))
    except InvalidOperation:
        return None
    if price.is_finite() and 0 < price <= MAX_AMOUNT and price.quantize(PAISE) == price:
        return price.quantize(PAISE)
    return None


def _quote(instrument: dict) -> Decimal | None:
    quote = instrument.get("quote", {})
    return _price(quote.get("price_inr")) if quote.get("state") == "reported" else None


def _listed_inputs(instruments: list[dict]) -> dict[str, dict]:
    by_id = {instrument["id"]: instrument for instrument in instruments}
    inputs = {}
    for instrument_id, (band, floor) in INSTRUMENTS.items():
        asset = by_id[instrument_id]
        if instrument_id == "FRSB2020T":
            liquidity = asset["liquidity"]
            price = _price(liquidity.get("face_value_inr")) if liquidity["state"] == "locked" else None
            loss, basis = Decimal(0), "assumed_principal_held"
        else:
            price = _quote(asset)
            history = asset["history"]
            loss, basis = Decimal(floor), "scenario_floor"
            if history["state"] == "ok":
                observed = -Decimal(str(history["max_drawdown_pct"]))
                if observed >= loss:
                    loss, basis = observed, "sampled_drawdown"
        inputs[instrument_id] = {"id": instrument_id, "name": asset["name"], "risk_band": band, "unit_price_inr": price,
                                 "price_as_of": asset.get("quote", {}).get("as_of"), "loss_pct": loss, "loss_basis": basis}
    return inputs


def _unlisted_input(company: dict, include: bool, amount: Decimal, policy: dict) -> dict:
    quote = _quote(company)
    lot = company["liquidity"].get("lot_shares")
    valid_lot = type(lot) is int and lot > 0
    lot_cost = quote * lot if quote is not None and valid_lot else None
    is_exchange = company["business_model"] == "exchange"
    limits = {
        "holding_cap": _money(amount * policy["unlisted_cap_pct"] / 100),
        "stress_budget": _money(amount * policy["max_loss_pct"] / UNLISTED_LOSS_PCT),
    }
    if is_exchange:
        limits["exchange_cap"] = _money(amount * EXCHANGE_CAP_PCT / 100)
    limit = min(limits.values())
    lots = int(limit // lot_cost) if include and lot_cost else 0
    if not include:
        state = "excluded"
    elif quote is None:
        state = "quote_unavailable"
    elif not valid_lot:
        state = "lot_unavailable"
    elif not lots:
        state = "minimum_lot_exceeds_limit"
    else:
        state = "allocated"
    return {"id": company["id"], "name": company["name"], "state": state, "is_exchange": is_exchange,
            "quote_state": company["quote"]["state"], "status_note": company.get("status_note"),
            "price_as_of": company["quote"].get("as_of"), "unit_price_inr": quote, "lot_shares": lot if valid_lot else None,
            "min_lot_inr": lot_cost, "min_lot_weight_pct": (lot_cost * 100 / amount).quantize(PAISE, rounding=ROUND_HALF_UP)
            if lot_cost else None, "limits_inr": limits, "effective_limit_inr": limit, "lots": lots,
            "amount_inr": lot_cost * lots if lot_cost else Decimal("0.00")}


def _weight_holdings(holdings: list[dict], amount: Decimal) -> dict:
    """Distribute display rounding across weights so the holdings and risk mix add to 100%."""
    shares = [row["amount_inr"] * 10000 / amount for row in holdings]
    basis_points = [int(share) for share in shares]
    by_remainder = sorted(range(len(holdings)), key=lambda i: shares[i] - basis_points[i], reverse=True)
    for i in by_remainder[:10000 - sum(basis_points)]:
        basis_points[i] += 1
    mix = {band: {"amount_inr": Decimal("0.00"), "weight_pct": Decimal("0.00")} for band in ("low", "medium", "high")}
    for row, bp in zip(holdings, basis_points):
        row["weight_pct"] = Decimal(bp).scaleb(-2)
        group = mix[row["risk_band"]]
        group["amount_inr"] += row["amount_inr"]
        group["weight_pct"] += row["weight_pct"]
    return mix


def _allocate(inputs: dict[str, dict], amount: Decimal, policy: dict, unlisted: dict | None,
              reserve: Decimal = Decimal(0)) -> dict:
    unlisted_amount = unlisted["amount_inr"] if unlisted else Decimal("0.00")
    exchange_unlisted = unlisted_amount if unlisted and unlisted["is_exchange"] else Decimal("0.00")
    exchange_limit = _money(amount * EXCHANGE_CAP_PCT / 100)
    focus_listed = unlisted and unlisted.get("listing") == "listed"
    shock_rate = Decimal(30) if focus_listed else UNLISTED_SHOCK_PCT
    haircut_rate = Decimal(0) if focus_listed else EXIT_HAIRCUT_PCT
    shock = unlisted_amount * shock_rate / 100
    haircut = (unlisted_amount - shock) * haircut_rate / 100
    budget = amount * policy["max_loss_pct"] / 100

    targets = {asset_id: (amount - unlisted_amount - reserve) * policy["targets"][asset_id] / 100
               if asset["unit_price_inr"] else Decimal(0) for asset_id, asset in inputs.items()}
    if focus_listed and unlisted_amount and unlisted["id"].upper().removeprefix("NSE-") in targets:
        targets[unlisted["id"].upper().removeprefix("NSE-")] = Decimal(0)
    exchange_target = targets["MCX"]
    targets["MCX"] = min(exchange_target, exchange_limit - exchange_unlisted)
    proposed_loss = sum(target * inputs[asset_id]["loss_pct"] / 100 for asset_id, target in targets.items())
    scale = min(Decimal(1), (budget - shock - haircut) / proposed_loss) if proposed_loss else Decimal(1)

    positions = {}
    for asset_id, asset in inputs.items():
        price = asset["unit_price_inr"]
        target = targets[asset_id]
        budgeted = target if asset_id == "FRSB2020T" else target * scale
        units = int(budgeted // price) if price else 0
        cost = price * units if price else Decimal("0.00")
        flag = "allocated" if units else "below_unit_size" if price else "input_unavailable"
        positions[asset_id] = {**asset, "status": flag, "target_pct": policy["targets"][asset_id], "units": units,
                               "amount_inr": cost, "stress_loss_inr": _money(cost * asset["loss_pct"] / 100)}
    holdings = list(positions.values())
    if unlisted:
        holdings.append({"id": unlisted["id"], "name": unlisted["name"], "risk_band": "high",
                         "status": unlisted["state"], "units": unlisted["lots"] * (unlisted["lot_shares"] or 0),
                         "unit_price_inr": unlisted["unit_price_inr"], "price_as_of": unlisted["price_as_of"],
                         "amount_inr": unlisted_amount,
                         "loss_pct": shock_rate + (100 - shock_rate) * haircut_rate / 100,
                         "loss_basis": "scenario_floor" if focus_listed else "assumed_shock_then_exit_haircut",
                         "stress_loss_inr": _money(shock) + _money(haircut)})
    remaining = amount - sum(row["amount_inr"] for row in holdings)
    holdings.append({"id": "CASH", "name": "Unallocated cash", "risk_band": "low", "status": "residual",
                     "amount_inr": remaining, "loss_pct": Decimal(0), "loss_basis": "assumed_cash_par",
                     "stress_loss_inr": Decimal("0.00")})
    mix = _weight_holdings(holdings, amount)
    loss = sum(row["stress_loss_inr"] for row in holdings)
    exchange_amount = positions["MCX"]["amount_inr"] + exchange_unlisted
    return {"holdings": holdings, "risk_mix": mix, "stress_loss_inr": loss,
            "stress_loss_pct": (loss * 100 / amount).quantize(PAISE, rounding=ROUND_HALF_UP),
            "unlisted_shock_loss_inr": _money(shock), "unlisted_exit_haircut_loss_inr": _money(haircut),
            "exchange_exposure_inr": exchange_amount, "exchange_limit_inr": exchange_limit,
            "exchange_cap_applied": targets["MCX"] < exchange_target,
            "restricted_capital_inr": positions["FRSB2020T"]["amount_inr"] + (Decimal(0) if focus_listed else unlisted_amount),
            "listed_target_scale_pct": (scale * 100).quantize(PAISE, rounding=ROUND_HALF_UP),
            "stress_budget_applied": scale < 1}


def allocate(snapshot: dict, amount: Decimal, tolerance: str, company_id: str, include_unlisted: bool) -> dict:
    company = next((item for item in snapshot["unlisted"] if item["id"] == company_id), None)
    if company is None:
        raise AllocationInputError("Choose an unlisted company from the portfolio lab.")
    policy = PROFILES[tolerance]
    inputs = _listed_inputs(snapshot["instruments"])
    unlisted = _unlisted_input(company, include_unlisted, amount, policy)
    baseline = _allocate(inputs, amount, policy, None)
    scenario = _allocate(inputs, amount, policy, unlisted)
    return {
        "method_version": METHOD_VERSION, "build_id": snapshot["build_id"], "data_as_of": snapshot["as_of"],
        "market_date": snapshot["market_date"], "mode": "illustrative", "amount_inr": amount,
        "tolerance": tolerance, "include_unlisted": include_unlisted, "unlisted": unlisted,
        "policy": {"targets_pct": policy["targets"], "unlisted_cap_pct": policy["unlisted_cap_pct"],
                   "exchange_cap_pct": EXCHANGE_CAP_PCT, "max_loss_pct": policy["max_loss_pct"],
                   "max_loss_inr": _money(amount * policy["max_loss_pct"] / 100),
                   "unlisted_shock_pct": UNLISTED_SHOCK_PCT, "exit_haircut_pct": EXIT_HAIRCUT_PCT,
                   "unlisted_combined_loss_pct": UNLISTED_LOSS_PCT},
        "baseline": baseline, "scenario": scenario,
    }


def _close(snapshot: dict, instrument: dict) -> Decimal | None:
    as_of = instrument.get("quote", {}).get("as_of")
    return _quote(instrument) if as_of and as_of == snapshot.get("market_date") else None


def _turnover_limit(row: dict, market_date: str | None) -> Decimal | None:
    value = row.get("turnover_lacs")
    if value is None or row.get("as_of") != market_date:
        return None
    return _money(Decimal(str(value)) * 100000 * TURNOVER_PARTICIPATION_PCT / 100)


def _workspace_inputs(snapshot: dict, horizon: int) -> dict:
    instruments = {row["id"]: row for row in snapshot["instruments"]}
    inputs = _listed_inputs(snapshot["instruments"])
    for key, row in inputs.items():
        asset = instruments[key]
        row["kind"] = asset.get("kind", "listed_equity")
        row["liquidity_limit_inr"] = _turnover_limit(asset.get("liquidity", {}), snapshot.get("market_date"))
        row["history"] = snapshot.get("listed_history", {}).get(key, {}).get("history", asset.get("history", {}))
        if key == "FRSB2020T":
            row["kind"] = "sovereign_bond"
            row["unit_price_inr"] = row["unit_price_inr"] if horizon >= 84 else None
            coupon = asset.get("coupon", {})
            row["coupon_rate"] = coupon.get("rate_pct_pa") if coupon.get("state") == "reported" else None
            row["coupon_as_of"] = coupon.get("from") if row["coupon_rate"] is not None else None
        else:
            row["unit_price_inr"] = _close(snapshot, asset)
    inputs["GOLDBEES"]["kind"] = "gold_etf"
    inputs["MCX"]["kind"] = "high_volatility_equity"
    for asset in snapshot.get("workspace_instruments", []):
        if asset["id"] != "LIQUIDBEES":
            continue
        liquidity = asset["liquidity"]
        cap = _turnover_limit(liquidity, snapshot.get("market_date"))
        inputs["LIQUIDBEES"] = {
            "id": "LIQUIDBEES", "name": asset["name"], "kind": "money_market_etf", "risk_band": "low",
            "unit_price_inr": _close(snapshot, asset) if liquidity.get("lot_verified") and cap else None,
            "price_as_of": asset.get("quote", {}).get("as_of"), "loss_pct": LIQUID_SHOCK_PCT,
            "loss_basis": "scenario_floor", "liquidity_limit_inr": cap, "history": asset["history"],
        }
    return inputs


def _workspace_position(asset: dict, target: Decimal) -> dict:
    price = asset["unit_price_inr"]
    cap = asset["liquidity_limit_inr"]
    eligible = target if cap is None else min(target, cap)
    units = int(eligible // price) if price and eligible > 0 else 0
    cost = units * price if price else Decimal(0)
    return {**asset, "units": units, "amount_inr": _money(cost),
            "stress_loss_inr": _money(cost * asset["loss_pct"] / 100),
            "status": "allocated" if units else "below_unit_size" if price else "input_unavailable"}


def _workspace_allocate(inputs: dict, amount: Decimal, reserve: Decimal, tolerance: str, horizon: int,
                        focus: dict | None) -> dict:
    policy = PROFILES[tolerance]
    loss_budget = amount * policy["max_loss_pct"] / 100
    focus_amount = focus["amount_inr"] if focus else Decimal(0)
    focus_loss = focus_amount * focus["loss_pct"] / 100 if focus else Decimal(0)
    focus_exchange = focus_amount if focus and focus["is_exchange"] else Decimal(0)
    exchange_limit = _money(amount * EXCHANGE_CAP_PCT / 100)
    liquid = inputs.get("LIQUIDBEES")
    liquid_floor = liquid["loss_pct"] if liquid and liquid["unit_price_inr"] else Decimal(0)

    sleeve = amount - reserve - focus_amount
    profile = WORKSPACE_TARGETS[tolerance]
    bond = _workspace_position(inputs["FRSB2020T"], sleeve * profile["FRSB2020T"] / 100)
    investable = sleeve - bond["amount_inr"]
    # Shorter horizons shrink risky target bands. Lower-risk holdings take up the balance.
    horizon_scale = Decimal("0.50") if horizon <= 12 else Decimal("0.75") if horizon < 36 else Decimal(1)
    targets = {}
    for key in ("HDFCBANK", "GOLDBEES", "MCX"):
        asset = inputs[key]
        duplicate = focus and focus.get("symbol") == key
        target = sleeve * profile[key] * horizon_scale / 100 if asset["unit_price_inr"] and not duplicate else Decimal(0)
        targets[key] = min(target, asset["liquidity_limit_inr"]) if asset["liquidity_limit_inr"] is not None else target
    exchange_target = targets["MCX"]
    targets["MCX"] = min(exchange_target, exchange_limit - focus_exchange)
    # Reserve stress for a liquid completion sleeve before increasing risk exposure.
    excess_loss = sum(target * (inputs[key]["loss_pct"] - liquid_floor) / 100 for key, target in targets.items())
    capacity = max(Decimal(0), loss_budget - focus_loss - investable * liquid_floor / 100)
    scale = min(Decimal(1), capacity / excess_loss) if excess_loss else Decimal(1)
    holdings = [bond, *[_workspace_position(inputs[key], target * scale) for key, target in targets.items()]]
    if focus:
        holdings.append({"id": focus["id"], "name": focus["name"], "risk_band": focus["risk_band"],
                         "kind": focus["kind"], "status": "allocated", "units": focus["lots"] * focus["lot_shares"],
                         "unit_price_inr": focus["unit_price_inr"], "price_as_of": focus["price_as_of"],
                         "amount_inr": focus_amount, "loss_pct": focus["loss_pct"], "loss_basis": focus["loss_basis"],
                         "stress_loss_inr": _money(focus_loss), "history": focus["history"],
                         "downside_exit_haircut_pct": EXIT_HAIRCUT_PCT if focus["listing"] == "unlisted" else Decimal(0)})

    cash = amount - sum(row["amount_inr"] for row in holdings)
    headroom = max(Decimal(0), loss_budget - sum(row["amount_inr"] * row["loss_pct"] / 100 for row in holdings))
    if liquid and liquid["unit_price_inr"]:
        completion = _workspace_position(liquid, min(cash - reserve, headroom * 100 / LIQUID_SHOCK_PCT))
        cash -= completion["amount_inr"]
        holdings.insert(0, completion)
        residual_reason = ("liquidity_cap" if completion["amount_inr"] + liquid["unit_price_inr"] > liquid["liquidity_limit_inr"]
                           else "stress_cap" if (completion["amount_inr"] + liquid["unit_price_inr"]) * LIQUID_SHOCK_PCT / 100 > headroom
                           else "whole_units")
    else:
        residual_reason = "liquid_input_unavailable"
    holdings.append({"id": "CASH", "name": "Cash", "kind": "cash", "risk_band": "low", "status": "residual",
                     "amount_inr": cash, "loss_pct": Decimal(0), "stress_loss_inr": Decimal(0)})
    mix = _weight_holdings(holdings, amount)
    loss = sum(row["stress_loss_inr"] for row in holdings)
    mcx = next(row for row in holdings if row["id"] == "MCX")
    return {"holdings": holdings, "risk_mix": mix, "stress_loss_inr": loss,
            "stress_loss_pct": (loss * 100 / amount).quantize(PAISE, rounding=ROUND_HALF_UP),
            "exchange_exposure_inr": mcx["amount_inr"] + focus_exchange, "exchange_limit_inr": exchange_limit,
            "exchange_cap_applied": targets["MCX"] < exchange_target, "stress_budget_applied": scale < 1,
            "cash_inr": cash, "invested_inr": amount - cash, "unspent_inr": cash - reserve,
            "cash_reason": residual_reason if cash > reserve else None,
            "restricted_capital_inr": bond["amount_inr"] + (focus_amount if focus and focus["listing"] == "unlisted" else 0),
            "returns": return_scenarios(holdings, amount, horizon)}


def workspace_scenario(snapshot: dict, catalog: list[dict], request: dict) -> dict:
    amount, include = validate_parameters(request.get("amount", "1000000"), request.get("tolerance", "balanced"),
                                          request.get("include_unlisted", "true"))
    tolerance = request.get("tolerance", "balanced")
    fields = {}
    for key, default, low, high in (("horizon", "36", 1, 120), ("cash_reserve", "0", 0, 90)):
        value = request.get(key, default)
        if not re.fullmatch(r"[0-9]{1,3}", value) or not low <= int(value) <= high:
            raise AllocationInputError(f"{key.replace('_', ' ').capitalize()} must be {low} to {high}.")
        fields[key] = int(value)
    horizon, reserve_pct = fields["horizon"], fields["cash_reserve"]
    reserve = _money(amount * reserve_pct / 100)
    policy = PROFILES[tolerance]
    rows = {row["id"]: row for row in catalog}
    named = request.get("company", "")
    shortlist = list(dict.fromkeys(filter(None, request.get("shortlist", "").split(","))))
    if len(shortlist) > 20 or any(not re.fullmatch(r"[a-z0-9-]{1,80}", key) for key in [*shortlist, *([named] if named else [])]):
        raise AllocationInputError("Choose up to 20 identified companies.")
    unlisted_rows = {row["id"]: row for row in snapshot["unlisted"]}
    inputs = _workspace_inputs(snapshot, horizon)

    def evaluate(key):
        row = rows.get(key)
        label = row["name"] if row else key
        listing = row["identity"]["listing"] if row else "unknown"
        candidate = {"id": key, "name": label, "listing": listing, "state": "quote_unavailable",
                     "amount_inr": Decimal(0), "lots": 0, "is_exchange": False, "risk_band": "high",
                     "kind": "unlisted_equity", "loss_pct": UNLISTED_LOSS_PCT,
                     "loss_basis": "assumed_shock_then_exit_haircut", "history": {"state": "no_verified_trade_series"}}
        if listing == "unlisted" and key in unlisted_rows:
            eligible = include and horizon >= 36
            candidate.update(_unlisted_input(unlisted_rows[key], eligible, amount, policy))
            if not eligible:
                candidate["state"] = "liquidity_horizon" if include else "excluded"
            if re.search(r"delist|suspend|illiquid", candidate.get("status_note") or "", re.I):
                candidate.update(state="listing_issue", amount_inr=Decimal(0), lots=0)
        elif listing == "listed" and row["model"] == "unknown":
            candidate["state"] = "sector_unclassified"
        elif (listing == "listed" and row.get("quote_as_of") and snapshot.get("market_date")
              and row["quote_as_of"][:10] != snapshot["market_date"]):
            candidate["state"] = "quote_stale"
        elif listing == "listed" and row["price_inr"] and row.get("quote_as_of") and row["coverage"] == "annual":
            symbol = row["identity"].get("symbol") or key.upper().removeprefix("NSE-")
            retained = snapshot.get("listed_history", {}).get(symbol, {})
            history = retained.get("history", {"state": "insufficient_history"})
            input_asset = inputs.get(symbol, {})
            floor = input_asset.get("loss_pct", Decimal(30))
            observed = -Decimal(str(history.get("max_drawdown_pct", 0))) if history["state"] == "ok" else Decimal(0)
            loss = max(floor, observed)
            high_risk = row["model"] == "exchange" or Decimal(str(history.get("ann_vol_pct") or 0)) >= 35 or loss >= 40
            candidate.update(symbol=symbol, risk_band="high" if high_risk else "medium",
                             kind="high_volatility_equity" if high_risk else "listed_equity", history=history, loss_pct=loss,
                             loss_basis="sampled_drawdown" if observed >= floor else "scenario_floor")
            wrapped = {"id": key, "name": label, "business_model": row["model"], "liquidity": {"lot_shares": 1},
                       "quote": {"state": "reported", "price_inr": row["price_inr"], "as_of": row.get("quote_as_of")}}
            candidate.update(_unlisted_input(wrapped, True, amount, policy))
            if price := candidate["unit_price_inr"]:
                cap = _turnover_limit(retained.get("liquidity", {}), snapshot.get("market_date"))
                limits = candidate["limits_inr"]
                limits["stress_budget"] = _money(amount * policy["max_loss_pct"] / loss)
                if cap is not None:
                    limits["turnover_cap"] = cap
                limit = min(limits.values())
                lots = int(limit // price)
                candidate.update(effective_limit_inr=limit, lots=lots, amount_inr=lots * price,
                                 state="allocated" if lots else "minimum_lot_exceeds_limit")
        if candidate["state"] == "allocated" and candidate["amount_inr"] > amount - reserve:
            limit = amount - reserve
            lots = int(limit // candidate["min_lot_inr"])
            candidate["limits_inr"]["cash_reserve_limit"] = limit
            candidate.update(amount_inr=lots * candidate["min_lot_inr"], lots=lots, effective_limit_inr=limit,
                             state="allocated" if lots else "cash_reserve_limit")
        return candidate

    evaluated = [evaluate(key) for key in shortlist]
    eligible = [candidate for candidate in evaluated if candidate["state"] == "allocated"]
    focus = evaluate(named) if named else min(eligible, key=lambda item: (item["listing"] != "listed", item["loss_pct"]), default=None)
    baseline = _workspace_allocate(inputs, amount, reserve, tolerance, horizon, None)
    allocated_focus = focus if focus and focus["state"] == "allocated" else None
    scenario = _workspace_allocate(inputs, amount, reserve, tolerance, horizon, allocated_focus) if allocated_focus else baseline
    for candidate in evaluated:
        if candidate["state"] == "allocated":
            candidate["selection"] = "chosen" if focus and focus["id"] == candidate["id"] else "alternate"
    return {"method_version": "2.1", "build_id": snapshot["build_id"], "amount_inr": amount, "reserve_inr": reserve, "horizon_months": horizon,
            "tolerance": tolerance, "focus": focus, "candidates": evaluated, "baseline": baseline, "scenario": scenario,
            "market_date": snapshot["market_date"], "max_loss_pct": policy["max_loss_pct"],
            "notes": [
                "Risk-profile targets for the bank, gold and exchange sleeves are reduced at shorter horizons and scaled down if they exceed the stress budget. Whole Liquid BeES units fill the remainder when dated price, lot and turnover are available.",
                "The model limits a position to 1% of observed daily turnover when available. Check live spreads, depth, settlement, fees and taxes before trading.",
                "The sovereign floating-rate bond has a seven-year term and no secondary market. It enters at 84 months or longer.",
                "The model considers one shortlist holding and prefers a listed candidate, then lower modeled stress loss. List order breaks ties.",
                "An off-exchange holding needs a 36-month liquidity planning window in this model. Its stress assumes a 35% price drop followed by a 25% exit haircut. Check dealer terms and the ability to find a buyer independently.",
            ]}
