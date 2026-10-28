# Excel-to-Markdown migration

- Completed: 2026-10-22
- Source snapshot: [IPO_Ready_Research_Survey_Pass3.xlsx](../../outputs/ipo-ready-survey-20261022/IPO_Ready_Research_Survey_Pass3.xlsx)
- Source SHA-256: `40b536c800e0a1b8c587dbbeb2f3e947874d489888d8164258d74aa130a1abb4`
- Migrated: 45 survey records, all 16 columns, eight findings, five queue items, existing usage notes, 110 primary pilot observations, eight broker comparisons, 20 derived/input measures and 20 reconciliation residuals.
- IDs are unchanged. Repeated underlying URLs were not collapsed because paper, code and published-data reviews have different evidence scope.
- Publication years and review dates were preserved. Blank years are explicitly not established.
- Formulas and cached results are preserved as audit references. Markdown does not recalculate them.
- The workbook and its builder are historical snapshots. Future research edits belong in Markdown. Do not rerun old builders over canonical notes.
- Native PDF/XML/HTML, downloaded third-party source snapshots and small reproducibility scripts remain in `research/` as evidence, not as the canonical research narrative.

The stage-1 XBRL research is added after this migration and was not part of the Excel source.
