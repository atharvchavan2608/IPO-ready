"""Issuer-document text extraction and selected-line reading.

PDF text is extracted page by page with pypdf and cached (keyed by the PDF's SHA-256) so the
agent and the reconciliation read identical text. Selected statement lines are read with
explicit label patterns; a line that is not found is reported as not found, never guessed.
"""
from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader

from .config import CAPTURES, ROOT

TEXT_CACHE = ROOT / "data" / "derived" / "pdf_text"
NUM = r"\(?-?[\d,]+\.\d+\)?|-"

# (page hint, canonical field, label regex). Pages are 1-based physical pages of the restated
# financial information PDF; the reader also confirms the page title before using it.
IGX_SELECTED = {
    "balance_sheet": {
        "page": 5, "title": "Restated Statement of Assets and Liabilities",
        "lines": {
            "trade_receivables": r"\(ii\) Trade receivables",
            "cash": r"\(iii\) Cash and cash equivalents",
            "current_investments": r"\(i\) Investments 10\(a\)",
            "current_assets": r"Total current assets",
            "total_assets": r"TOTAL ASSETS",
            "total_equity": r"Total equity",
            "settlement_and_other_fin_liabilities": r"\(iii\) Other financial liabilities",
            "current_liabilities": r"Total current liabilities",
            "total_liabilities": r"TOTAL LIABILITIES",
            "inventories": r"(?:\([ivx]+\) )?Inventories",
        },
    },
    "income_statement": {
        "page": 6, "title": "Restated Statement of Profit and Loss",
        "lines": {
            "revenue_ops": r"Revenue from operations",
            "other_income": r"Other income",
            "total_income": r"Total Income",
            "total_expenses": r"Total expenses",
            "finance_cost": r"Finance costs",
            "pbt": r"Restated Profit before tax",
            "tax": r"Total tax expense",
            "pat": r"Restated Profit for the year \(A\)",
            "eps": r"Basic \( ?₹\)",
            "eps_diluted": r"Diluted \( ?₹\)",
        },
    },
    "cash_flow": {
        "page": 7, "title": "Restated Statement of Cash flows",
        "lines": {"cfo": r"Net cash generated from/\(used in\) operating activities"},
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page_texts(pdf: Path) -> dict:
    """Return {'sha256', 'pages': [text,...]} using a hash-keyed cache."""
    digest = sha256_file(pdf)
    TEXT_CACHE.mkdir(parents=True, exist_ok=True)
    cache = TEXT_CACHE / f"{digest}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    reader = PdfReader(str(pdf))
    data = {"sha256": digest, "file": pdf.name, "pages": [(p.extract_text() or "") for p in reader.pages]}
    cache.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def latest_issuer_docs() -> dict[str, dict]:
    """doc_id -> manifest item with an absolute 'abs_path' (latest successful capture)."""
    docs: dict[str, dict] = {}
    for m in sorted((CAPTURES / "issuer").glob("*/manifest.json")):
        for it in json.loads(m.read_text(encoding="utf-8"))["items"]:
            if it.get("status") != 200 or not it.get("sha256"):
                continue
            run = it.get("reused_from_run") or m.parent.name
            path = CAPTURES / "issuer" / run / it["path"]
            if path.is_file() and sha256_file(path) == it["sha256"]:
                docs[it["id"]] = {**it, "abs_path": str(path), "capture_run": run}
    return docs


def _num(tok: str) -> Decimal | None:
    tok = tok.strip()
    if tok == "-":
        return Decimal(0)
    neg = tok.startswith("(") and tok.endswith(")")
    v = Decimal(tok.strip("()").replace(",", ""))
    return -v if neg else v


def read_selected_lines(pdf: Path, spec: dict = IGX_SELECTED) -> dict:
    """Read selected lines. Values are INR million in the document; returned in INR crore too."""
    texts = page_texts(pdf)
    out: dict = {"document_sha256": texts["sha256"], "statements": {}}
    for stmt, s in spec.items():
        page = texts["pages"][s["page"] - 1]
        title_ok = s["title"].lower() in page.lower()
        years = re.findall(r"31 March (\d{4})", page.split("\n", 4)[-1][:600]) or re.findall(r"31 March (\d{4})", page)
        periods = [f"FY{y}" for y in years[:3]]
        unit_m = re.search(r"All amounts in ([A-Za-z ]+?)(?:,|\))", page)
        lines_out = {}
        for field, label_rx in s["lines"].items():
            rx = re.compile(rf"^\s*{label_rx}(?:\s+\d+(?:\([a-z]\))?)?\s+({NUM})\s+({NUM})\s+({NUM})", re.M)
            m = rx.search(page)
            if not m:
                lines_out[field] = {"state": "no_line_item", "label_pattern": label_rx}
                continue
            vals = [_num(g) for g in m.groups()]
            lines_out[field] = {
                "state": "reported", "matched_text": " ".join(m.group(0).split()),
                "raw_values": dict(zip(periods, m.groups())),
                "values_inr_million": {p: str(v) for p, v in zip(periods, vals)},
                "values_inr_crore": {p: format(v if field.startswith("eps") else v / 10, "f") for p, v in zip(periods, vals)},
                "unit": "INR per share" if field.startswith("eps") else "INR crore (converted from INR million / 10)",
            }
        out["statements"][stmt] = {"page": s["page"], "title_confirmed": title_ok, "periods": periods,
                                   "unit_text": unit_m.group(1).strip() if unit_m else None, "lines": lines_out}
    return out


def igx_operating_scope(pdf: Path) -> dict | None:
    """Review the pinned scope disclosures before allowing a standalone operating reference."""
    pages = page_texts(pdf)["pages"]
    scope_text = " ".join(pages[54].lower().split()) if len(pages) >= 55 else ""
    relationship = " ".join(pages[8].lower().split()) if len(pages) >= 9 else ""
    if ("esos trust is considered an extension of the company" not in scope_text
            or "17 january 2022, igx has become an associate of iex" not in relationship):
        return None
    return {
        "basis": "issuer_and_esos_trust", "operating_comparison_basis": "standalone",
        "label": "Restated IGX and employee share trust",
        "note": "IGX treats its employee share trust as an extension of the issuer. The restated income statement supports an operating comparison with standalone exchanges. IGX is an associate of IEX, its promoter.",
        "scope_page": 55, "relationship_page": 9,
    }


def igx_inventory_note(pdf: Path) -> str | None:
    """Use the issuer's inventory note only with years on the retained balance sheet."""
    pages = page_texts(pdf)["pages"]
    if len(pages) < 54:
        return None
    notes = " ".join(pages[53].split()).partition("Notes:")[2]
    if "Inventory turnover ratio" in notes and "cannot be meaningfully calculated or are not applicable" in notes:
        return "Inventory turnover is not applicable to the business."
    return None


def igx_market_activity(doc: dict, evidence) -> dict:
    """Read matching twelve-month fee and traded-volume definitions from the prospectus."""
    pdf = Path(doc["abs_path"])
    pages = page_texts(pdf)["pages"]
    if len(pages) < 30:
        return {}
    page = " ".join(pages[29].split())
    if "Particulars Fiscal 2026 Fiscal 2025 Fiscal 2024" not in page:
        return {}
    rows = {
        "volume": (r"Trade volume \(Million MMBtu\)", "million MMBtu"),
        "fees": (r"Transaction fees after netting of provision for reversal of revenue \(₹ million\) \(A\)", "INR million"),
    }
    by_period = {}
    for key, (label, unit) in rows.items():
        match = re.search(rf"({label}) ({NUM}) ({NUM}) ({NUM})(?!\S)", page)
        if not match or "-" in match.groups()[1:]:
            return {}
        for year, token in zip((2026, 2025, 2024), match.groups()[1:]):
            period = f"FY{year}"
            eid = evidence.add({"source": "IGX Draft Red Herring Prospectus", "url": f'{doc["url"]}#page=30', "page": 30,
                                "sha256": doc["sha256"], "retrieved_at": doc["retrieved_at"], "file": pdf.name,
                                "period": period, "period_label": f"Fiscal {year}", "basis": "IGX trading venue",
                                "raw_label": match[1], "raw_text": token, "raw_unit": unit})
            by_period.setdefault(period, {})[key] = {"value": format(_num(token), "f"), "ev": eid}
    return by_period
