# Learning analyst reasoning for a later AI pipeline

Updated: 2026-11-12. The user explicitly identified Chittorgarh's company analysis and expert strengths/weaknesses articles as a learning source. Current work is bounded method research; no model training, article-rewriting engine or automated recommendation pipeline was built.

## What was reviewed

[N08](../sources/N08.md): Chittorgarh homepage/review index, including its explanation of analysis sections and provider attribution. The captured index had zero individual review rows. Direct web-tool access returned 402, but native requests returned useful public HTML. No individual Dilip Davda article was acquired, and his particular methodology has not been claimed as reviewed.

[N09](../sources/N09.md): Canara Bank Securities' NSDL note dated 29 July 2025, hosted on Chittorgarh's report domain. Selected financial, strengths, risks and disclosure pages read; cover visually reviewed. [N10](../sources/N10.md): ICICI Securities' HDB review dated 25 June 2025, selected business/risk/valuation/disclosure sections from the broker's own host. These are two report examples, not a survey or validation of expert performance.

## Observations from the samples

The Chittorgarh index organises reviews around background, strengths, weaknesses, valuation, financials and ratings, and distinguishes providers. The Canara sample connects market position and income characteristics with peer-relative valuation, while discussing activity/technology exposures. ICICI's lending case uses loan-book/underwriting and funding context with a post-issue valuation footnote. These are attributed analyst positions rather than primary facts approved by IPO-Ready.

A concrete extraction issue: the Canara PDF's extracted cover text begins with an unrelated old issuer/date, while the rendered cover correctly shows NSDL and July 2025. Other selected pages also contain stale text strings. A parser must resolve visible identity, section context and provenance; first text/filename alone is insufficient. Native PDF, selected text and rendered cover are retained.

## Proposed reasoning contract

One claim record should contain: company ID; claim type (`reported_fact`, `calculation`, `management_statement`, `analyst_opinion`, `our_interpretation`, `hypothesis`); theme; source/author/date; public-availability cutoff; exact page/paragraph; supporting fact IDs; mechanism; opposing evidence; conditions/horizon; uncertainty; review state; and version. A strength is a claim whose mechanism and applicability must be explained, not a positive adjective assigned to a company.

| Research question | Needed evidence/model input | Portal output |
| --- | --- | --- |
| How does it make money? | Segments, pricing, recurring/transaction mix, concentration | Business drivers with cited scope and periods |
| Is growth translating into earnings? | Same-basis history, margins, exceptional/discontinued items | Trend plus earnings-quality bridge |
| Is cash available to owners? | CFO composition, client/settlement funds, capex, restrictions | Cash-flow explanation; unknown states retained |
| What supports a strength? | Market position, customer/product facts, economic mechanism | Attributed strength with evidence and caveat |
| What could weaken the thesis? | Competitive, operational, governance and regulatory disclosure | Company-specific weakness/risk and sensitivity |
| Is the offered valuation defensible? | Dated price, post-offer shares, earnings basis, compatible peers | Eligible multiples and assumption range |
| What information is absent? | Coverage map and unresolved exceptions | Open question, suppressed conclusion |

The table is our proposed specification inferred from samples and earlier research, not a claim that every provider follows this exact method. Generic corporate ratios do not substitute for sector analysis: lending asset-quality/funding measures differ from exchange transaction economics.

## Later pipeline and evaluation

1. Capture permitted sources and dated versions; resolve issuer/document identity.
2. Extract candidate numerical and narrative claims with exact anchors; separate reported quantities from analyst opinions and management assertions.
3. Reconcile selected quantities to issuer evidence; run deterministic metrics/compatibility checks.
4. Retrieve support and counterevidence for each research question. Missing evidence produces an explicit unanswered question.
5. Generate structured strengths, weaknesses, valuation assumptions and uncertainties from that evidence graph. Preserve attribution and avoid copying report prose or importing a broker rating as our truth.
6. Check citations, numbers, dates, contradictions and unsupported conclusions; review before publication. Store snapshot/model/prompt versions.

Start evaluation with three manually annotated company reports, including one current pre-IPO candidate and one recent IPO's pre-offer documents. Keep one company held out. Measure claim-type accuracy, evidence-location correctness, numeric agreement, unsupported claims and whether both supporting and opposing evidence are represented. Expert agreement is useful review evidence, not investment accuracy. Do not use later listing gains to validate an earlier reconstructed opinion without a separate point-in-time study.

Next research task after IGX reconciliation: acquire one clearly accessible individual Chittorgarh expert article and trace two claimed strengths and two weaknesses to its cited filing. Local methodological study does not establish permission for bulk republication or model training; source-specific access/reuse belongs in the adapter design.
