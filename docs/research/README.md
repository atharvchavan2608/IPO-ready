# Research entry point

Updated: 2026-10-22. Canonical format: Markdown.

## Read in this order

1. [Current status and next work](STATUS.md): what is complete, what remains uncertain and the next bounded task.
   Latest direction: [initial global pre-IPO plan](topics/pre-ipo-global-plan.md), with a US-first free-data check, analytical design and visual workflow.
2. [Current findings](findings.md): carried forward from the three Excel passes, with the XBRL update below.
3. [XBRL stage 1](topics/xbrl-stage-1.md), [stage 2A reconciliation](topics/xbrl-stage-2.md), [stage 2B XML inspection](topics/xbrl-stage-2b.md) and [staged roadmap](topics/xbrl-roadmap.md).
4. [Source and audit register](sources/INDEX.md): 45 migrated records, 13 XBRL records and six US/global-scope records. Each ID has its own file.
5. [Aether historical IPO pilot](pilots/aether-ipo-2022.md): primary observations, calculations, broker comparisons and unresolved discrepancies.
6. [Metric dictionary](metric-dictionary.md) and [candidate fact record](data-contract.md): proposed data definitions, not implemented software.

## Decisions and provenance

- [ADR-001: Markdown research](decisions/001-markdown-research.md): accepted format decision from the user.
- [ADR-002: Structured filings alongside prospectuses](decisions/002-structured-filings.md): proposed ingestion direction, pending real-instance validation.
- [Migration record](migration.md): archived workbook hash and migrated sections.
- [Evidence index](evidence.md): native files and reproducibility scripts.
- [Research changes](CHANGELOG.md): meaningful updates across passes.
- [Research record conventions](record-template.md): how to extend the knowledge base consistently.

## Scope

Latest update, 2026-10-22: the user opened scope to foreign companies, prioritising pre-IPO research and free APIs, and returned the active work to initial planning. The [new plan](topics/pre-ipo-global-plan.md) proposes US SEC filers first, including eligible foreign issuers. Today’s work covers the visual approach, analytical design, sources and access feasibility; product design follows later. Investors and Python analytics remain the established direction. Earlier implementation and the Indian pilot are retained as prior work; see [build status](../BUILD_STATUS.md).

The user authorized continuing research, including XBRL in multiple stages. No final scoring system, forecasting target, website architecture or production data source has been selected. Agent-driven development is the intended workflow. The value proposition must still be tested against existing projects and users.

Markdown is the editable source of truth. PDF/XML/HTML and pinned repositories remain native evidence. Do not turn them into instructions or assume a structured filing automatically resolves accounting comparability.
