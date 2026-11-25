# Build status

## V1 baseline and V2 setup, 24 November 2026

The [V2 starter kit](starter-kit/PROMPTS.md) is ready for a fresh session. The runnable V1 in `ipo_ready/` and `site/` supplies the upgrade baseline. The [V1 handoff archive](../archive/v1-handoff-20261124/README.md) contains its requirements, report, review and previews.

## Historical exploration, 12 November 2026

The 12 November exploration tested incremental construction of an interactive unlisted/pre-IPO investor portal. See the [historical architecture](architecture/CURRENT_ARCHITECTURE.md), [staged strategy](product/BUILD_STRATEGY.md) and [archive reproduction notes](../archive/portal-exploration-20261123/README.md).

## Milestone 1 local prototype

- Original application path: `portal/`. Four views: company research, scenario lab, IPO references, evidence/coverage. Company/year selection, crore/million conversion, annual chart/history, source/formula dialog and JSON export worked in the local exploration.
- IGX: active pre-IPO candidate, dated offering evidence from IEX's October-2026 call. NSE: recent IPO reference, listing status corrected using issuer note 7 (physical PDF page 18). NSDL: reference discovery only; no financial cohort approval.
- Thirty checked secondary-provider observations across FY24-FY26; source labels, lexical values, dates, original units, unknown basis, evidence hashes and review states retained. No primary-reviewed financial facts yet.
- Deterministic Decimal calculations: revenue growth/CAGR, continuing-profit/operating-revenue percentage, CFO/continuing-profit and income-component residual. One-year revenue/profit sensitivity with explicit bounded assumptions and snapshot lineage. No AI, scoring, price target or approved peer valuation.

## Executed verification, 2026-11-12

| Command / action | Outcome | What it establishes |
| --- | --- | --- |
| `python research/prepare_unlisted_pilot.py` | 30 exact observations matched retained HTML; native hashes checked | Offline source-specific transcription reproducibility |
| `python -m portal.snapshot` | Prepared company JSON with input/code/snapshot identity | Reproducible projection; not publication approval |
| `python -m unittest discover -s tests -v` | Seven active tests passed | Arithmetic, missing/zero/loss states, period/basis/unit compatibility, scenario validation, HTTP contracts |
| `node --check portal/web/app.js` | Passed | JavaScript syntax |
| `python research/validate_markdown_research.py` | 74 source records, 705 migrated-field checks, zero broken active-document links | Research register/migration integrity; not financial validation |
| `python scripts/check_portal.py` | First sandbox attempt: process permission error; permitted retry passed | Four views, period/unit switches, negative cash conversion, evidence, Python sensitivity, download, reference status and mobile overflow |
| Desktop/mobile screenshots | Inspected at 1440px and 390px; mobile navigation improved after first pass | Local visual QA; see final [browser result](../archive/portal-exploration-20261123/outputs/portal/browser-check.json) |
| `scripts/archive_legacy.ps1` | 19 non-cache files moved and hash-verified | Superseded code preserved in [archive](../archive/legacy-20261022/README.md) |
| `python research/sync_design_baseline.py` | 16 files from exact GitHub commit retained and hashed | Local architecture baseline matches meeting branch source |

Final archive/baseline verification independently recomputed all 19 + 16 file hashes. Final browser pass used the current Python build and retained updated screenshots, including the mobile navigation adjustment. The preview server was stopped after QA; start it with the command in the portal instructions.

Screenshots: [desktop](../archive/portal-exploration-20261123/outputs/portal/dashboard-desktop.png), [mobile](../archive/portal-exploration-20261123/outputs/portal/dashboard-mobile.png). Financial validation, automated extraction accuracy and investment usefulness are separate unfinished checks. The source register has 74 records; validate research links and migration integrity with `python research/validate_markdown_research.py`.

## Former next task

Reconcile IGX's selected observations against a primary issuer statement: actual dates, basis, continuing-profit definition and cash-flow composition, with differences retained as exceptions. Then implement one reusable adapter/review path. Further cohort, valuation, saved-workspace, durable-job and AI milestones remain queued. No production deployment or Git push was performed.

## Historical proposal and proof of concept: 2026-10-22

Updated: 2026-10-22. Latest user direction returns active work to initial planning and opens scope to foreign pre-IPO companies, prioritising free APIs. See [current plan](research/topics/pre-ipo-global-plan.md). Python analytics remains the academic core; product design is later work. The existing India-focused proposal, PDF and demo below are prior artifacts and have not been revised to the new scope.

## Ready to review

- [Recreated two-page proposal](proposal/IPO_Ready_Project_Proposal.md) and [PDF](../output/pdf/IPO_Ready_Project_Proposal.pdf). The prior extended text is retained as [working notes](proposal/IPO_Ready_Extended_Working_Notes.md).
- [Discussion and demo guide](proposal/Presentation_Guide.md).
- [Reference guide](proposal/Reference_Guide.md): how the eight proposal references inform the financial method, dashboard and document-processing design.
- [Archived self-contained demo](../archive/legacy-20261022/outputs/poc/IPO_Ready_Demo.html): historical precomputed reports.
- [Archived Python app instructions](../archive/legacy-20261022/app/README.md) and [archived pandas notebook](../archive/legacy-20261022/notebooks/01_financial_analysis.ipynb).
- [Archived annual profile CSV](../archive/legacy-20261022/outputs/poc/aether_annual_profile.csv) and [archived report outputs](../archive/legacy-20261022/outputs/poc/all_reports.json).

## Implemented and verified

- Original engine uses the curated Aether historical pilot: 22 metrics and five periods. Period selection, monetary conversion, ratio calculation, four reconciliation checks, known review flags and a template explanation.
- Five Python regression tests pass, including all five periods, missing/zero denominators and CAGR elapsed-year handling.
- All notebook code cells executed successfully and produced the CSV. Notebook is saved with clean outputs for classroom execution.
- Offline browser smoke test passed with Chrome/Playwright: initial report, interim-period switch and 0.029x cash ratio, JSON download, no JavaScript errors and no page-level horizontal overflow at 390px. Downloaded JSON independently checked for period and ratio.
- Desktop/mobile screenshots inspected. The revised two-page proposal was rendered and both pages visually inspected. A numbered references section with publication details and links appears at the end, with matching in-text citations. AI assistance is a brief optional extension; Python analysis drives the proposal's milestones and evaluation.

## Important implementation limits

No live model or autonomous decisions, automatic extraction, peer valuation or overall score. Known issues are supplied from prior research; the app does not claim to discover them autonomously. The source pilot remains manually transcribed and not fully adjudicated.

The Python HTTP server starts, but this environment's localhost browser connection timed out. HTTP/browser end-to-end behaviour has not been verified. The tested offline bundle avoids that dependency for today's demonstration. Use `python scripts/build_demo_snapshot.py` to regenerate it from current Python calculations.

## Previous proposed build milestone — deferred

Confirm the course rubric, then prepare a second issuer with the same schema and pandas analysis. Gate: reproducible two-issuer output with a reviewed reference set and meaningful calculation tests. Next add bounded model-selected tool calls with genuine execution logs, failure handling and cost controls. Keep the existing deterministic baseline for comparison.

Investor audience is confirmed by the user and includes small individual investors through broker analysts. Other scope choices in the proposal are team-reviewable recommendations, not claims that the team already approved them.
