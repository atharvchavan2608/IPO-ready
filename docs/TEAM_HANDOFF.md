# Team handoff

## V1-to-V2 upgrade, 24 November 2026

Start with the [V2 brief](starter-kit/PROTOTYPE_BRIEF.md), [starter prompts](starter-kit/PROMPTS.md) and [owner steering](starter-kit/steering.md). The [V1 handoff archive](../archive/v1-handoff-20261124/README.md) records the baseline, its open review findings and reproducible examples.

## Historical handoff, 12 November 2026

Commands and source paths in this section record the original repository layout. For isolated reproduction, use the archive instructions.

For a fresh session, read the [detailed continuation log](SESSION_LOG_2026-11-12.md): user priorities, implementation map, exact source runs, archive/Git state, checks, limitations and next-task completion criteria.

Updated: 2026-11-12. Latest user direction: staged construction of an interactive investor portal for unlisted/pre-IPO companies, free data first, recent IPO references, and learning company-specific analyst reasoning from Chittorgarh and expert reports.

Read [current architecture](architecture/CURRENT_ARCHITECTURE.md), [strategy/checklist](product/BUILD_STRATEGY.md), [research status](research/STATUS.md) and [build status](BUILD_STATUS.md). The full latest GitHub architecture package is copied and pinned under `docs/architecture/`; it is a target proposal, while `CURRENT_ARCHITECTURE.md` records actual implementation.

## Run and verify

`python -m portal.main` served the November app at http://127.0.0.1:8766. Its original application folder was `portal/`; the October demo and survey builders are in the [earlier archive](../archive/legacy-20261022/README.md). Runtime used Python's standard library.

```powershell
python -m unittest discover -s tests -v
python research/validate_markdown_research.py
python -m portal.snapshot
```

The optional browser script is `python scripts/check_portal.py`, with the server running and Playwright/Chrome already installed. Tests verify arithmetic/contracts and interactions, not issuer reporting or investment accuracy.

## What exists

- IGX active pre-IPO candidate; dated IEX transcript provides offering context. NSE reference is correctly classified as a September-2026 IPO rather than relying on a stale provider category. NSDL is discovery-only.
- Thirty provisional secondary observations across two companies and three annual periods, with exact WWIPL row/year anchors and native hashes. Unknown statement basis remains unknown.
- Interactive annual trends, ratios, history, formula/source inspection, one-year assumption sensitivity, coverage/reference exclusions and snapshot download.
- A proposed analyst-claim/evidence contract informed by the Chittorgarh index and two selected broker notes. No AI model or individual Davda article evaluation.

## Former next task: IGX primary reconciliation

Acquire one accessible official IGX financial statement covering FY25/FY26 (prefer a clearly linked issuer/DRHP source). Retain native bytes and hash. Reconcile the selected operating revenue, other income, total income, continuing profit and CFO; identify reporting basis, dates and cash-flow composition. Save mismatches and definition ambiguities as exceptions instead of overwriting provider observations. Update N05/N06 and topic/status/register together where evidence changes.

After that, implement one reusable source adapter and candidate/review persistence. Then add compatible reference/cohort work. Do not build all pending ranking, valuation, jobs, accounts and AI systems in one pass. Specific individual expert-article tracing is a later bounded method task.

## Preserve

Earlier 64 source IDs, Aether research and XBRL/SEC findings remain useful. Current N01-N10 add design, provider/status and expert-method evidence. Native evidence lives under `research/`; the archive manifest proves original demo code bytes were preserved. No commit, push or hosted publication is implied by this local handoff.
