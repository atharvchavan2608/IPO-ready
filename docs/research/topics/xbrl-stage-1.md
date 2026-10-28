# XBRL stage 1: source and format reconnaissance

- Date: 2026-10-22.
- Status: bounded reconnaissance complete. Real-instance acquisition and validation remain stage 2.
- Scope agreed with user: proceed in multiple stages; do not attempt a universal XBRL ingestion system now.

## Main conclusion

XBRL deserves an early feasibility test for listed peers and post-listing outcomes. It can reduce PDF extraction, but does not remove definition, period, entity or revision problems. It is not yet an established replacement for pre-IPO restated statements or prospectus narrative.

## Three routes to distinguish

| Route | Evidence | Potential role | Unresolved |
| --- | --- | --- | --- |
| NSE/BSE financial-result XBRL | NSE publishes filing/taxonomy resources; real Aether exchange rendering inspected | Listed-peer and later-outcome financials | Raw instance acquisition, historical coverage and exact taxonomy versions |
| MCA statutory financial-statement XBRL | XBRL India distinguishes C&I and Ind AS taxonomies; MCA filing manual reviewed | Potential fuller annual statements and notes | Public access route, retrieval cost, company coverage and version availability not tested |
| RHP/DRHP and signed result PDFs | Existing Aether pilot | Pre-IPO restatement, offer terms, business/risk narrative and reconciliation | No general prospectus-XBRL source established |

Sources: [X01](../sources/X01.md), [X02](../sources/X02.md), [X03](../sources/X03.md), [B01–B06](../sources/INDEX.md).

## Format is an observation, not a filename assumption

1. A plain XBRL instance contains facts, contexts and units, normally with a taxonomy reference.
2. Genuine inline XBRL embeds tagged facts in HTML. Numeric extraction must account for transformations, sign and scale.
3. An exchange HTML rendering can be a human-readable output. A filename containing `iXBRL_WEB` alone does not prove that raw fact tags/context structures are embedded.

The real Aether page was reviewed as rendered text. Its underlying bytes could not be downloaded in this stage, so its embedded markup and linkage to a specific raw XML file were not verified. Do not feed this evidence into an XML parser and label the task complete.

## Real filing inspected: Aether, September 2025

Source: [official exchange rendering](https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_127119_13112025150257_iXBRL_WEB.html), recorded in [X02](../sources/X02.md).

- Issuer identity: AETHER / ISIN INE0BWX01014 / scrip 543534.
- Standalone; unaudited; presentation in INR lakh.
- Quarter: 2025-07-01 to 2025-09-30. YTD: 2025-04-01 to 2025-09-30.
- Approval date shown: 2025-11-13. This is not a verified exchange publication timestamp.

Hand-transcribed examples below are from the HTML view, not a raw-instance extraction. This 2025 evidence must not enter a reconstructed 2022 assessment as a predictor.

| Measure | Quarter, INR lakh | YTD, INR lakh |
| --- | --- | --- |
| Operating revenue | 22472.00 | 43905.40 |
| Other income | 966.70 | 1284.90 |
| Total income | 23438.70 | 45190.30 |
| Finance costs | 181.00 | 506.20 |
| D&A | 1527.10 | 2808.80 |
| PBT | 6150.40 | 11465.40 |
| Tax expense | 1793.20 | 3093.90 |
| PAT from continuing operations | 4357.20 | 8371.50 |

Arithmetic spot-checks: operating revenue plus other income equals total income in both columns; PBT less tax equals PAT in both columns. To express these HTML monetary amounts in crore, divide by 100. This display conversion must not be blindly reapplied to a raw XML fact that already contains absolute INR.

## What the repository inspection teaches

### nse-xbrl

[X06](../sources/X06.md) records the pinned source. The parser separates generic XML extraction from financial field mapping, which is a useful boundary. Static inspection shows local-name keys discard namespace identity and omit unit/accuracy information from returned facts. Dictionary assignment can overwrite repeated same-key observations. Field mapping assumes named contexts; its mapping of a pre-exceptional pre-tax profit tag into an EBIT field also requires financial-definition review before using derived EBITDA. Full package and tests were not run.

### india-xbrl-filings

[X07](../sources/X07.md) separates discovery and byte-preserving storage from normalization. It records revisions, status and hashes, and its reader retains more fact metadata. It is a reference for acquisition design, not a proven normalized financial dataset. Its README includes personal/educational-use wording alongside an MIT code license; upstream access/reuse questions remain distinct.

### Taxonomy resolution

The vendored entry point inspected in [X08](../sources/X08.md) references imports and multiple linkbases. Downloading that XSD alone is not a complete taxonomy set. The repository resolver can substitute a schema filename's date with its package date. Such substitution is a compatibility hypothesis, not proof of semantic equivalence. Our proposed approach is to record the exact version and an unresolved mismatch rather than silently rename it.

## Fixtures inspected, without pretending they are company filings

| Fixture | Facts with contextRef | Context IDs | Units | Evidence class |
| --- | --- | --- | --- | --- |
| nse-xbrl sample_filing.xml | 61 | OneD, FourD, OneI, PY_I | 3 | Explicitly synthetic |
| india-xbrl sample_integrated_2025.xml | 5 | OneD, FourD, N1D | 1 | Repository test fixture; no real-company authenticity asserted |

XML well-formedness was checked with ElementTree. No XBRL/schema/filing-rule validation occurred. The different instant context name is already enough to reject the assumption that a fixed context-ID vocabulary is universal.

## What a fact needs

Retain full concept QName, entity, context dates and dimensions, unit, nil state, accuracy, source filing and revision. Read actual period semantics instead of inferring them from `OneD` or `FourD`. For inline data, scale and transformations are separate from XBRL decimals/precision. See [X04](../sources/X04.md), [X05](../sources/X05.md) and the [candidate record contract](../data-contract.md).

## Current recommendation

Investigate an established validator such as Arelle as a reference tool, then evaluate a narrow Indian normalization layer. Do not select a parser on README coverage claims alone. The immediate goal is a single real filing with 10–15 reconciled facts. Full historical coverage, additional sectors and agent orchestration come later.

## Learning resources added

- [FinTagging, X09](../sources/X09.md): numerical identification and concept linking are separate evaluation tasks.
- [HiFi-KPI, X10](../sources/X10.md): hierarchical KPI extraction and date errors are relevant evaluation patterns.

Both are abstract-level reviews. They do not validate Indian exchange mappings.
