"""Parse captured WWIPL company pages into observations.

Each observation keeps the provider's raw label and raw text, the statement it came from,
the basis the provider states (or "unspecified"), the period, the unit, a value state and an
anchor (capture file + table/row index). Canonical field mapping is a separate, explicit step.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from bs4 import BeautifulSoup

# Value states kept distinct throughout the pipeline.
REPORTED, ZERO, DASH, BLANK, PROVIDER_ERROR, UNPARSED = (
    "reported", "explicit_zero", "dash", "blank", "provider_error", "unparsed")

STATEMENTS = [
    ("balance_sheet", re.compile(r"balance\s*sheet", re.I)),
    ("cash_flow", re.compile(r"cash\s*flow", re.I)),
    ("ratios", re.compile(r"ratio", re.I)),
    ("income_statement", re.compile(r"income statement|profit\s*(?:&|and)\s*loss|p&l", re.I)),
    ("summary", re.compile(r"summary", re.I)),
]

# Canonical field -> (statements to look in, list of raw-label regexes). First match wins.
CANONICAL = {
    "total_income": (("income_statement",), [r"^revenue$", r"^total income$"]),
    "revenue_ops": (("income_statement",), [r"^revenue from operations?$"]),
    "other_income": (("income_statement",), [r"^other income$"]),
    "other_gains": (("income_statement",), [r"^other gains\s*/\s*\(losses\)$"]),
    "job_work_revenue": (("income_statement",), [r"^revenue from job work$"]),
    "total_expenses": (("income_statement",), [r"^expenses$", r"^total expenses?$"]),
    "finance_cost": (("income_statement",), [r"^finance costs?$"]),
    "depreciation": (("income_statement",), [r"^depreciation"]),
    "pbt": (("income_statement",), [r"^profit\s*/?\s*\(loss\)\s*before tax", r"^profit before tax"]),
    "tax": (("income_statement",), [r"^tax expenses?$", r"^total tax expenses?$"]),
    "pat": (("income_statement",), [
        r"^(?:[IVX]+\. )?(?:Net )?(?:Profit\s*(?:/\s*)?(?:\(?Loss\)?\s*)?|Loss) (?:for the (?:period|year)|after tax)(?: \([IVX]+-[IVX]+\))?$",
        r"^profit(?:\s*/?\s*\(?\s*loss\s*\)?)?\s+for the (period|year) from continuing operations?$",
    ]),
    "pat_pre_associate": (("income_statement",), [r"^profit after tax before share of\s*profit from associate$"]),
    "pat_owners": (("income_statement",), [r"^attributable to owners of the company$"]),
    "associate_profit": (("income_statement",), [r"^share of profit/loss from associate$"]),
    "total_assets": (("balance_sheet", "summary"), [r"^assets$", r"^total assets$"]),
    "total_equity": (("balance_sheet",), [r"^total equity$"]),
    "total_liabilities": (("balance_sheet",), [r"^total liabilit"]),
    "current_assets": (("balance_sheet",), [r"^current assets$", r"^total current assets$"]),
    "current_liabilities": (("balance_sheet",), [r"^current liabilities$", r"^total current liabilities$"]),
    "noncurrent_assets": (("balance_sheet",), [r"^non\s*-?\s*current assets$"]),
    "noncurrent_liabilities": (("balance_sheet",), [r"^non\s*-?\s*current liabilities$"]),
    "inventories": (("balance_sheet",), [r"^inventor"]),
    "trade_receivables": (("balance_sheet",), [r"^trade receivables$"]),
    "trade_payables": (("balance_sheet",), [r"^trade payables$"]),
    "borrowings": (("balance_sheet",), [r"^total borrowings$", r"^total debt$"]),
    "fixed_assets": (("balance_sheet",), [r"^net fixed assets$", r"^property, plant and equipment$"]),
    "cost_of_sales": (("income_statement",), [r"^cost of (?:goods sold|sales)$"]),
    "gross_profit": (("income_statement",), [r"^gross profit$"]),
    "operating_profit": (("income_statement",), [r"^operating profit$"]),
    "dividend_per_share": (("income_statement", "summary"), [r"^dividend per share$"]),
    "cash": (("balance_sheet",), [r"^cash and cash equivalents?$"]),
    "loans": (("balance_sheet",), [r"^loans$", r"^loans and advances"]),
    "cfo": (("cash_flow",), [r"operating activities"]),
    "cfi": (("cash_flow",), [r"investing activities"]),
    "cff": (("cash_flow",), [r"financing activities"]),
    "ebitda": (("summary",), [r"^ebitda$"]),
    "eps": (("summary", "income_statement"), [r"^earnings per share", r"^basic$"]),
    "eps_basic": (("income_statement",), [r"^(?:a\) )?basic(?: \(rs\.\)| earnings per share| and diluted)?$"]),
    "eps_diluted": (("income_statement",), [r"^(?:b\) )?diluted(?: \(rs\.\)| earnings per share)?$", r"^basic and diluted$"]),
    "shares_outstanding": (("summary",), [r"^outstanding shares$"]),
    "gross_npa": (("balance_sheet", "ratios", "summary"), [r"gross\s+npa", r"gross non[- ]performing"]),
    "net_npa": (("balance_sheet", "ratios", "summary"), [r"net\s+npa", r"net non[- ]performing"]),
    "nim": (("ratios", "summary"), [r"^net interest margin"]),
    "provision_coverage": (("ratios", "summary"), [r"^provision coverage"]),
    "capital_adequacy": (("ratios", "summary"), [r"^capital adequacy"]),
    "claims_ratio": (("ratios", "summary"), [r"^incurred claims ratio"]),
    "combined_ratio": (("ratios", "summary"), [r"^combined ratio"]),
    "solvency_ratio": (("ratios", "summary"), [r"^solvency ratio"]),
}

OVERVIEW_FIELDS = {
    "EPS": "eps_ttm", "PE ratio": "pe_provider", "P/S Ratio": "ps_provider", "Market Capitalization": "mcap_provider",
    "Book value": "book_value_ps", "P/BV": "pb_provider", "52 Week High": "high_52w", "52 Week Low": "low_52w",
    "Lifetime High": "lifetime_high", "Lifetime Low": "lifetime_low", "DRHP Filed?": "drhp_filed", "Available on": "depository",
    "ROFR Require": "rofr", "Sector": "provider_sector", "CIN": "cin", "Registration Date": "registration_date",
    "No. of Outstanding Shares": "shares_fundamentals", "Face Value": "face_value", "ISIN No.": "isin", "Scrip Name": "scrip",
}


def parse_number(text: str) -> tuple[Decimal | None, str, str | None]:
    """Return (value, state, unit). Never guesses: unknown text is 'unparsed'."""
    t = (text or "").strip()
    if t == "":
        return None, BLANK, None
    if t in {"-", "--", "—", "NA", "N/A"}:
        return None, DASH, None
    if t.startswith("#"):
        return None, PROVIDER_ERROR, None
    unit = "%" if t.endswith("%") else None
    core = t.rstrip("%").replace(",", "").replace("Crore", "").replace("Cr", "").strip()
    neg = core.startswith("(") and core.endswith(")")
    core = core.strip("()")
    try:
        v = Decimal(core)
    except InvalidOperation:
        return None, UNPARSED, None
    if neg:
        v = -v
    return v, (ZERO if v == 0 else REPORTED), unit


UNIT_RX = re.compile(r"\((?:Rs\.?|In Rs\.?)\s*(?:in\s*)?(Crores?|Lakhs?|Thousands?|Millions?)\)", re.I)
SCALE_TO_CRORE = {"crore": Decimal(1), "lakh": Decimal("0.01"), "thousand": Decimal("0.0001"), "million": Decimal("0.1")}
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def normalise_period(label: str) -> str | None:
    """Map provider column labels to a period key.

    '2025-26' -> FY2026; '31-03-2026', '31-Mar-26', 'As at 31 March 2023', '31st March 2023' -> FY of a
    31 March year end; other explicit dates -> 'PE:YYYY-MM-DD'; a bare year '2023' -> 'FY2023?' (the
    trailing ? keeps the assumption visible).
    """
    s = re.sub(r"^(as at|as on)\s+", "", label.strip(), flags=re.I)
    m = re.fullmatch(r"(\d{4})\s*-\s*(\d{2})", s)
    if m:
        return f"FY{int(m.group(1)) + 1}"
    m = re.fullmatch(r"(\d{1,2})-(\d{2})-(\d{4})", s)
    if m:
        d, mo, y = m.groups()
        return f"FY{y}" if (int(d), mo) == (31, "03") else f"PE:{y}-{mo}-{int(d):02d}"
    m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?[ -]([A-Za-z]{3,9})[ ,-]*(\d{2,4})", s)
    if m:
        d, mon, y = int(m.group(1)), MONTHS.get(m.group(2)[:3].lower()), int(m.group(3))
        y = y + 2000 if y < 100 else y
        if mon is None:
            return None
        return f"FY{y}" if (d, mon) == (31, 3) else f"PE:{y}-{mon:02d}-{d:02d}"
    m = re.fullmatch(r"(?:FY\s*)?(\d{4})", s, re.I)
    if m:
        return f"FY{m.group(1)}?"
    return None


def _statement_for(heading: str, first_labels: list[str]) -> str | None:
    ratio_like = sum(1 for l in first_labels if re.search(r"ratio|margin|return on", l, re.I))
    found = next((name for name, rx in STATEMENTS if rx.search(heading)), None)
    # A ratio table sometimes sits under the previous statement's heading (seen on India Carbon).
    if first_labels and ratio_like >= max(3, len(first_labels) // 2) and found in (None, "cash_flow", "ratios"):
        return "ratios"
    return found


def _basis_for(heading: str) -> str:
    h = heading.lower()
    if "consolidated" in h:
        return "consolidated"
    if "standalone" in h:
        return "standalone"
    return "unspecified"


def _heading_for(table) -> str:
    stmt_rx = re.compile(r"balance sheet|profit|loss|cash ?flow|ratio|summary|income statement", re.I)
    b = table.find_previous(["b", "strong"])
    if b is not None and stmt_rx.search(b.get_text(" ", strip=True)):
        return " ".join(b.get_text(" ", strip=True).split())
    s = table.find_previous(string=stmt_rx)
    return " ".join(s.split()) if s else ""


def parse_financial(path: Path, company: str) -> dict:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    observations, tables = [], []
    for t_idx, table in enumerate(soup.find_all("table")):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        header = [" ".join(c.get_text(" ", strip=True).split()) for c in rows[0].find_all(["td", "th"])]
        periods = [normalise_period(h) for h in header[1:]]
        if not header or not any(periods):
            continue
        heading = _heading_for(table)
        first_labels = [" ".join(r.find(["td", "th"]).get_text(" ", strip=True).split()) for r in rows[1:15] if r.find(["td", "th"])]
        stmt = _statement_for(heading, first_labels)
        if stmt is None:
            continue
        um = UNIT_RX.search(heading)
        unit_word = (um.group(1).lower().rstrip("s") if um else ("crore" if stmt != "ratios" else None))
        scale = SCALE_TO_CRORE.get(unit_word) if unit_word else None
        basis = _basis_for(heading)
        tables.append({"table_index": t_idx, "statement": stmt, "heading": heading, "basis": basis,
                       "raw_unit": f"INR {unit_word}" if unit_word else None, "period_labels": header[1:], "periods": periods})
        section: list[str] = []
        for r_idx, row in enumerate(rows[1:], start=1):
            cells = [" ".join(c.get_text(" ", strip=True).split()) for c in row.find_all(["td", "th"])]
            if not cells or not cells[0]:
                continue
            label = cells[0]
            values = cells[1:]
            if all(v.strip() == "" for v in values):
                section = (section + [label])[-2:]   # section header row, e.g. "Current Assets" / "Financial Assets:"
                continue
            for p_label, period, raw in zip(header[1:], periods, values):
                if period is None:
                    continue
                value, state, unit = parse_number(raw)
                lab = label.lower()
                if unit == "%" or stmt == "ratios":
                    out_unit, out_val = (unit or "x"), value
                elif "per share" in lab or re.search(r"\b(?:basic|diluted)\b", lab) or "earning" in lab:
                    out_unit, out_val = "INR per share", value
                elif "shares" in lab:
                    out_unit, out_val = "shares", value
                else:
                    out_unit = "INR crore"
                    out_val = None if value is None or scale is None else (value * scale)
                observations.append({
                    "company": company, "statement": stmt, "basis": basis, "raw_label": label,
                    "section": " > ".join(section), "period": period, "period_label": p_label, "raw_text": raw,
                    "raw_unit": f"INR {unit_word}" if unit_word and out_unit == "INR crore" else out_unit,
                    "value": None if out_val is None else format(out_val.normalize(), "f"), "state": state, "unit": out_unit,
                    "anchor": {"file": path.name, "table_index": t_idx, "row_index": r_idx, "heading": heading},
                })
    return {"tables": tables, "observations": observations}


def map_canonical(observations: list[dict]) -> dict[str, dict[str, dict]]:
    """Map annual observations, retaining conflicts in repeated profit rows."""
    out: dict[str, dict[str, dict]] = {}
    for field, (stmts, patterns) in CANONICAL.items():
        rx = [re.compile(p, re.I) for p in patterns]
        for o in observations:
            if o["statement"] not in stmts:
                continue
            label = re.sub(r"\s+", " ", o["raw_label"]).strip()
            if field == "pat_owners" and "comprehensive income" in o["section"].casefold():
                continue
            if any(r.search(label) for r in rx):
                period = o["period"]
                values = out.setdefault(field, {})
                previous = values.setdefault(period, o)
                if field not in {"pat", "pat_owners", "eps_basic", "eps_diluted"} or previous is o:
                    continue
                if previous["basis"] != o["basis"] or previous["anchor"]["table_index"] != o["anchor"]["table_index"]:
                    continue
                continuing = "continuing operation" in label.casefold()
                previous_continuing = "continuing operation" in previous["raw_label"].casefold()
                if field == "pat" and continuing != previous_continuing:
                    if previous_continuing:
                        values[period] = o
                    continue
                if previous["value"] is not None and o["value"] is not None and previous["value"] != o["value"]:
                    values[period] = {**previous, "value": None, "state": "conflict", "components": [
                        {"label": f"Row {item['anchor']['row_index']}: {item['raw_label']}",
                         "value": item["value"], "raw_text": item["raw_text"], "raw_unit": item["raw_unit"],
                         "anchor": item["anchor"]} for item in (previous, o)
                    ]}
    return out


def _lines(path: Path) -> list[str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    return soup.get_text("\n", strip=True).split("\n")


def parse_overview(path: Path) -> dict:
    lines = _lines(path)
    out: dict = {"_file": path.name}
    if "Last Traded Price" in lines:
        i = lines.index("Last Traded Price")
        out["price_raw"] = lines[i + 1]
        out["price_change_raw"] = lines[i + 2] if i + 2 < len(lines) else None
    for j, line in enumerate(lines[:-1]):
        key = OVERVIEW_FIELDS.get(line)
        if key and key not in out:
            out[key] = lines[j + 1]
    joined = "\n".join(lines)
    m = re.search(r"Share Details as\s*of\s*([A-Za-z]+ \d{1,2}, \d{4})", joined)
    if m:
        out["share_details_as_of"] = m.group(1)
    m = re.search(r"Outstanding Shares:\s*\n?([\d,]+)", joined)
    if m:
        out["shares_details"] = m.group(1)
    m = re.search(r"Lot Size of [^\n]*\n([\d,]+)", joined)
    if m:
        out["lot_size"] = m.group(1)
    # company description: the paragraph block after "Company Overview"
    if "Unlisted Shares - Company Overview" in lines:
        i = lines.index("Unlisted Shares - Company Overview")
        block = []
        for line in lines[i + 1:i + 60]:
            if re.search(r"Share Price, Share Details|Outstanding Shares|Board of Directors", line):
                break
            block.append(line)
        out["description"] = re.sub(r"\s+", " ", " ".join(block)).strip()
    return out
