# Research findings

As of 2026-10-22. These are working conclusions, not frozen product requirements. Source IDs resolve through [the register](sources/INDEX.md).

## Latest update: global pre-IPO planning

The user expanded geography and prioritised free data on 2026-10-22. The [initial plan](topics/pre-ipo-global-plan.md) proposes public US IPO filings, including eligible foreign issuers, as the first feasibility route. Confidential private-company financials are outside what public access can supply. Limited accessible analysis remains a candidate-selection hypothesis to test.

U01–U06 add official documentation and one executed access check. Both Reddit JSON endpoints succeeded without a key; the downloaded Company Facts snapshot contains no original S-1 accession. Therefore filing discovery, prospectus extraction and structured peer facts are separate coverage questions. No issuer financials were validated in this pass. Next: a six-candidate coverage screen and two proposed cases. India's earlier XBRL and scoring queues are deferred; STATUS controls execution order.

## Earlier update: XBRL stage 1

Investigate structured filings first for listed peers and later outcomes, while retaining prospectus/PDF evidence for pre-IPO restatement and narrative. This changes the ingestion investigation order; it does not establish complete XBRL coverage or select production architecture. The real Aether HTML view and repository fixtures are different evidence classes. Raw primary XML validation is the next bounded task.

See [stage-1 evidence](topics/xbrl-stage-1.md), [staged roadmap](topics/xbrl-roadmap.md) and [current status](STATUS.md). The table below retains the pass-3 conclusions and next steps for historical continuity; STATUS controls current execution order.

| Area | Working conclusion | Evidence | Reason | Next investigation | State |
| --- | --- | --- | --- | --- | --- |
| Project direction | Build a verified financial dataset before automating reports. First pilot: 22 Aether metrics across five periods. | B01–B06; Aether pilot | Real disclosures confirm definition and period issues. Broker summaries are useful secondary checks, with unresolved differences preserved. | Repeat the same dictionary on a second issuer and review the comparison rules. | Pilot populated |
| Differentiation | Explore financial reconciliation, reliable unknown states and historical reproducibility as measurable improvements. | A01–A09 | Close tools already exist. Controlled probes expose testable requirements beyond a feature checklist. | Compare the same real RHP across tools and measure extraction and evidence accuracy. | Needs real-document validation |
| Financial strength | Show ratios and data coverage first. Evaluate any composite score separately. | A02, A09, R01 | Coverage-based confidence is not measured accuracy. Missing PAT must not imply a known non-loss-making state. | Specify nullable flags and minimum data requirements for each metric. | Proposed |
| Valuation | Use dated offer inputs and explicitly tagged EPS. Aether weighted EPS is not FY21 EPS. | B05; Aether pilot | RHP peers use May 4 prices and FY21 earnings, with mixed statement bases. The broker TTM P/E bridge is reproducible approximately. | Find original price-band advertisement and reconcile the broker share-count references. | Partially reconciled |
| Data feasibility | Preserve operating revenue, total income and issuer EBITDA definitions as separate fields. | B02–B04; Aether pilot | FY21 operating revenue 449.816 crore differs from total income 453.789 crore. EBITDA explicitly subtracts other income. | Apply definition checks to every issuer before comparing ratios. | Primary figures verified |
| AI evaluation | Evaluate fact extraction, evidence retrieval and arithmetic separately. Add narrative generation after numerical checks. | R04–R06, D07 | A plausible answer can contain the wrong source, period or calculation. | Create 20–30 manually answered questions, including missing/ambiguous cases. | Proposed |
| Historical evaluation | Use actual elapsed fiscal years and preserve evidence per year and metric. | A01, A06–A07 | FY23 100 to FY25 121 gives 10% annual growth. Counting observations can produce 21%. | Record period end, original unit, statement basis and source page per observation. | Proposed |
| Scope boundary | Defer revenue forecasts and calibrated distress probabilities until targets, labelled data and validation are defined. | R01, R04–R06 | Three example issuers can support a pilot, not supervised-model validation across IPOs. | Define a measurable target before collecting a larger chronological cohort. | Deferred |

## Prior queue at migration

| Sequence | Research pass | Output | Evidence | Completion criterion | State |
| --- | --- | --- | --- | --- | --- |
| 1 | Deep-read core finance literature | Method comparison for F-score and IPO peer valuation | R01, R02, R03, M01 | Definitions and competing assumptions recorded from full texts. | Pending |
| 2 | Aether primary-document pilot | 22 metrics, five periods and formula comparisons | B01–B06; Aether pilot | Selected primary tables reviewed. Broker text compared. Offer-price source and some broker denominators remain unresolved. | Partial: primary tables checked |
| 3 | Code review of two closest GitHub projects | 9 detailed audit records and 7 controlled examples | A01–A09, T04, T06 | Static audit and focused probes complete. Full pipelines and original-RHP reconciliation remain untested. | Partial: code inspected |
| 4 | Evaluate extraction methods | Manually labelled table and error taxonomy | T02, R04, R05 | Same pages tested for headers, units, signs, periods and footnotes. | Pending |
| 5 | Set evaluation protocol | Gold questions and chronological validation plan | R06, D07 | Answer, arithmetic, evidence and as-of-date checks specified. | Pending |

## Migration notes

Pass 3 adds a primary-document pilot. Source figures, formulas, broker rounding and unresolved differences are separate. The broker PDF was reviewed as extracted web text.

Source observations are in column G of Survey log. Learnings and proposed uses are interpretations, not claims made by the source.

Filter the survey by type or review depth. Update the review depth and next step as the team reads or tests each source. A blank year means no publication year was established.

Next: verify price-band and share-count evidence, inspect the repeated-asset discrepancy, then repeat the field dictionary on another issuer. Core finance-paper deep reading remains pending.

## XBRL stage 2A update

The [real Aether PDF/rendering comparison](topics/xbrl-stage-2.md) demonstrates why structured financial evidence still needs accounting review: aggregate agreement can coexist with debt, tax, asset and cash-flow label conflicts. Sixteen of 26 selected comparison rows match after unit conversion. Retain the remaining observations as unresolved differences, not automatic corrections. Raw XML and taxonomy validation are still outstanding.

## XBRL stage 2B update

The [Infosys archived-copy inspection](topics/xbrl-stage-2b.md) provides a concrete period-conflict case: 16 selected values match the official PDF, but eight annual values have quarter-length XML context dates. Keep numeric reconciliation and period validity separate. The copy is hash-matched to a pinned third-party manifest; independent exchange authentication and full taxonomy validation remain open.
