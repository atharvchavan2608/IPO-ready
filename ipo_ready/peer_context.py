"""Bounded sources and reviewed research notes for the comparison page."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import re

from bs4 import BeautifulSoup
from pypdf import PdfReader

from .issuer import sha256_file
from .parse_wwipl import parse_number

CONTEXT_SOURCES = {
    "iex-oct-call": ("https://nsearchives.nseindia.com/corporate/IEX_05112026110840_IEX_Intimation_EarningCall_Transcript_Q2_Sep26Signed.pdf", "pdf", 3_000_000),
    "mcx-coal-release": ("https://www.mcxindia.com/docs/default-source/media/pressreleases/english/2026/april/mcx-receives-sebi-approval-to-incorporate-a-new-coal-exchange.pdf", "pdf", 1_000_000),
    "igx-oct-reporting": ("https://psuwatch.com/amp/story/newsupdates/igx-gas-trade-volume-rises-326-year-on-year-in-october", "html", 2_000_000),
    "cial-annual-2026": ("https://www.cial.aero/ckeditor/upload/CIAL_Annual_Report_2025_2026.pdf", "pdf", 16_000_000),
    "cial-terminal-tender": ("https://www.cial.aero/Tender-Details?TdId=1636", "html", 1_000_000),
    "autoaxles-annual-2026": ("https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_159028_19052026202413_iXBRL_WEB.html", "html", 2_000_000),
    "alkem-fy26-release": ("https://admin.alkemlabs.com/uploads/Q4_and_FY_26_Results_Press_Release_and_Results_Presentation_52dad86930.pdf", "pdf", 8_000_000),
    "crunchbase-filters": ("https://support.crunchbase.com/hc/en-us/articles/30493799544211-Companies-Filters-Definitions", "html", 2_000_000),
}

# Short paraphrases from opened sources. The date and anchor identify the reviewed passage.
# Each entry is attached to the company making the disclosure or covered in the article.
NOTES = {
    "igx": [
        ("igx-drhp", "2026-07-14", "Plan", "Expand gas market participation",
         "The draft prospectus describes plans to add delivery points, including in the North-East, and deepen liquidity across existing contracts.",
         250, "Strategies · expand participation and deepen liquidity", "IGX draft prospectus"),
        ("igx-oct-reporting", "2026-11-06", "Reporting", "October gas volume rose year over year",
         "PSU Watch reported 13.28 million MMBtu traded in October, up 326% from a year earlier and down 25% from September. The two comparisons highlight how volatile month-to-month volumes can be.",
         None, "Opening paragraphs of the article", "PSU Watch"),
    ],
    "IEX": [
        ("iex-oct-call", "2026-10-30", "Plan", "Extend the term-ahead market",
         "Management said it was awaiting CERC approval to extend the term-ahead contract from three to 11 months and add green real-time and peak trading segments.",
         6, "Product pipeline paragraph", "IEX earnings call"),
    ],
    "MCX": [
        ("mcx-coal-release", "2026-04-20", "Plan", "Approval to incorporate a coal exchange",
         "MCX said SEBI approved its investment in a proposed coal exchange. It planned to incorporate a subsidiary and apply to the Coal Controller when prescribed.",
         1, "Press release", "MCX"),
    ],
    "cial": [
        ("cial-terminal-tender", "2025-10-21", "Plan", "Prepare the Terminal 1 expansion",
         "CIAL invited design, engineering and project management consultants for expansion of the existing Terminal 1 and associated projects.",
         None, "Tender CIAL/CIVIL/688 · Name of Work", "CIAL tender notice"),
    ],
    "ALKEM": [
        ("alkem-fy26-release", "2026-05-28", "Plan", "Chronic therapies and international launches",
         "Management highlighted chronic therapies and a pipeline of international launches as expected contributors to FY2027 growth.",
         19, "CEO comments in the FY2026 results release", "Alkem Laboratories"),
    ],
}


def _evidence(capture: dict, page: int | None, anchor: str) -> dict:
    return {"url": capture["url"] + (f"#page={page}" if page else ""), "page": page, "anchor": anchor,
            "retrieved_at": capture["retrieved_at"], "sha256": capture["sha256"],
            "capture_run": capture.get("run") or capture["capture_run"], "file": Path(capture["abs_path"]).name}


def build_updates(captures: dict, issuer_docs: dict) -> dict:
    available = {**captures, **issuer_docs}
    result = {}
    for company, notes in NOTES.items():
        result[company] = []
        for key, date, kind, title, summary, page, anchor, publisher in notes:
            capture = available.get(key)
            if capture is None:
                continue
            result[company].append({"date": date, "kind": kind, "title": title, "summary": summary,
                                    "publisher": publisher, "evidence": _evidence(capture, page, anchor)})
    return result


def read_cial_annual(capture: dict | None) -> dict | None:
    """Read six explicitly reviewed rows from the retained FY2026 filing."""
    if not capture:
        return None
    path = Path(capture["abs_path"])
    if sha256_file(path) != capture["sha256"]:
        return None
    reader = PdfReader(path)
    for physical_page in range(121, min(133, len(reader.pages)) + 1):
        lines = [" ".join(line.split()) for line in reader.pages[physical_page - 1].extract_text().splitlines()]
        sheet = " ".join(lines).upper()
        if "CONSOLIDATED STATEMENT OF PROFIT AND LOSS FOR THE YEAR ENDED 31" in sheet and "RUPEES IN LAKHS" in sheet:
            break
    else:
        return None

    fields = {
        "revenue_ops": ("Revenue from Operations", "1,40,148.85"),
        "other_income": ("Other Income", "9,072.81"),
        "finance_cost": ("Finance Costs", "3,474.41"),
        "pbt": ("Profit before tax (VII - VIII)", "70,955.12"),
        "pat": ("Profit for the year (IX - X)", "52,674.63"),
        "eps": ("Basic (In ₹per share)", "11.01"),
    }
    facts = {}
    for key, (label, raw) in fields.items():
        pattern = rf"{re.escape(label)}\s+(?:\d+\.\d+\s+)?{re.escape(raw)}\s"
        if not re.search(pattern, sheet, re.IGNORECASE):
            return None
        value = Decimal(raw.replace(",", "")) / (1 if key == "eps" else 100)
        facts[key] = {"value": format(value, "f"), "state": "reported", "basis": "consolidated",
                      "evidence": {**_evidence(capture, physical_page, label), "source": "CIAL annual report FY2026",
                                   "raw_label": label, "raw_text": raw,
                                   "raw_unit": "INR/share" if key == "eps" else "INR lakh",
                                   "period_label": "For the year ended 31.03.2026"}}
    return {"label": "FY2026 issuer consolidated statements", "basis": "consolidated",
            "period_end": "2026-03-31", "date": "2026-08-08", "facts": facts,
            "evidence": _evidence(capture, physical_page, "Consolidated Statement of Profit and Loss")}


def read_autoaxles_annual(capture: dict | None) -> dict | None:
    """Read the annual audited column from the exchange's rendered statement."""
    if not capture:
        return None
    path = Path(capture["abs_path"])
    if sha256_file(path) != capture["sha256"]:
        return None
    document = BeautifulSoup(path.read_bytes(), "lxml")
    metadata = {}
    for row in document.find_all("tr"):
        cells = [" ".join(" ".join(cell.stripped_strings).split()) for cell in row.find_all(["td", "th"], recursive=False)]
        if len(cells) == 2:
            metadata[cells[0]] = cells[1]
    if metadata.get("Description of presentation currency") != "INR" or metadata.get("Level of rounding used in financial results") != "Lakhs":
        return None
    column_checks = {"Date of start of reporting period": "01-04-2025",
                     "Date of end of reporting period": "31-03-2026",
                     "Whether results are audited or unaudited": "Audited",
                     "Nature of report standalone or consolidated": "Standalone"}
    table = None
    for candidate in document.find_all("table"):
        rows = {}
        for element in candidate.find_all("tr"):
            cells = [" ".join(" ".join(cell.stripped_strings).split()) for cell in element.find_all(["td", "th"], recursive=False)]
            if len(cells) == 4:
                rows[cells[1]] = cells[3]
        if all(rows.get(label) == expected for label, expected in column_checks.items()):
            table = rows
            break
    if table is None:
        return None
    mappings = {"revenue_ops": "Revenue from operations", "other_income": "Other income",
                "pat": "Total profit (loss) for period",
                "eps": "Basic earnings (loss) per share from continuing operations"}
    facts = {}
    for key, label in mappings.items():
        raw = table.get(label)
        value, state, _ = parse_number(raw)
        if value is None or not value.is_finite():
            continue
        facts[key] = {"value": format(value / (1 if key == "eps" else 100), "f"), "state": state,
                      "basis": "standalone", "raw_label": label, "raw_text": raw,
                      "raw_unit": "INR/share" if key == "eps" else "INR lakh", "period_label": "Year to date",
                      "anchor": "Audited financial results · annual column"}
    if not {"revenue_ops", "pat"} <= facts.keys():
        return None
    return {"state": "ok", "basis": "standalone", "name": "Automotive Axles Ltd",
            "source": {**_evidence(capture, None, "Audited financial results · annual column"),
                       "provider": "NSE rendered company filing", "run": capture["run"]},
            "annual": {"2026-03-31": facts}}
