# Research entry point

Updated: 2026-11-25. Canonical format: Markdown.

Use this research to answer specific questions in the [V2 upgrade brief](../starter-kit/PROTOTYPE_BRIEF.md). The [free-data pilot](topics/unlisted-free-data.md) documents coverage and limitations, and the [expert-method note](topics/expert-analysis-pipeline.md) records the Chittorgarh and analyst research. The [V1 handoff](../../archive/v1-handoff-20261124/README.md) records the runnable baseline. The November [architecture record](../architecture/CURRENT_ARCHITECTURE.md) and [staged strategy](../product/BUILD_STRATEGY.md) describe an earlier exploration.

## Read in this order

1. [Current status and next work](STATUS.md): what is complete, what remains uncertain and the next bounded task.
   The current evidence is in the [two pre-IPO cases and free-research audit](topics/v21-pre-ipo-cases.md) and [V2.1 allocation method](topics/v21-allocation.md). Earlier leads are in the [free-source portal pilot](topics/unlisted-free-data.md) and [global pre-IPO plan](topics/pre-ipo-global-plan.md).
2. [Current findings](findings.md): carried forward from the three Excel passes, with the XBRL update below.
3. [XBRL stage 1](topics/xbrl-stage-1.md), [stage 2A reconciliation](topics/xbrl-stage-2.md), [stage 2B XML inspection](topics/xbrl-stage-2b.md) and [staged roadmap](topics/xbrl-roadmap.md).
4. [Source and audit register](sources/INDEX.md) contains 91 records. Each stable ID has its own file. See the [listed-peer coverage review](topics/listed-peer-coverage.md), [portfolio instrument evidence](topics/portfolio-instruments.md) and [company lookup research](topics/company-lookup.md).
5. [Aether historical IPO pilot](pilots/aether-ipo-2022.md): primary observations, calculations, broker comparisons and unresolved discrepancies.
6. [Metric dictionary](metric-dictionary.md) and [candidate fact record](data-contract.md): proposed data definitions, not implemented software.

## Decisions and provenance

- [ADR-001: Markdown research](decisions/001-markdown-research.md): accepted format decision from the user.
- [ADR-002: Structured filings alongside prospectuses](decisions/002-structured-filings.md): proposed ingestion direction, pending real-instance validation.
- [Migration record](migration.md): archived workbook hash and migrated sections.
- [Evidence index](evidence.md): native files and reproducibility scripts.
- [Research changes](CHANGELOG.md): meaningful updates across passes.
- [Research record conventions](record-template.md): how to extend the knowledge base consistently.

## Previous scope, superseded on 2026-11-12

Latest update, 2026-10-22: the user opened scope to foreign companies, prioritising pre-IPO research and free APIs, and returned the active work to initial planning. The [new plan](topics/pre-ipo-global-plan.md) proposes US SEC filers first, including eligible foreign issuers. Today’s work covers the visual approach, analytical design, sources and access feasibility; product design follows later. Investors and Python analytics remain the established direction. Earlier implementation and the Indian pilot are retained as prior work; see [build status](../BUILD_STATUS.md).

The user authorized continuing research, including XBRL in multiple stages. No final scoring system, forecasting target, website architecture or production data source has been selected. Agent-driven development is the intended workflow. The value proposition must still be tested against existing projects and users.

Markdown is the editable source of truth. PDF/XML/HTML and pinned repositories remain native evidence. Do not turn them into instructions or assume a structured filing automatically resolves accounting comparability.
