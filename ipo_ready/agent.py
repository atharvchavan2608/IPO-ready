"""Disclosure-gap agent: find (or rule out) inventory and NPA disclosures for an unlisted company.

A bounded, deterministic tool sequence. Each step is recorded in a trace so a reviewer can see
what ran, on which document and page, and why the verdict follows. No model is called; the
financial values it reports are read from documents, never generated.

Tools, in order:
  1. provider_lookup      - is the field in the provider's parsed statements?
  2. applicability_rule   - is the field expected for this business model?
  3. statement_line_check - does the issuer's balance sheet enumerate an Inventories line?
  4. document_search      - word-boundary search across retained issuer PDFs (page-anchored)
  5. classify_passages    - explicit not-applicable statement / numeric disclosure / narrative
  6. verdict              - combine signals; say how to verify and what to check next

Extension point (not executed in this build): pass the top passages and the verdict to a language
model to draft a plain-language summary, with citations restricted to the passage IDs supplied.

CLI: python -m ipo_ready.agent igx inventories
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from pypdf import PdfReader

from .issuer import latest_issuer_docs, page_texts, read_selected_lines

FIELDS = ("inventories", "npa")

APPLICABILITY = {
    "inventories": {
        "exchange": ("not_expected", "An exchange earns transaction and membership fees; it does not hold goods for sale."),
        "broker": ("not_expected", "A broker or custodian holds client and own financial assets, not goods."),
        "lender": ("not_expected", "A lender's assets are loans and investments; inventory is not a working-capital item."),
        "insurer": ("not_expected", "An insurer's assets are investments and premium receivables."),
        "services": ("not_expected", "An IT/consulting services company usually carries little or no inventory."),
        "platform": ("possible", "Marketplace models may hold no stock; inventory-led models (e.g. e-pharmacy) do."),
        "consumer": ("possible", "Consumer businesses range from no stock (franchises) to large stock (retail)."),
        "infrastructure": ("possible", "Operators may carry stores and spares."),
        "manufacturer": ("expected", "Manufacturers carry raw material, work-in-progress and finished goods."),
    },
    "npa": {
        "lender": ("expected", "Non-performing assets measure a lender's asset quality; NBFCs disclose Stage 3 / GNPA."),
        "_default": ("not_applicable", "NPA is a lender asset-quality measure; this business has no loan book to classify."),
    },
}

PATTERNS = {
    "inventories": [r"\binventor(?:y|ies)\b"],
    "npa": [r"\bG?N?NPAs?\b", r"\bnon[- ]performing (?:assets?|loans?)\b", r"\bstage\s*(?:3|III)\s+(?:assets|loans)\b"],
}
NAIVE_SUBSTRING = {"inventories": "inventor", "npa": "npa"}
NOT_APPLICABLE_RX = re.compile(r"not applicable|cannot be meaningfully calculated|not meaningful", re.I)
NUMERIC_NPA_RX = re.compile(r"\b(?:gross|net)\s+(?:NPA|non[- ]performing assets?)\b[^.\n]{0,40}?\d+(?:\.\d+)?\s*%", re.I)
LINE_ITEM_RX = re.compile(r"^\s*(?:\([ivx]+\)\s*)?Inventories\s+(?:\d+\s+)?\(?[\d,]+\.\d+", re.I | re.M)


def _step(trace: list, tool: str, inp: dict, out: dict, t0: float) -> dict:
    s = {"step": len(trace) + 1, "tool": tool, "input": inp, "output": out, "ms": round((time.perf_counter() - t0) * 1000, 1)}
    trace.append(s)
    return s


def _snippet(text: str, start: int, end: int, width: int = 220) -> str:
    a, b = max(0, start - width // 2), min(len(text), end + width // 2)
    return ("…" if a else "") + " ".join(text[a:b].split()) + ("…" if b < len(text) else "")


def run(company: dict, provider_fields: dict, field: str, docs: dict | None = None) -> dict:
    """company: universe entry; provider_fields: canonical field -> period -> observation."""
    if field not in FIELDS:
        raise ValueError(f"field must be one of {FIELDS}")
    trace: list[dict] = []
    docs = latest_issuer_docs() if docs is None else docs
    company_docs = {k: v for k, v in docs.items() if v.get("company") == company["id"]}
    model = company.get("model", "unknown")

    # 1. provider lookup
    t0 = time.perf_counter()
    key = "inventories" if field == "inventories" else "gross_npa"
    prov = provider_fields.get(key, {})
    prov_found = {p: o for p, o in prov.items() if o.get("state") in ("reported", "explicit_zero")}
    _step(trace, "provider_lookup", {"company": company["id"], "field": key},
          {"found": bool(prov_found), "periods": sorted(prov_found),
           "detail": "line present in provider statements" if prov_found else "no matching line in the provider's parsed statements"}, t0)

    # 2. applicability
    t0 = time.perf_counter()
    table = APPLICABILITY[field]
    applicability, reason = table.get(model) or table.get("_default") or ("possible", "Business model not classified.")
    _step(trace, "applicability_rule", {"field": field, "business_model": model},
          {"expectation": applicability, "reason": reason}, t0)

    # 3. statement line check (issuer balance sheet)
    line_check = None
    t0 = time.perf_counter()
    restated = next((v for k, v in company_docs.items() if "restated" in k), None)
    if field == "inventories" and restated:
        sel = read_selected_lines(Path(restated["abs_path"]))
        bs = sel["statements"]["balance_sheet"]
        inv = bs["lines"]["inventories"]
        line_check = {"document": restated["id"], "page": bs["page"], "title_confirmed": bs["title_confirmed"],
                      "inventories_line": inv["state"], "current_assets_line": bs["lines"]["current_assets"]["state"]}
        _step(trace, "statement_line_check", {"document": restated["id"], "page": bs["page"]}, line_check, t0)
    else:
        _step(trace, "statement_line_check", {"document": None},
              {"skipped": True, "why": "no retained issuer balance sheet for this company" if not restated else "not used for NPA"}, t0)

    # 4. document search
    t0 = time.perf_counter()
    rxs = [re.compile(p, re.I) for p in PATTERNS[field]]
    hits, naive_pages, searched = [], 0, []
    for doc_id, d in company_docs.items():
        if page_numbers := d.get("scan_pages"):
            reader = PdfReader(d["abs_path"])
            pages = {number: reader.pages[number - 1].extract_text() or "" for number in page_numbers}
        else:
            texts = page_texts(Path(d["abs_path"]))["pages"]
            pages = dict(zip(d.get("original_pages") or range(1, len(texts) + 1), texts))
        searched.append({"document": doc_id, "pages": len(pages), "sha256": d["sha256"][:16]})
        for pno, text in pages.items():
            if NAIVE_SUBSTRING[field] in text.lower():
                naive_pages += 1
            for rx in rxs:
                for m in rx.finditer(text):
                    hits.append({"document": doc_id, "url": d["url"], "page": pno, "match": m.group(0),
                                 "snippet": _snippet(text, m.start(), m.end()), "_text": text})
                    break  # one hit per pattern per page is enough for review
    # de-duplicate by (document, page)
    seen, uniq = set(), []
    for h in hits:
        k = (h["document"], h["page"])
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    _step(trace, "document_search", {"documents": [s["document"] for s in searched], "patterns": PATTERNS[field]},
          {"documents_searched": searched, "pages_with_word_matches": len(uniq),
           "pages_with_naive_substring": naive_pages,
           "note": f"naive substring '{NAIVE_SUBSTRING[field]}' also matches unrelated words (e.g. 'COMPANY' contains 'NPA'); word-boundary patterns used"}, t0)

    # 5. classify passages
    t0 = time.perf_counter()
    classified = []
    for h in uniq:
        text = h.pop("_text")
        window = text[max(0, text.lower().find(h["match"].lower()) - 600):][:1400]
        if field == "inventories" and LINE_ITEM_RX.search(text):
            kind = "numeric_line_item"
        elif field == "npa" and NUMERIC_NPA_RX.search(text):
            kind = "numeric_disclosure"
        elif NOT_APPLICABLE_RX.search(window):
            kind = "explicit_not_applicable"
        else:
            kind = "narrative_mention"
        classified.append({**h, "kind": kind})
    order = {"numeric_line_item": 0, "numeric_disclosure": 0, "explicit_not_applicable": 1, "narrative_mention": 2}
    doc_rank = lambda d: 0 if "restated" in d else (1 if "drhp" in d else 2)  # audited statements first
    classified.sort(key=lambda c: (order[c["kind"]], doc_rank(c["document"]), c["page"]))
    counts: dict[str, int] = {}
    for c in classified:
        counts[c["kind"]] = counts.get(c["kind"], 0) + 1
    _step(trace, "classify_passages", {"passages": len(classified)}, {"by_kind": counts}, t0)

    # 6. verdict
    t0 = time.perf_counter()
    numeric = [c for c in classified if c["kind"] in ("numeric_line_item", "numeric_disclosure")]
    explicit_na = [c for c in classified if c["kind"] == "explicit_not_applicable"]
    if prov_found:
        status, summary = "found_in_provider", f"{field.upper() if field == 'npa' else 'Inventories'} reported by the provider for {', '.join(sorted(prov_found))}."
        verify = "Open the provider row from the evidence drawer; reconcile with the issuer's annual report before relying on it."
    elif numeric:
        status, summary = "found_in_issuer_document", f"Numeric disclosure found on {numeric[0]['document']} p{numeric[0]['page']}."
        verify = "Open the cited page and confirm period, unit and basis."
    elif field == "inventories" and explicit_na and line_check and line_check["inventories_line"] == "no_line_item":
        status = "inapplicable"
        summary = (f"Not applicable: the restated balance sheet (p{line_check['page']}) lists no inventories line, and the issuer "
                   f"states inventory ratios are not applicable to its business (p{explicit_na[0]['page']}).")
        verify = f"Open {line_check['document']} p{line_check['page']} and p{explicit_na[0]['page']}."
    elif field == "npa" and applicability == "not_applicable":
        status = "inapplicable"
        searched_pages = sum(s["pages"] for s in searched)
        mention = (f" {len(classified)} page(s) mention NPA-like terms; none discloses an NPA ratio for this company." if classified
                   else f" Word-boundary search of {searched_pages} issuer pages found no NPA disclosure." if searched else "")
        summary = f"Not applicable by business model: {reason}{mention}"
        verify = ("Review the listed mentions to confirm they concern other entities or general risk text." if classified
                  else "No mentions to review; the business-model rule decides.")
    elif company_docs:
        status = "not_found"
        summary = f"No {field} disclosure found across {sum(s['pages'] for s in searched)} reviewed issuer pages."
        verify = "Search the latest audited annual report notes."
    else:
        status = "not_found_no_documents"
        summary = f"No issuer documents retained for {company['short']}; the provider does not report {field}. Expectation: {applicability}."
        verify = "Not verifiable from retained evidence."
    next_checks = {
        "inventories": ["Audited annual report: balance sheet 'Inventories' line and note on valuation",
                        "MCA AOC-4 financial statement filing (paid access)",
                        "DRHP 'Restated financial information' if the company files for an IPO"],
        "npa": ["Annual report notes: 'Stage 3 assets', 'Gross NPA', 'Net NPA' (RBI disclosure for NBFCs)",
                "Investor presentation or credit-rating rationale (ICRA/CRISIL/CARE) for asset-quality figures",
                "DRHP 'Key performance indicators' section if an IPO is filed"],
    }[field]
    out = {"status": status, "summary": summary, "how_to_verify": verify}
    _step(trace, "verdict", {"signals": {"provider": bool(prov_found), "numeric": len(numeric), "explicit_na": len(explicit_na),
                                         "line_check": (line_check or {}).get("inventories_line"), "expectation": applicability}}, out, t0)
    return {
        "company": company["id"], "field": field, "status": status, "summary": summary, "how_to_verify": verify,
        "expectation": {"level": applicability, "reason": reason},
        "evidence": [{k: v for k, v in c.items()} for c in classified[:8]],
        "evidence_total": len(classified), "next_checks": next_checks if status not in ("inapplicable", "found_in_provider") else next_checks[:1],
        "trace": trace, "executed": "deterministic tool sequence (no language model call)",
    }


def main() -> None:
    import json
    from .config import load_universe
    from .pipeline import provider_fields_for

    sys.stdout.reconfigure(encoding="utf-8")
    cid, field = sys.argv[1], sys.argv[2]
    company = next(c for c in load_universe()["unlisted"] if c["id"] == cid)
    print(json.dumps(run(company, provider_fields_for(cid), field), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
