"""Evaluate a bounded comparison language against the pipeline's company summary."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation
import operator
import re


FIELDS = {
    "market_cap_cr": ("Market capitalization", "₹ crore", ("Market cap",)),
    "pe": ("Price to earning", "×", ("P/E", "Price to earnings")),
    "pe_reported": ("Reported EPS multiple", "×", ("Reported P/E",)),
    "pe_proxy": ("Proxy EPS multiple", "×", ("Proxy P/E",)),
    "roce_pct": ("Return on capital employed", "%", ("ROCE",)),
    "pb": ("Price to book", "×", ("P/B",)),
    "ps": ("Price to sales", "×", ("P/S",)),
    "revenue_cr": ("Revenue", "₹ crore", ()),
    "pat_cr": ("Profit after tax", "₹ crore", ("PAT",)),
    "revenue_growth_pct": ("Revenue growth", "%", ()),
    "pat_margin_pct": ("PAT margin", "%", ()),
    "roe_pct": ("Return on equity", "%", ("ROE",)),
    "current_ratio": ("Current ratio", "×", ()),
    "quick_ratio": ("Quick ratio", "×", ()),
}
FIELD_NAMES = {
    name.casefold(): key
    for key, (label, _, aliases) in FIELDS.items()
    for name in (key, label, *aliases)
}
OPERATORS = {">": operator.gt, ">=": operator.ge, "<": operator.lt,
             "<=": operator.le, "=": operator.eq}
CONDITION = re.compile(
    r"([A-Za-z][A-Za-z_/ ]*?)\s*(>=|<=|>|<|=)\s*"
    r"([+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+))\s*(%?)"
)
MAX_QUERY_LENGTH = 500
MAX_CONDITIONS = 12


class QueryError(ValueError):
    """A query the user can correct."""


def parse_query(query: str) -> list[list[tuple[str, str, Decimal]]]:
    """Return OR groups of AND conditions, in order."""
    if len(query) > MAX_QUERY_LENGTH:
        raise QueryError(f"Use at most {MAX_QUERY_LENGTH} characters.")
    query = re.sub(r"^\s*SELECT\s+company\s+FROM\s+companies\s+WHERE\s+", "", query, count=1, flags=re.I)
    if not query.strip():
        raise QueryError("Enter a condition, for example Market capitalization > 500.")
    parts = re.split(r"\s+(AND|OR)\s+", " ".join(query.split()), flags=re.IGNORECASE)
    if len(parts[::2]) > MAX_CONDITIONS:
        raise QueryError(f"Use at most {MAX_CONDITIONS} conditions.")

    groups = [[]]
    for index, part in enumerate(parts[::2]):
        match = CONDITION.fullmatch(part)
        if match is None:
            raise QueryError(f"Condition {index + 1}: use a field, a comparison operator and a number.")
        label, op, number, suffix = match.groups()
        key = FIELD_NAMES.get(label.casefold())
        if key is None:
            raise QueryError(f"Unknown field “{label}”. See Fields and units.")
        if suffix and FIELDS[key][1] != "%":
            raise QueryError(f"{FIELDS[key][0]} uses {FIELDS[key][1]}. Remove the percent sign.")
        if index and parts[2 * index - 1].upper() == "OR":
            groups.append([])
        groups[-1].append((key, op, Decimal(number)))
    return groups


def _read_metric(metrics: dict, key: str) -> tuple[Decimal | None, str]:
    cell = metrics.get(key, {})
    state, raw = cell.get("state", "missing_input"), cell.get("value")
    if state != "ok":
        return None, state
    if raw is None:
        return None, "missing_input"
    try:
        value = Decimal(str(raw))
    except InvalidOperation:
        return None, "invalid_value"
    return (value, "ok") if value.is_finite() else (None, "invalid_value")


def _evaluate(groups: list, values: dict) -> bool | None:
    unresolved = False
    for conditions in groups:
        outcomes = [
            None if values[key] is None else OPERATORS[op](values[key], number)
            for key, op, number in conditions
        ]
        if False in outcomes:
            continue
        if None not in outcomes:
            return True
        unresolved = True
    return None if unresolved else False


def screen(groups: list, companies: list[dict], exclusions: dict) -> dict:
    columns = list(dict.fromkeys(key for group in groups for key, _, _ in group))
    counts = {key: Counter() for key in columns}
    matches, excluded = [], []
    no_match = unresolved = 0
    for company in companies:
        cid = company["id"]
        if cid in exclusions:
            excluded.append({"id": cid, "name": company["name"], **exclusions[cid]})
            continue

        values, states = {}, {}
        for key in columns:
            values[key], states[key] = _read_metric(company["metrics"], key)
            counts[key][states[key]] += 1
        outcome = _evaluate(groups, values)
        if outcome is True:
            matches.append({
                **{key: company.get(key) for key in ("id", "name", "short", "hierarchy",
                                                    "latest_period", "basis", "quote_as_of", "listing", "ipo_stage")},
                "metrics": {key: {"value": values[key], "state": states[key],
                                  **({"basis": company["metrics"][key]["basis"]}
                                     if company["metrics"].get(key, {}).get("basis") else {})}
                            for key in columns},
                "checks_flagged": company.get("checks_flagged", []),
            })
        elif outcome is None:
            unresolved += 1
        else:
            no_match += 1

    return {
        "fields": {key: {"label": label, "unit": unit, "aliases": aliases}
                   for key, (label, unit, aliases) in FIELDS.items()},
        "columns": columns,
        "matches": sorted(matches, key=lambda company: company["name"].casefold()),
        "no_match": no_match,
        "unresolved": unresolved,
        "evaluated": len(companies) - len(excluded),
        "excluded": excluded,
        "coverage": {key: {"available": states["ok"],
                           "gaps": {state: count for state, count in states.items() if state != "ok"}}
                     for key, states in counts.items()},
    }
