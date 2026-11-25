"""Build reviewed peer cohorts and same-period operating comparisons."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from . import metrics as M
from .parse_screener import parse_screener

KNOWN_BASES = {"standalone", "consolidated"}
IST = timezone(timedelta(hours=5, minutes=30))
FIELDS = ("revenue_ops", "other_income", "other_gains", "job_work_revenue", "pat", "pbt", "finance_cost", "total_assets", "eps")

# Judgments based on the retained company profiles and IGX's issuer notes.
# True indicates a shared operating model suitable for the narrow metrics below.
REVIEWED = {
    "igx": {
        "IEX": (True, "Runs a fee-earning electronic electricity exchange. Its standalone statement is the operating reference, and it remains an IGX investor."),
        "MCX": (True, "Runs a fee-earning commodity derivatives exchange. Product and settlement exposures differ from IGX’s physical gas market."),
        "BSE": (False, "Runs securities and derivatives markets. Its product and revenue mix make it broader market-infrastructure context."),
        "CDSL": (False, "Earns depository and account-service fees. Custody economics differ from a gas trading venue."),
    },
    "ncdex": {
        "MCX": (True, "Both operate commodity derivatives markets. NCDEX is agriculture-led, while MCX has greater metal and energy exposure."),
        "IEX": (False, "Power trading provides exchange-fee context. Physical electricity contracts differ from agricultural futures."),
        "BSE": (False, "Securities and financial derivatives dominate its market mix."),
    },
    "hpx": {
        "IEX": (True, "Both run power exchanges with physical delivery in traded electricity products."),
        "MCX": (False, "Its commodity futures provide energy-market context with different settlement economics."),
    },
    "msei": {
        "BSE": (True, "Both provide listed securities markets. Trading scale, activity and mix differ."),
        "MCX": (False, "Its commodity futures and options provide exchange infrastructure context."),
    },
    "icex": {
        "MCX": (False, "Both have a commodity-derivatives history. ICEX operating continuity and a comparable trading period need verification."),
    },
    "herofincorp": {
        "BAJFINANCE": (True, "Both lend to retail and business borrowers. Consumer product and fee mixes differ."),
        "CHOLAFIN": (True, "Both lend to vehicle and business customers. Secured lending and funding mixes differ."),
        "LTF": (True, "Both offer diversified retail lending. The product mix and secured share differ."),
    },
    "hdfcsec": {
        "ANGELONE": (True, "Retail securities broking and related financial services overlap. Digital and bank distribution differ."),
        "MOTILALOFS": (False, "The group adds asset management, wealth and housing finance to broking."),
    },
    "sbigeneral": {
        "ICICIGI": (True, "Both write multiple lines of general insurance. Underwriting mix affects profitability."),
        "GODIGIT": (True, "Both write general insurance. Motor concentration and distribution differ."),
    },
    "orbis": {
        "CDSL": (False, "Securities infrastructure overlaps. Its core depository role differs from institutional custody and clearing."),
        "CAMS": (False, "Fund infrastructure overlaps. Registrar and transfer-agent fees differ from custody and clearing fees."),
    },
    "pharmeasy": {
        "MEDPLUS": (False, "Shares pharmacy distribution exposure. Its store-led retail model differs from PharmEasy’s online pharmacy and diagnostics mix."),
    },
    "polymatech": {
        "MOSCHIP": (False, "Provides semiconductor design and engineering services. Its service economics differ from optical chip manufacturing."),
        "KAYNES": (False, "Provides electronics manufacturing services and has a packaging initiative. Its broad assembly mix differs from optical chip production."),
    },
    "capgemini": {
        "LTM": (True, "IT consulting and outsourced delivery overlap. Customer sectors and service mix differ."),
        "MPHASIS": (True, "Both provide IT services and outsourcing. Banking exposure and geographic mix differ."),
    },
    "pharmed": {
        "ALKEM": (True, "Domestic branded formulations overlap. Alkem also has substantial international operations."),
        "IPCALAB": (True, "Both sell branded formulations. Ipca also has API and international businesses."),
    },
    "grouppharma": {
        "COLPAL": (False, "Oral care is shared. Mass-market consumer distribution differs from specialty dental formulations."),
    },
    "cial": {
        "GMRAIRPORT": (True, "Both operate airports with aeronautical and commercial revenue. One listed group spans multiple airports and concessions, which affects scale and financing."),
    },
    "kial": {
        "GMRAIRPORT": (True, "Both operate airports. Kannur is a single airport and the listed group includes multiple concessions and non-aeronautical activities."),
    },
    "indiacarbon": {
        "GOACARBON": (True, "Manufactures and sells calcined petroleum coke to industrial users, India Carbon’s core product."),
        "PCBL": (False, "Manufactures carbon black and specialty chemicals. Carbon black has different products, customers and pricing drivers."),
        "RAIN": (False, "Includes petroleum coke in a diversified carbon, cement and advanced-materials group. Its annual statements close in December."),
    },
    "haldia": {
        "RELIANCE": (False, "Petrochemicals overlap inside a group with major refining, telecom and retail businesses."),
        "SPLPETRO": (False, "Both manufacture petrochemicals. Supreme Petrochem's styrenics focus differs from Haldia's integrated olefins and polymers."),
    },
    "nayara": {
        "MRPL": (True, "Both operate refineries. Product mix, crude sourcing and branded retail exposure differ."),
        "CHENNPETRO": (True, "Both operate refineries. Chennai Petroleum has a different distribution structure and refinery mix."),
    },
    "reliance-retail": {
        "DMART": (True, "Store-led grocery and general merchandise overlap. Reliance Retail has a wider format mix."),
        "TRENT": (False, "Fashion retail overlaps with one part of Reliance Retail. Trent's consolidated mix is different."),
    },
    "oyo": {
        "EASEMYTRIP": (False, "Both reach travellers online. Booking commissions differ from hotel franchise and property services."),
        "INDHOTEL": (False, "Both have hotel exposure. The mix of managed and owned hotels differs from OYO's platform model."),
    },
    "csk": {},
    "axlesindia": {
        "AUTOAXLES": (True, "Commercial-vehicle axles and supplier exposure overlap. Axles India includes axle housings and the listed firm sells assemblies."),
        "GNA": (False, "Both serve drivetrain customers. Forged axle shafts differ from fabricated axle housings."),
    },
    "gkndriveline": {
        "GNA": (False, "Both sell drivetrain components. Axle shafts differ from constant-velocity joints and systems."),
        "AUTOAXLES": (False, "Automotive supplier exposure overlaps. Truck axle assemblies differ from passenger-vehicle driveline systems."),
    },
}

OPERATING_NOTES = {
    "igx": "Other income, settlement balances and product mix affect exchange comparisons. IEX has a promoter relationship with IGX.",
    "indiacarbon": "Both eligible companies reported a loss in the assessed year. Calcined petroleum coke exposure supports the operating comparison.",
    "cial": "Airport tariffs, traffic and duty-free sales contribute differently across airport groups. Concessions and financing can materially affect net profit.",
    "pharmed": "Branded formulations overlap, while exports, therapy mix and subsidiaries change the comparison.",
    "axlesindia": "Commercial vehicle production affects axle demand. Housings and completed assemblies carry different value per unit.",
}

def _source_for(evidence: dict) -> dict:
    return {key: evidence.get(key) for key in (
        "source", "url", "retrieved_at", "sha256", "capture_run", "file", "raw_label", "raw_text",
        "raw_unit", "period_label", "basis", "anchor", "components",
    )}


def _unlisted_annual(company: dict) -> tuple[str | None, str | None, dict, dict | None]:
    """Select the latest annual P&L and its accounting perimeter."""
    recon = company.get("reconciliation") or {}
    annual = company.get("peer_annual")
    if annual:
        return annual["period_end"], annual["basis"], annual["facts"], None
    scope = recon.get("operating_scope")
    statement = recon.get("selected", {}).get("statements", {}).get("income_statement", {})
    if scope and statement.get("title_confirmed") and statement.get("unit_text") == "Indian Rupees millions":
        periods = statement["lines"].get("revenue_ops", {}).get("values_inr_crore", {})
        if periods:
            period = max(periods)
            facts = {}
            for field in FIELDS:
                line = statement["lines"].get(field, {})
                value = line.get("values_inr_crore", {}).get(period)
                if value is None:
                    continue
                facts[field] = {
                    "value": value, "state": "reported", "basis": scope["basis"],
                    "evidence": {
                        "url": f"{recon['url']}#page={statement['page']}", "page": statement["page"],
                        "source": "IGX Restated Financial Information",
                        "retrieved_at": recon["retrieved_at"], "sha256": recon["sha256"],
                        "capture_run": recon["capture_run"], "file": recon["file"],
                        "raw_label": line["matched_text"], "raw_text": line["raw_values"][period],
                        "raw_unit": "INR/share" if field == "eps" else "INR million", "period_label": period,
                    },
                }
            return f"{period[2:]}-03-31", scope["basis"], facts, {
                **scope, "url": f"{recon['url']}#page={scope['scope_page']}",
                "relationship_url": f"{recon['url']}#page={scope['relationship_page']}",
            }

    period = next((p for p in reversed(company["periods"]) if p.startswith("FY") and not p.endswith("?")
                   and company["fields"]["revenue_ops"]["by_period"][p]["value"] is not None), None)
    if period is None:
        return None, None, {}, None
    facts = {}
    for field in FIELDS:
        cell = company["fields"][field]["by_period"][period]
        evidence = company["evidence"].get(cell.get("ev"))
        facts[field] = {"value": cell["value"], "state": cell["state"], "basis": evidence and evidence.get("basis"),
                        "evidence": _source_for(evidence) if evidence else None}
    return f"{period[2:]}-03-31", company["basis"], facts, None


def _fact_value(facts: dict, field: str, basis: str | None) -> Decimal | None:
    cell = facts.get(field, {})
    if basis is None or cell.get("basis") != basis or cell.get("state") not in ("reported", "explicit_zero", "derived"):
        return None
    value = M.dec(cell["value"])
    return value if value is not None and value.is_finite() else None


def _operating_metrics(facts: dict, basis: str | None) -> dict:
    revenue = _fact_value(facts, "revenue_ops", basis)
    pat = _fact_value(facts, "pat", basis)
    other = _fact_value(facts, "other_income", basis)
    gains = _fact_value(facts, "other_gains", basis)
    job_work = _fact_value(facts, "job_work_revenue", basis)
    non_operating = other + (gains or Decimal(0)) if other is not None else None
    income = (revenue + (job_work or Decimal(0)) + non_operating
              if revenue is not None and non_operating is not None else None)
    other_formula = "other income / (operating revenue + other income) x 100"
    if gains is not None or job_work is not None:
        other_formula = "(other income + other gains) / (operating revenue + job-work revenue + other income + other gains) x 100"
    return {
        "pat_to_revenue_pct": M.ratio(pat, revenue, "PAT / operating revenue x 100", ("pat", "revenue_ops"), "%", True),
        "other_income_share_pct": M.ratio(non_operating, income, other_formula,
                                          ("other_income_and_gains", "total_income"), "%", True),
    }


def _annual_pe(facts: dict, basis: str | None, price: dict | None, period: str | None, price_issue: str | None = None) -> dict:
    eps = _fact_value(facts, "eps", basis)
    pat = _fact_value(facts, "pat", basis)
    note = None
    state = "missing_input"
    if pat is None or eps is None:
        note = "Annual profit or EPS is unavailable on the assessed reporting basis."
    elif pat <= 0 or eps <= 0:
        state = "zero_denominator" if pat == 0 or eps == 0 else "negative_base"
        note = "Annual profit and EPS must both be positive."
    elif price_issue or not price or not period or price["date"] < period:
        note = price_issue or "A dated price on or after the assessed year-end is required."
    if note:
        result = M.result(None, state, "dated price / annual EPS", {"price_inr": price and price["value"], "eps": eps}, note, "x")
    else:
        result = M.pe(price["value"], eps)
    return {**result, "price": price, "period_end": period}


def _unlisted_price(company: dict) -> dict | None:
    quote = company["quote"]
    cap = company["valuation"]["market_cap"]
    if cap["state"] == "suspect_quote" or not quote["as_of"] or not quote["price_inr"] or M.dec(quote["price_inr"]) <= 0:
        return None
    stamp = datetime.fromisoformat(quote["as_of"]).astimezone(IST)
    return {"value": quote["price_inr"], "date": stamp.date().isoformat(), "kind": "indicative dealer quote",
            "evidence": _source_for(company["evidence"][quote["ev"]])}


def _listed_price(stock: dict | None) -> dict | None:
    if not stock or stock["state"] != "ok" or not stock["close"] or stock["close"] <= 0:
        return None
    return {
        "value": str(stock["close"]), "date": stock["date"], "kind": "NSE end-of-day close",
        "evidence": {**stock["source"], "anchor": {"symbol": stock["symbol"], "field": "Close Price"}},
    }


def _candidate(symbol: str, rule: tuple[bool, str], captures: dict, stock: dict | None, ref: dict) -> dict:
    fits, rationale = rule
    pages = {basis: captures.get(f"{symbol}-{basis}", {}) for basis in sorted(KNOWN_BASES)}
    basis = ref["comparison_basis"]
    preferred = pages.get(basis, {})
    usable = [p for p in pages.values() if p.get("state") == "ok"]
    page = preferred if preferred.get("state") == "ok" or not usable else usable[0]
    periods = sorted(date for date, rows in page.get("annual", {}).items()
                     if _fact_value(rows, "revenue_ops", page.get("basis")) is not None)
    period = ref["period_end"]
    observed = period if period in periods else periods[-1] if periods else None
    facts = page.get("annual", {}).get(observed, {})
    reasons = []
    if not fits:
        reasons.append("different_business_model")
    if not usable:
        reasons.append("capture_unavailable")
    if not period:
        reasons.append("issuer_period_unavailable")
    if not basis:
        reasons.append(ref.get("issuer_gap") or "issuer_basis_unverified")
    elif usable and preferred.get("state") != "ok":
        reasons.append("incompatible_reporting_basis")
    if usable and period and period not in periods:
        reasons.append("no_same_annual_period")
    if period in periods and page.get("basis") == basis and _fact_value(facts, "pat", basis) is None:
        reasons.append("annual_profit_unavailable")

    price = _listed_price(stock)
    price_issue = None
    if observed and price:
        if not ref["price"] or price["date"] != ref["price"]["date"]:
            price_issue = "The exchange close and issuer dealer quote require the same Indian calendar date."
        elif observed != periods[-1]:
            price_issue = "P/E requires the latest annual EPS on this page."
        elif any(observed < event["date"] <= price["date"] for event in stock.get("split_events", [])):
            price_issue = "A detected split after year-end requires a verified EPS adjustment."
    pe = (_annual_pe(facts, basis, price, observed, price_issue)
          if not reasons else M.result(None, "incompatible_peer", "dated price / annual EPS", {},
                                       "P/E is withheld for context-only or incompatible candidates.", "x"))
    return {
        "symbol": symbol, "name": page.get("name", symbol), "operating_fit": fits, "rationale": rationale,
        "status": "eligible" if not reasons else "context_only" if not fits and usable else "excluded",
        "reasons": reasons, "basis": page.get("basis"), "period_end": observed,
        "available_periods": periods, "source": page.get("source"), "profile_anchor": page.get("profile_anchor"),
        "facts": facts, "metrics": _operating_metrics(facts, basis) if not reasons else {}, "pe": pe,
    }

def _comparison_drivers(ref: dict, peers: list[dict]) -> dict:
    """Compare the first eligible peer in the reviewed business-fit order."""
    lead = next((peer for peer in peers if peer["status"] == "eligible"), None)
    if lead is None:
        return {}
    differences = {}
    for field in ("pat_to_revenue_pct", "other_income_share_pct"):
        left = M.dec(ref["metrics"][field]["value"])
        right = M.dec(lead["metrics"][field]["value"])
        if left is not None and right is not None:
            differences[field] = M.q(left - right, "0.01")
    return {"benchmark": lead["name"], "percentage_point_differences": differences}


def build_peers(companies: dict, items: dict, market: dict, fallbacks: list, build_id: str,
                default: str, domains: list, updates: dict, issuer_overrides: dict) -> dict:
    selected = [cid for domain in domains for cid in domain["companies"]]
    if len(selected) != len(set(selected)) or set(selected) != set(REVIEWED):
        raise ValueError("Each reviewed company must appear in exactly one demo domain")
    symbols = {symbol for candidates in REVIEWED.values() for symbol in candidates}
    parsed = {}
    for key, item in items.items():
        if item["symbol"] in symbols:
            try:
                parsed[key] = parse_screener(item)
            except OSError:
                # A selected file can disappear between snapshot selection and parsing.
                parsed[key] = {"state": "capture_unavailable"}
    reviewed_captures = {**parsed, **issuer_overrides}
    cohorts = {}
    stocks = {row["symbol"]: row for row in market.get("stocks", [])}
    for cid in selected:
        company = companies[cid]
        rules = REVIEWED[cid]
        if list(rules) != company["listed_peers"]:
            raise ValueError(f"Listed review and configured candidates disagree for {cid}")
        period, basis, facts, scope = _unlisted_annual(company)
        basis_key = scope["operating_comparison_basis"] if scope else basis if basis in KNOWN_BASES else None
        issuer_gap = None
        if basis_key and not all(_fact_value(facts, field, basis) is not None for field in ("revenue_ops", "pat")):
            basis_key = None
            issuer_gap = "issuer_inputs_unavailable"
        price = _unlisted_price(company)
        ref = {
            "id": cid, "name": company["name"], "short": company["short"], "market_status": company["market_status"],
            "hierarchy": company["hierarchy"], "period_end": period, "annual_source": (company.get("peer_annual") or {}).get("evidence"),
            "basis": basis, "comparison_basis": basis_key, "issuer_gap": issuer_gap, "scope": scope, "facts": facts, "price": price,
            "metrics": _operating_metrics(facts, basis if basis_key else None),
            "pe": _annual_pe(facts, basis if basis_key else None, price, period),
            "profile_source": _source_for(company["evidence"][company["profile"]["ev"]])
            if company["profile"]["ev"] else None,
        }
        candidates = [_candidate(sym, rule, reviewed_captures, stocks.get(sym), ref) for sym, rule in rules.items()]
        for peer in candidates:
            peer["updates"] = updates.get(peer["symbol"], [])
        cohorts[cid] = {**ref, "peers": candidates, "drivers": _comparison_drivers(ref, candidates),
                        "operating_note": OPERATING_NOTES.get(cid), "updates": updates.get(cid, []),
                        "news": company.get("news", {}).get("items", [])[:3]}
    return {
        "schema_version": 2, "build_id": build_id, "default": default, "domains": domains, "cohorts": cohorts,
        "capture_audit": {key: {k: v for k, v in page.items() if k != "annual"} for key, page in parsed.items()},
        "fallbacks": [item for item in fallbacks if item["item"].rsplit("-", 1)[0] in symbols],
    }
