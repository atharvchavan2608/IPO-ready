# IPO-Ready
## A Python Analytics Project for Evidence-Based IPO Research

Programming Analytics Lab Project

Team members: Abdul, Ankit, Atharv, Kabeer, Sailaja, Utkarsh.

### Project summary

IPO-Ready proposes a Python-based analytical workflow that helps investors understand and compare the financial position of Indian IPO issuers. It will turn selected prospectus disclosures into structured financial observations, calculate transparent indicators, visualise trends and produce an evidence-linked research report. An agent-assisted research layer will coordinate analytical tools and highlight questions that need human judgement.

The project begins as a programming analytics submission. Its central contribution is the Python data pipeline, analytical methodology and measurable evaluation. A lightweight website presents the results; it is not the main academic contribution. Broader company coverage and professional research workflows are longer-term extensions.

### Problem and intended users

An investor comparing an IPO issuer with listed companies must read lengthy documents, distinguish operating revenue from total income, align annual and interim periods, and reconcile inconsistent accounting definitions. A confident explanation is insufficient if its inputs or calculations cannot be checked.

The intended audience includes individual investors investing small amounts, experienced direct investors, and analysts at brokers or investment firms. The initial pilot will serve a shared task: understand an issuer's financial trends and identify questions worth investigating. A plain-language view will explain the results; an analyst view will expose figures, definitions, assumptions and document references. Institutional integration and personalized portfolios are outside the initial submission.

### Research question and objectives

Can a reproducible Python workflow make selected IPO financial analysis easier to inspect and compare, while preserving source evidence and unresolved uncertainty?

- Prepare a structured dataset from public issuer disclosures, retaining units, periods, statement basis and source locations.
- Calculate growth, profitability, liquidity/leverage where supported, and operating cash conversion using explicit formulas.
- Compare suitable issuers or peers while identifying material differences in accounting basis and business model.
- Produce visualisations and a concise research report whose material numerical claims can be traced to evidence.
- Evaluate data correctness, calculation correctness, evidence coverage and usefulness on a small, manually reviewed sample.

### Deliverables for today's discussion

A working historical Aether demonstration already uses the transcribed research pilot: 22 metrics across five reporting periods, Python calculations, arithmetic checks, period selection, evidence links, review flags and a downloadable analysis record. Its narrative and workflow routing are deterministic. Live LLM planning, automated PDF extraction and peer valuation have not yet been implemented. This proposal describes the intended project, not completed autonomous capabilities.

---

## Analytical scope and Python methodology

### Bounded first version

Proposed submission scope: three historical non-financial Indian IPO issuers and up to five listed peer candidates, subject to document availability and course time. Aether is the first case; Clean Science and Fine Organic are candidates requiring the same verification. Restricting the first sample to a comparable sector reduces, but does not remove, peer-selection difficulties. The sample is a feasibility study, not a statistically representative investment backtest.

The minimum end-to-end version will cover two issuers with reviewed inputs. The stretch version adds a third issuer, assisted extraction, justified peers and clearly labelled valuation scenarios. A general financial-health probability, listing-return prediction, universal XBRL parser and real-time market feed are excluded from the first version.

### Data preparation and analysis

1. Collect dated public RHP/DRHP documents and relevant annual reports. Preserve original files, source URLs, checksums and document dates. Historical reports reconstructed today will be labelled retrospective.
2. Extract candidate tables with Python PDF tools and verify selected values manually. Use pandas for reshaping, cleaning and joining. Keep reported values separate from normalized values; do not replace missing entries with zero.
3. Model each observation with company, metric, raw value, unit, period start/end, standalone/consolidated basis, page reference and review status. Preserve conflicting observations rather than silently selecting one.
4. Calculate indicators in Python and test accounting bridges. Annual and interim comparisons use matching periods. Chart annual trends separately from interim observations.
5. Add peer comparisons only after checking sector, business model, scale, reporting period and statement basis. Record why a candidate was included or rejected.
6. Publish a research report with visualisations, calculation definitions, findings, limitations and evidence links.

