# XBRL stage 2B: archived Infosys XML inspection

Checked: 2026-10-22. Outcome: a repository-held copy attributed to a real Infosys FY24 filing was inspected and compared with the official results PDF. Primary exchange bytes and full taxonomy validity remain unverified. This is stronger than a synthetic fixture, but does not satisfy the original primary-download completion criterion.

## Provenance

- Discovery: [Financial-results-extraction-using-NSE-BSE-APIs](https://github.com/Jayadityas/Financial-results-extraction-using-NSE-BSE-APIs), pinned commit `80a93617604a043936c03d1fca88aef558fdacca`.
- [Pinned XML copy](https://github.com/Jayadityas/Financial-results-extraction-using-NSE-BSE-APIs/blob/80a93617604a043936c03d1fca88aef558fdacca/data/raw/nse/INE009A01021/financial_results/quarterly/fourth-2023-24/INDAS_104589_1099938_19042024112830.xml).
- [Pinned acquisition manifest](https://github.com/Jayadityas/Financial-results-extraction-using-NSE-BSE-APIs/blob/80a93617604a043936c03d1fca88aef558fdacca/data/metadata/filings_manifest.jsonl) attributes it to [this NSE URL](https://nsearchives.nseindia.com/corporate/xbrl/INDAS_104589_1099938_19042024112830.xml), Infosys, consolidated, audited, period end 31 March 2024. Manifest filing timestamp: 19 April 2024 11:28; manifest acquisition: 2 July 2026. Both are third-party metadata, not independently established timestamps.
- XML downloaded through the public GitHub blob API, blob `afe1b918152296c25d8bd846428ab39c2ef9f1de`. Raw GitHub URL returned 403; the public API returned the file. No credentials, proxy, cookie copying or access-control workaround was used.
- Size 108,706 bytes; SHA-256 `76b50cfcb43c474f7db3203627fe300165dcc54e7890d71eae416d7b838bb977`, matching the pinned repository manifest. A matching third-party hash does not prove exchange authenticity.
- Official comparison: [Infosys FY24 results page](https://www.infosys.com/investors/reports-filings/quarterly-results/2023-2024/q4.html) and its linked [results and auditors' reports PDF](https://www.infosys.com/investors/reports-filings/quarterly-results/2023-2024/q4/documents/q4-and-12m-fy24-financial-results-auditorsreports.pdf), physical page 13 (zero-based PDF page 12), consolidated Ind AS results, INR crore except EPS. Selected table reviewed using web-extracted text; no local PDF visual verification. Local PDF download returned 403, although the web tool could read it.

## Executed inspection

The [stdlib inspection script](../../../research/xbrl_stage2b_inspect.py) reads the saved copy, rejects DTD/entity declarations, preserves expanded fact names, raw text, context references, units, decimals and nil flags, and inventories context periods and dimensions. It does not resolve taxonomy schemas, infer XBRL defaults, perform dimensional validation or execute downloaded code.

Outputs: [native XML](../../../research/xbrl_stage2_20261022/infosys_fy24_repository_copy.xml), [acquisition record](../../../research/xbrl_stage2_20261022/infosys_copy_manifest.json), [full inventory](../../../research/xbrl_stage2_20261022/infosys_inventory.json), [comparison rows](../../../research/xbrl_stage2_20261022/infosys_comparison.json), [summary](../../../research/xbrl_stage2_20261022/infosys_summary.json), [same-aspect conflict candidates](../../../research/xbrl_stage2_20261022/infosys_same_aspect_conflicts.json).

Observed: 417 fact elements, 81 contexts, 4 units; 78 contexts contain dimensions. Zero facts have an explicit true nil flag. This does not establish complete reporting or mean every absent fact is zero.

## Taxonomy and units

- Concept namespace: `http://www.bseindia.com/xbrl/fin/2020-03-31/in-bse-fin`. An NSE-hosted source can use a BSE-named taxonomy namespace; do not infer the acquisition source from a concept prefix.
- Relative schema reference: `Ind-AS_entry_point_2020-03-31.xsd`. Exact official dependencies have not been acquired. The previously inspected 2025 integrated taxonomy is not a verified substitute for this 2020 entry point.
- Units: INR, pure, shares, INR/share. The full unit XML and namespace map are retained in the inventory.
- Monetary numbers are already in rupees; divide by 10,000,000 to compare with PDF crore. `decimals="-7"` describes stated numerical accuracy, not a multiplier. EPS uses INR/share and `decimals="INF"` in this file; preserve that claim without interpreting it as economically unlimited precision.
- Metadata identifies the report as consolidated. Retain this report-level field; it is not encoded as a standalone/consolidated dimension in the three non-dimensional contexts inspected here.

## Finding: context dates conflict with the annual reporting field

| Evidence | `OneD` | `FourD` |
|---|---|---|
| Context start | 2024-01-01 | 2024-01-01 |
| Context end | 2024-03-31 | 2024-03-31 |
| `DateOfStartOfReportingPeriod` fact | 2024-01-01 | 2023-04-01 |
| `RevenueFromOperations`, rupees | 379230000000.00 | 1536700000000.00 |
| Corresponding official PDF column | Quarter, 37,923 crore | Year, 153,670 crore |

Both contexts have the same entity, period and no dimensions. Yet their revenue values differ, and the `FourD` reporting-start fact disagrees with its own context. Eight quarter comparisons and eight annual comparisons match the official PDF numerically; only the eight quarter rows also match its period through the XML context.

The script finds 35 groups with differing text values under the same inspected concept/entity/period/dimensions/unit combination. This is a **conflict-candidate inventory**, not an Arelle duplicate-fact validation report: taxonomy defaults, datatype semantics and accuracy consistency were not evaluated. No statement is made about which party introduced the conflict. The primary file may differ from the repository copy.

Do not solve this by hardcoding `FourD = annual`. Also do not trust context dates alone when another explicit reporting field and the primary PDF disagree. Preserve both and quarantine the observation pending a documented resolution. Parsing the XML successfully does not make annual growth calculation safe.

## Further accounting observations

- Total annual profit is 26,248 crore; profit attributable to owners is 26,233 crore. Both are valid separate lines. EPS and shareholder valuation generally require a deliberate owner-profit definition rather than the generic PAT tag.
- The XML's assets note explicitly aggregates PPE with right-of-use assets and other non-current assets with tax assets. Thus some cross-format line differences can be disclosed aggregations. Read explanatory text alongside numeric tags before labelling every mismatch an error.
- This is an older financial-results taxonomy, not the 2025 integrated filing used in the Aether rendering. It establishes a concrete format difference to test later, not broad compatibility.

## Limits, queue and project decision

Direct NSE XML timed out. The explicit BSE FY25 alternative link returned 403. Saved [request outcomes](../../../research/xbrl_stage2_20261022/primary_xml_manifest.json) distinguish these failures from the successful GitHub API acquisition. Browser automation also failed to initialize; no UI download occurred. No production data access route has been demonstrated.

Keep XBRL as a promising listed-peer and post-listing input. Keep PDF/narrative reconciliation and human review in scope. Do not expand into bulk acquisition or universal parsing yet.

Stage 2C, deferred: obtain primary bytes, compare their hash with this archived copy, acquire matching official taxonomy dependencies, validate, then revisit period-conflict candidates and the Aether classification differences. A short literature pass on financial-strength scoring and IPO peer valuation should come next so data-access work does not consume the entire project research phase.

## Selected comparison rows

All monetary PDF values below are crore; EPS is INR/share. Numeric match and period match are separate results. Namespace `in-bse-fin` is given above; JSON retains expanded QNames.

| Concept (namespace `in-bse-fin`) | Context | Raw XML | Unit | Decimals | PDF p.13 | Numeric match | Context period match |
|---|---|---:|---|---|---:|---|---|
| RevenueFromOperations | OneD | 379230000000.00 | INR | -7 | 37923 | True | True |
| OtherIncome | OneD | 27290000000.00 | INR | -7 | 2729 | True | True |
| Income | OneD | 406520000000.00 | INR | -7 | 40652 | True | True |
| Expenses | OneD | 304120000000.00 | INR | -7 | 30412 | True | True |
| ProfitBeforeTax | OneD | 102400000000.00 | INR | -7 | 10240 | True | True |
| ProfitLossForPeriod | OneD | 79750000000.00 | INR | -7 | 7975 | True | True |
| ProfitOrLossAttributableToOwnersOfParent | OneD | 79690000000.00 | INR | -7 | 7969 | True | True |
| DilutedEarningsLossPerShareFromContinuingOperations | OneD | 19.22 | INRPerShare | INF | 19.22 | True | True |
| RevenueFromOperations | FourD | 1536700000000.00 | INR | -7 | 153670 | True | False |
| OtherIncome | FourD | 47110000000.00 | INR | -7 | 4711 | True | False |
| Income | FourD | 1583810000000.00 | INR | -7 | 158381 | True | False |
| Expenses | FourD | 1223930000000.00 | INR | -7 | 122393 | True | False |
| ProfitBeforeTax | FourD | 359880000000.00 | INR | -7 | 35988 | True | False |
| ProfitLossForPeriod | FourD | 262480000000.00 | INR | -7 | 26248 | True | False |
| ProfitOrLossAttributableToOwnersOfParent | FourD | 262330000000.00 | INR | -7 | 26233 | True | False |
| DilutedEarningsLossPerShareFromContinuingOperations | FourD | 63.29 | INRPerShare | INF | 63.29 | True | False |
