# XBRL stage 2A: real Aether report versus exchange rendering

Checked: 2026-10-22. Status: companion-report reconciliation completed; raw-instance acquisition and taxonomy validation remain open.

## Evidence and scope

- Issuer: Aether Industries Limited, NSE AETHER, ISIN INE0BWX01014.
- [Official investor-relations archive](https://aether.co.in/investor-relations/) provided the observed PDF link. Its local HTML and acquisition manifest are preserved.
- [Official results PDF](https://aether.co.in/wp-content/uploads/2025/10/9999.pdf), 31 physical pages, board outcome dated 13 November 2025. Includes both standalone and consolidated statements; this comparison uses **standalone only**.
- [NSE rendered filing](https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_127119_13112025150257_iXBRL_WEB.html), standalone, unaudited. Read using the web tool; local download timed out. This is a comparison of publicly presented reports, not proof about the underlying XML tags.
- Quarter: 1 July–30 September 2025. Half-year: 1 April–30 September 2025. Balance sheet: 30 September 2025. Approval date does not establish actual first publication time.
- PDF uses INR **million**, NSE rendering INR **lakh**. Multiply monetary PDF values by 10 for comparison. EPS remains INR per share and must not receive this conversion.
- PDF SHA-256: `9e42c84aa47d8e480f14de3770a850681a04c613fda3ae9f9d7af073c74c3f83`.
- Native evidence: [stage-2 directory](../../../research/xbrl_stage2_20261022), [PDF](../../../research/xbrl_stage2_20261022/aether_q2_fy26.pdf), [download manifest](../../../research/xbrl_stage2_20261022/aether_q2_fy26.manifest.json), [discovery manifest](../../../research/xbrl_stage2_20261022/discovery_manifest.json).

## Method and result

PDF text extraction located the statements. Physical pages 20, 24, 26, 28 and 30 were rendered and visually inspected to resolve OCR errors and column alignment. Selected NSE figures were manually transcribed from its primary-source web rendering. The [reconciliation script](../../../research/xbrl_stage2_reconcile.py) recomputes conversion and differences; it does not automatically extract these figures or validate either report. The initial terminal print encountered a Windows encoding error after the complete text file had been saved; the saved file and page renders were used subsequently.

Twenty-six comparison rows were recorded. Sixteen rows with the same or closely corresponding labels agree exactly after unit conversion. Those include operating revenue, quarter PAT, half-year PAT, assets and the three cash-flow section totals. The other ten rows include numerical differences and matching numbers under different labels; they are deliberately retained rather than silently reconciled.

### Accounting-label conflicts

1. PDF page 24 reports non-current **lease liabilities** of 143.96 million. NSE shows 1,439.60 lakh under **non-current borrowings**. Identical numeric magnitude does not establish equivalent debt definitions. Do not replace the PDF label or assume the XML concept until the instance is inspected.
2. PDF deferred-tax liabilities are 583.35 million. NSE shows zero under deferred tax and 5,833.40 lakh under other non-current liabilities. This suggests a presentation/mapping discrepancy, with a small numerical difference too; responsibility and cause are unverified.
3. PDF page 28 calls 37.17 million **income from current investments**; NSE places 371.70 lakh under **dividends received** and an offset under operating interest received. Treating the number as confirmed dividend income would exceed the evidence.
4. PDF cash generated from operations is 1,530.97 million; NSE presents 15,681.40 lakh. Their final operating cash flow nevertheless matches at 1,306.13 million / 13,061.30 lakh. Agreement at the total does not validate intermediate classifications.
5. PDF PPE purchases are an outflow of 1,003.78 million; the NSE purchase line is 5,566.50 lakh. Other investing outflows are grouped differently while investing cash-flow totals match. Do not infer a usable capex metric from the matching total.
6. PDF separately presents right-of-use assets of 1,774.50 million and other non-current assets of 355.72 million. These labels are not separately presented in the inspected NSE table, while its CWIP and intangible figures differ. Do not speculate that a particular reclassification fully explains the differences.

### Cash definition conflict within the PDF

Balance-sheet cash and cash equivalents are 33.40 million (page 24); closing cash in the cash-flow statement is 561.72 million (page 28). Page 30 explicitly includes other bank balances of 528.33 million in the latter total. Thus the apparent contradiction is partly explained by a disclosed broader cash basis. Even 33.40 + 528.33 = 561.73 differs by 0.01 million from the printed closing total. Preserve that rounding residual and the separate definitions. Do not use the broader figure for net-debt calculations without an explicit policy on eligible bank balances.

### Numerical differences and source authority

Examples: quarter total expenses are 1,702.41 million in the visually inspected PDF versus 17,020.40 lakh in NSE; quarter other expenses are 300.15 million versus 3,001.40 lakh; half-year tax expense is 309.38 million versus 3,093.90 lakh. A blanket tolerance or unit conversion cannot explain all differences. The PDF also has rounding residuals; its quarter total income minus total expenses differs by 0.37 million from printed pre-exceptional profit. Preserve both as reported. This survey does not determine a legally authoritative correction or accuse a party of a filing error.

## Implications for the project (proposals)

- Include statement basis, period start/end, original unit, original label, reported number and source location in each observation.
- Store two source observations before choosing a reviewed value. A reconciliation decision should explain why a particular value/definition is used.
- Separate numerical agreement from label agreement, calculation consistency and validator status. They are independent checks.
- Route classification conflicts affecting debt, cash, capex and earnings adjustments to human review before scoring or valuation.
- Preserve the standalone/consolidated distinction: page 6 consolidated quarter revenue is 2,751.00 million, versus 2,247.20 million standalone on page 20. This is an expected scope difference, not a conflict.
- These 2025 results belong to post-listing evaluation or contemporary analysis; they must not enter reconstructed May-2022 prediction inputs.

## Acquisition limits and next stage

Bounded ordinary public requests: Aether investor-relations HTML and its linked PDF downloaded; NSE HTML timed out; a third-party Infosys discovery page returned HTTP 403. The latter is only a discovery attempt, not financial evidence. No authentication workaround or guessed raw-XML URL was used.

Stage 2 remains incomplete against its original raw-XML completion criterion. Next: obtain one primary raw instance through an explicit accessible link, identify actual concept QNames, contexts, dimensions and units, then test whether the conflicts above occur in the instance or only its rendering. Verify exact matching taxonomy dependencies before running a validator. If Aether remains unavailable, use another non-financial issuer with a clear public download route and retain this comparison as an independent case study.

## Comparison observations

The following table is generated from the manual observations in the research script. Monetary amounts only. `instant` means as at 30 September 2025; `quarter` and `half-year` use the periods above. A different label is flagged even if the numeric difference is zero.

| Observation | PDF page | Period | PDF million | NSE lakh | NSE minus PDF, lakh | Review |
|---|---:|---|---:|---:|---:|---|
| Revenue from operations | 20 | quarter | 2247.20 | 22472.00 | 0.00 | same label |
| Other income | 20 | quarter | 96.67 | 966.70 | 0.00 | same label |
| Total income | 20 | quarter | 2343.87 | 23438.70 | 0.00 | same label |
| Finance costs | 20 | quarter | 18.10 | 181.00 | 0.00 | same label |
| Depreciation and amortisation | 20 | quarter | 152.71 | 1527.10 | 0.00 | same label |
| Profit before tax | 20 | quarter | 615.04 | 6150.40 | 0.00 | same label |
| PAT | 20 | quarter | 435.72 | 4357.20 | 0.00 | same label |
| Revenue from operations | 20 | half-year | 4390.54 | 43905.40 | 0.00 | same label |
| PAT | 20 | half-year | 837.15 | 8371.50 | 0.00 | same label |
| Total assets | 24 | instant | 27499.04 | 274990.40 | 0.00 | same label |
| Cash and cash equivalents, balance sheet | 24 | instant | 33.40 | 334.00 | 0.00 | same label |
| Current borrowings | 26 | instant | 1479.18 | 14791.80 | 0.00 | same label |
| Operating cash flow | 28 | half-year | 1306.13 | 13061.30 | 0.00 | same label |
| Investing cash flow | 28 | half-year | -3461.00 | -34610.00 | 0.00 | same label |
| Financing cash flow | 28 | half-year | 331.34 | 3313.40 | 0.00 | same label |
| Cash flow closing balance | 28 | instant | 561.72 | 5617.20 | 0.00 | same label; broader than balance-sheet cash |
| Quarter total expenses | 20 | quarter | 1702.41 | 17020.40 | -3.70 | numeric conflict |
| Quarter other expenses | 20 | quarter | 300.15 | 3001.40 | -0.10 | numeric conflict |
| Half-year tax expense | 20 | half-year | 309.38 | 3093.90 | 0.10 | numeric conflict |
| Capital work in progress | 24 | instant | 5290.27 | 57374.00 | 4471.30 | numeric/classification conflict |
| Intangible assets | 24 | instant | 8.27 | 16913.60 | 16830.90 | numeric/classification conflict |
| Non-current lease liabilities / NSE non-current borrowings | 24 | instant | 143.96 | 1439.60 | 0.00 | equal number; different label |
| Deferred tax liabilities / NSE other non-current liabilities | 24 | instant | 583.35 | 5833.40 | -0.10 | different label and number |
| Cash generated from operations | 28 | half-year | 1530.97 | 15681.40 | 371.70 | numeric/classification conflict |
| PPE purchases, signed / NSE purchase amount unsigned | 28 | half-year | -1003.78 | 5566.50 | 15604.30 | sign convention and amount differ |
| Investment income / NSE dividends received | 28 | half-year | 37.17 | 371.70 | 0.00 | equal number; label not established equivalent |