### Initial analytical indicators

- Revenue growth and CAGR: use elapsed years between comparable annual endpoints; no growth rate when the mathematical assumptions fail.
- Profitability: PAT margin and EBITDA margin, with the revenue denominator and EBITDA treatment of other income stated explicitly.
- Cash conversion: operating cash after tax divided by PAT, interpreted with working-capital context. A weak ratio is a question for investigation, not proof of distress.
- Leverage: borrowings/equity, with lease treatment stated. Cash deductions require an explicit policy on bank balances and restrictions.
- Valuation extension: transparent peer-multiple scenarios with dated prices and consistent earnings/share definitions. These are conditional illustrations, not validated fair-value predictions.

### Scoring decision

The core deliverable will show a financial profile rather than a single overall score. If time permits, the team will compare a documented rule-based score with its underlying indicators. Piotroski's historical F-score is a literature baseline, not automatically suitable for Indian IPOs and not a calibrated distress probability. No arbitrary weighted score will be presented as predictive accuracy.

### Programming analytics learning

The work exercises Python functions and modules, structured data, pandas transformations, exploratory analysis, ratios and growth mathematics, plotting, exception handling, file/API boundaries, reproducible experiments and testing. Suggested tools are pandas, NumPy, matplotlib or Plotly, a PDF extraction library, and a lightweight presentation layer. Final dependencies will follow the course environment; the current demo uses Python's standard library and requires no API key.

---

## Agent-assisted research design

### What makes the proposed system agentic

The target agent will receive a research objective, inspect available evidence, choose from a bounded set of tools, assess their results and decide whether to continue, request review or stop. A chatbot that merely writes a financial summary will not meet this objective. One orchestrator with well-defined tools is sufficient initially; multiple named agents are optional, not a goal in themselves.

Proposed flow: investor question -> research plan -> evidence retrieval -> candidate extraction -> Python validation and calculations -> discrepancy investigation -> human review where needed -> cited report -> archived run record.

### Tool and responsibility boundaries

- Research orchestrator: proposes tasks, tracks missing evidence, selects tools, recommends peer candidates and drafts explanations. Its proposed actions and outcomes are logged.
- Python analytics tools: perform transformations, arithmetic, ratio calculations and scenario computation. Numerical answers must come from tool outputs rather than unsupported model arithmetic.
- Evidence tools: return document passages, tables and source metadata. Retrieved documents are data, not instructions; tool permissions and permitted source locations are bounded.
- Reviewer: resolves ambiguous figures, approves peer choices and reviews material interpretations. A human decision and its rationale are recorded separately from the original observation.
- Report assembler: includes verified calculations and their references, labels unreviewed claims and withholds outputs whose required inputs are unresolved.

### A concrete agent task

Question: "Revenue and profit grew; did cash generation keep pace?" The agent locates same-period operating cash flow and PAT, requests the Python ratio tool, examines relevant working-capital disclosures and drafts an explanation with citations. If it finds mismatched periods or conflicting repeated figures, it opens a review item and identifies what evidence is missing. It must not repair a date or value silently.

### Current implementation versus planned capability

Implemented now: curated evidence loading, deterministic period selection, four arithmetic checks per selected period, ratio calculation, known review flags, a template explanation and an exportable trace. The trace accurately represents executed Python steps.

Planned: model-selected tool calls, iterative evidence investigation, assisted extraction, peer reasoning and cited narrative generation. If model access is unavailable, the deterministic analytics baseline remains demonstrable, but the team will report that agent objectives are incomplete. LLM integration is a separate milestone with a budget limit and measurable evaluation.

### Why the preliminary research matters

The survey examined financial-analysis papers, products and GitHub implementations. Aether reconciliation revealed how definitions change EBITDA, debt and EPS interpretation. XBRL inspection revealed that structured data can still contain conflicting periods and classifications. These observations justify evidence retention and review controls. They do not establish broad market demand, comprehensive source coverage or superior investment performance.

