# ADR-001: Maintain canonical research in Markdown

- Status: accepted.
- Date: 2026-10-22.
- Decision authority: user explicitly requested migrating the entire research from Excel into plain Markdown for agent-driven development.

## Decision

Use small linked Markdown records under `docs/research/`, with stable source IDs, a central status file, topic synthesis, decisions, open questions and pilot data. Keep native evidence separately. Excel workbooks remain archived snapshots and are no longer the research authoring target.

## Consequences

Agents can search, diff and update individual evidence records without loading a workbook. Narrative claims and proposals remain distinguishable from facts. Numeric tables do not recalculate in Markdown: preserve formulas and verified results, and rerun a targeted calculation when inputs change.

## Migration

All existing records and pilot sections were retained. See [migration details](../migration.md). Future changes should edit Markdown directly; the one-time migration script refuses to overwrite an existing register.
