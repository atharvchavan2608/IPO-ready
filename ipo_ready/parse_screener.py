"""Read annual facts from retained Screener.in captures."""
from __future__ import annotations

import calendar
import hashlib
import re
from decimal import InvalidOperation
from pathlib import Path

from bs4 import BeautifulSoup

from .parse_wwipl import MONTHS, parse_number

ANNUAL_HEADER = re.compile(r"([A-Z][a-z]{2}) (\d{4})(?: \(([SC])\))?")
ROWS = {
    "profit-loss": {
        "Sales": ("revenue_ops", "INR crore"),
        "Revenue": ("revenue_ops", "INR crore"),
        "Other Income": ("other_income", "INR crore"),
        "Expenses": ("total_expenses", "INR crore"),
        "Operating Profit": ("ebitda", "INR crore"),
        "Depreciation": ("depreciation", "INR crore"),
        "Profit before tax": ("pbt", "INR crore"),
        "Interest": ("finance_cost", "INR crore"),
        "Net Profit": ("pat", "INR crore"),
        "EPS in Rs": ("eps", "INR/share"),
    },
    "balance-sheet": {
        "Total Assets": ("total_assets", "INR crore"), "Borrowings": ("borrowings", "INR crore"),
        "Fixed Assets": ("fixed_assets", "INR crore"),
    },
    "cash-flow": {
        "Cash from Operating Activity": ("cfo", "INR crore"),
        "Cash from Investing Activity": ("cfi", "INR crore"),
        "Cash from Financing Activity": ("cff", "INR crore"),
        "Net Cash Flow": ("net_change", "INR crore"),
    },
    "ratios": {"ROCE %": ("provider_roce", "%")},
}


def parse_screener(item: dict) -> dict:
    path = Path(item["abs_path"])
    data = path.read_bytes()
    source = {
        "url": item["url"], "retrieved_at": item["retrieved_at"], "sha256": item["sha256"],
        "run": item["run"], "file": path.name, "provider": "Screener.in",
    }
    if hashlib.sha256(data).hexdigest() != item["sha256"]:
        return {"source": source, "state": "capture_hash_mismatch"}
    soup = BeautifulSoup(data, "lxml")
    heading = soup.select_one("h1")
    statement = soup.select_one("#profit-loss p")
    basis_match = re.match(r"(Standalone|Consolidated)\b", statement.get_text(" ", strip=True)) if statement else None
    basis = basis_match[1].lower() if basis_match else None
    if heading is None or basis != item["basis"]:
        return {"source": source, "state": "unexpected_statement_basis"}

    annual = {}
    for section, labels in ROWS.items():
        table = soup.select_one(f"#{section} table")
        description = soup.select_one(f"#{section} p")
        if table is None or description is None:
            continue
        description = description.get_text(" ", strip=True)
        if not description.startswith(basis.title()) or (section != "ratios" and "Figures in Rs. Crores" not in description):
            continue
        headers = [h.get_text(" ", strip=True) for h in table.select("thead th")]
        for row in table.select("tbody > tr"):
            cells = row.find_all("td", recursive=False)
            if not cells:
                continue
            raw_label = cells[0].get_text(" ", strip=True)
            spec = labels.get(raw_label.removesuffix(" +"))
            if spec is None:
                continue
            field, unit = spec
            for column, (header, cell) in enumerate(zip(headers[1:], cells[1:]), 1):
                period = ANNUAL_HEADER.fullmatch(" ".join(header.split()))
                if not period or period[1].lower() not in MONTHS:
                    continue
                month, year = MONTHS[period[1].lower()], int(period[2])
                period_end = f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
                if section != "profit-loss" and period_end not in annual:
                    continue
                column_basis = {"S": "standalone", "C": "consolidated"}.get(period[3], basis)
                raw = cell.get_text(" ", strip=True)
                try:
                    value, state, _ = parse_number(raw)
                except InvalidOperation:
                    value, state = None, "unparsed"
                if value is not None and not value.is_finite():
                    value, state = None, "unparsed"
                facts = annual.setdefault(period_end, {})
                facts[field] = {
                    "value": None if value is None or field in facts else format(value, "f"),
                    "state": "conflict" if field in facts else state, "basis": column_basis,
                    "raw_label": raw_label, "raw_text": raw, "raw_unit": unit, "period_label": header,
                    "anchor": {"section": f"#{section}", "row": raw_label, "column": column},
                }
    profile = soup.select_one(".company-profile")
    return {"source": source, "state": "ok" if annual else "annual_rows_unavailable",
            "name": heading.get_text(" ", strip=True), "basis": basis, "annual": annual,
            "profile_anchor": ".company-profile" if profile is not None else None}