---

## Evaluation, delivery plan and references

### Evaluation design

Create a reviewed reference set of at least 60 selected observations across two issuers, with a second team member checking the entries. Extend to the proposed three-issuer sample if time allows. Reserve a separate document or reporting period for testing assisted extraction so the system is not assessed only on its development examples.

- Input accuracy: compare value, unit, period, basis and citation separately against the reference set. Report coverage, errors and abstentions; do not report an overall accuracy percentage without its denominator.
- Calculation correctness: test known results and edge cases including zero/missing denominators, negative CAGR endpoints, unequal period lengths and accounting reconciliation differences. Acceptance target: all implemented deterministic calculation tests pass.
- Evidence completeness: target a valid source location and formula/input lineage for every material numerical claim in the generated report. Manually review citation relevance; a working link alone is insufficient.
- Agent behaviour: use at least ten bounded tasks, including missing data and conflicting disclosures. Record completion, correct escalation, unsupported claims, tool calls, latency and model cost. Compare with the same workflow without model routing.
- Investor usefulness: ask a small convenience sample of individual investors and, if accessible, an analyst to complete defined comparison tasks. Record comprehension, errors, time and feedback. Treat this as exploratory feedback, not proof of market demand.

### Proposed six-week delivery sequence

- Week 1: confirm course rubric; approve scope, observation schema, metric definitions and reference-set protocol. Demonstrate the current Aether baseline.
- Week 2: verify a second issuer, build the pandas preparation pipeline and implement meaningful calculation tests. Gate: two-issuer data and repeatable analysis.
- Week 3: add charts, reviewed peer candidates and report export. Gate: evidence-linked end-to-end report with unresolved inputs visible.
- Week 4: integrate a bounded tool-using agent and human-review handoff. Gate: real tool-call logs, failure handling and budget limits; no simulated autonomy claim.
- Week 5: run held-out extraction and agent evaluations, collect investor feedback and fix material failures.
- Week 6: package the application, notebook, methodology, evaluation results and demonstration. The schedule is a proposal and will adapt to the professor's deadline.

### Risks and feasible fallbacks

Poor PDF extraction: narrow the document sample and retain manual verification. Exchange access failures: use issuer-hosted reports and curated snapshots; defer bulk XBRL ingestion. Weak peer comparability: show financial profiles without a valuation conclusion. Limited model access: preserve the Python baseline and disclose the incomplete agent milestone. No historical outcome claims will be made without a properly separated evaluation dataset.

### Expected submission

Python source and reproducible notebook; reviewed sample dataset and data dictionary; interactive demonstration; evidence-linked reports; evaluation results; research bibliography; and a short explanation of limitations and future work. Public source availability will be distinguished from redistribution permission before sharing a dataset externally.

---

## Selected references and supporting evidence

- Piotroski, J. D. (2000). Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers. Journal of Accounting Research, 38, 1-41. https://www.ivey.uwo.ca/media/3775523/value_investing_the_use_of_historical_financial_statement_information.pdf
- Purnanandam, A. K., and Swaminathan, B. (2004). Are IPOs Really Underpriced? Review of Financial Studies, 17(3), 811-848. https://doi.org/10.1093/rfs/hhg055
- Chen et al. (2021). FinQA: A Dataset of Numerical Reasoning over Financial Data. https://arxiv.org/abs/2109.00122
- Zhu et al. (2021). TAT-QA: A Question Answering Benchmark on a Hybrid of Tabular and Textual Content in Finance. https://arxiv.org/abs/2105.07624
- Aether Industries (2022). Red Herring Prospectus, dated 16 May 2022. Primary financial evidence, selected pages reviewed. https://www.sebi.gov.in/sebi_data/attachdocs/may-2022/1652869529567.pdf

The full Markdown research register records 58 survey/audit entries and their review depths. The references above inform the proposed methodology; they do not independently validate the prototype or its applicability to Indian IPOs.
