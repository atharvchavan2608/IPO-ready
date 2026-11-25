# Detailed continuation log: 12 November 2026

> Historical record of the [archived exploration](../archive/portal-exploration-20261123/README.md). For the next build session, use the [starter prompts](starter-kit/PROMPTS.md).

Purpose: resume in a fresh session without repeating discovery or confusing historical plans with current work. This records the completed implementation session and subsequent sample-company clarification. It does not assert new financial validation.

## User instructions and priorities

1. The local October design was outdated. Use the GitHub `architecture/fintech-product-design` branch as the latest product meeting proposal.
2. Build IPO-Ready for unlisted/pre-IPO company research; recent IPO companies supply references. Use unpaid sources initially, including WWIPL and UnlistedZone.
3. Deliver a client-facing interactive analytics portal with financial modelling, ratios and comparisons. A notebook report is insufficient.
4. Write a strategy, build prototypes and pipelines incrementally, tick off bounded tasks. Do not implement the entire architecture in one pass.
5. Learn company-specific analytical reasoning from Chittorgarh and expert articles, especially strengths, weaknesses and valuation arguments, to inform a later AI pipeline.
6. Archive superseded code while preserving useful research. Update local architecture to reflect both the meeting proposal and actual implementation decisions.
7. Latest request: create a detailed continuation log. No additional implementation/research milestone was requested in this logging turn.

## Resume reading order

Read root `AGENTS.md`, then [research entry](research/README.md), [research status](research/STATUS.md), [current architecture](architecture/CURRENT_ARCHITECTURE.md), [strategy/checklist](product/BUILD_STRATEGY.md), [contracts](product/DATA_CONTRACTS.md) and [build status](BUILD_STATUS.md). Earlier US-first planning and XBRL queues are retained history, not the automatic next task.

## Architecture baseline and decisions

- Exact GitHub commit: `5b71ab3e0fea6dff294519fc2f6560aad5a059aa`, dated 29 October 2026.
- Sixteen architecture files copied into `docs/architecture/`: framework, backlog, diagrams, PDF, editable drawio and builders. [Baseline manifest](architecture/BASELINE_MANIFEST.json) records exact URLs, native hashes and retrieval times. Remote builders were not executed.
- The complete package describes the target product. `CURRENT_ARCHITECTURE.md` separately describes implemented components and decisions D01-D08. Preserve that distinction.
- Target: React/TypeScript, modular Python/FastAPI, background workers, PostgreSQL and immutable evidence. Present prototype: standard-library Python plus buildless browser assets. This temporary choice validated contracts/workflow without installing a production framework; it is not a replacement production-stack decision.
- Separate facts, calculations, analyst/management claims and interpretation. Preserve unknown basis and dates; do not promote transcription checks into primary financial approval.
- No production hosting, accounts, durable jobs, approval workflow, ranking, valuation or trained AI was built.

## Sample companies: exact scope

| Company | Role | Financial data included |
| --- | --- | --- |
| Indian Gas Exchange (IGX) | Active pre-IPO candidate, with dated IEX transcript describing IPO in progress | 15 provisional WWIPL observations: five items in FY24, FY25, FY26 |
| National Stock Exchange of India (NSE) | Recent IPO reference, not currently unlisted in this dataset's status evidence | Same five items/three years, 15 provisional observations |
| National Securities Depository (NSDL) | Reference candidate/discovery only | No financial dataset or approved peer comparison |
| Aether Industries | Archived October prototype | No longer the active portal dataset; useful historical research retained |

Five annual items: operating revenue, provider-labelled Revenue provisionally mapped to total income, other income, continuing-operations profit and CFO. Thirty observations total, all secondary; zero primary-reviewed financial facts. The provider pages do not state standalone/consolidated basis. No accounting basis inferred from numerical similarity.

NSE was initially selected from WWIPL's unlisted category. Independent issuer evidence established BSE listing on 24 September 2026, so it was reclassified and IGX became the active case. This is a documented stale-category example. Status must remain independent of provider page classification. IGX status is dated evidence of an IPO in progress, not a guaranteed future listing schedule.

## Active implementation map

| Path | Responsibility |
| --- | --- |
| `portal/data/observations.json` | Authoritative prototype inputs, raw labels/lexemes, periods, states, source anchors/hashes and reference metadata |
| `portal/analytics.py` | Decimal calculations, eligibility rules and bounded scenario |
| `portal/snapshot.py` | Evidence/state validation; prepared projection; input/code hash and snapshot identity |
| `portal/main.py` | Loopback-only HTTP adapter |
| `portal/web/index.html`, `styles.css`, `app.js` | Four views, chart/table, company/year/unit selection, source dialog, scenario and export |
| `research/prepare_unlisted_pilot.py` | Offline exact-row/year whitelist adapter against two pinned HTML captures; rejects changes to selected values |
| `research/unlisted_source_probe.py` | Bounded public requests; separate immutable run directories; error bodies distinct from documents |
| `research/sync_design_baseline.py` | Explicit pinned architecture-package download |
| `tests/test_portal.py` | Seven active arithmetic/eligibility/API tests |
| `scripts/check_portal.py` | Optional Playwright/Chrome interaction and layout QA |
| `outputs/portal/` | Snapshot, downloaded export, browser-check JSON, desktop/mobile screenshots |

API: `GET /api/snapshot` (IGX), `GET /api/reference` (NSE), `POST /api/scenario`. The interface reads separate coherent company projections. References are not an approved peer cohort. Evidence/coverage screen is read-only, not an analyst review console.

Calculations: operating-revenue YoY, elapsed-year CAGR, continuing-profit/operating-revenue percentage, CFO/continuing-profit and total-income component residual. Negative CFO is preserved. Invalid/missing/nonpositive denominators suppress affected outputs. Cash conversion requires settlement/client-money interpretation; high values are not an automatic strength. Profit/revenue includes other-income effects and is not operating margin.

Scenario: one hypothetical year; growth bounded to -30% through +30%, assumed continuing-profit/operating-revenue percentage 0-100%. Explicit inputs, base fact and snapshot lineage returned. No probability or price target. Example tested: IGX FY26 revenue 61.01 crore, growth 10%, profit percentage 50% -> hypothetical revenue 67.1110 crore and profit 33.5555 crore.

## Evidence and research records

The source register has 74 stable records: earlier 64 unchanged plus N01-N10. See [register](research/sources/INDEX.md), [free-source findings](research/topics/unlisted-free-data.md), [expert-method proposal](research/topics/expert-analysis-pipeline.md).

- N01: pinned meeting architecture.
- N02: WWIPL NSE financial table.
- N03: UnlistedZone NSE direct-access failure; no facts imported.
- N04: NSDL listing identity, selected annual-report section, financial dataset absent.
- N05: WWIPL IGX financial table.
- N06: IEX call dated 30 October, filed 5 November 2026; physical PDF p7/printed p6 IPO paragraph. Newer interim figures exist but are excluded from annual prototype inputs.
- N07: NSE results dated 3 November 2026, physical p18 consolidated note 7 listing disclosure. Physical p26 has standalone notes.
- N08: Chittorgarh homepage/review-index structure; captured review index had zero article rows. No individual Dilip Davda article was acquired.
- N09: selected Canara Bank Securities NSDL note, hosted by Chittorgarh, dated 29 July 2025; cover visually inspected.
- N10: selected ICICI Securities HDB IPO review, dated 25 June 2025.

Native root: `research/unlisted_sources_20261112/`.

| Run folder | Outcome |
| --- | --- |
| `20261112T111108947979Z` | Four sandbox connection failures; no native financial bytes |
| `20261112T111129759444Z` | WWIPL NSE and NSE index 200; UnlistedZone 404; NSDL index TLS-chain failure |
| `20261112T111648125604Z` | WWIPL IGX, IEX transcript, Chittorgarh home, Canara and ICICI notes retained; NSE filing exceeded initial 5 MB cap |
| `20261112T111832347079Z` | Chittorgarh review-index HTML retained |
| `20261112T112913570549Z` | One explicit 16 MB cap retry retained complete 12,072,423-byte NSE issuer PDF |

Each successful native capture/error body has its hash in its run manifest. Keep failed runs; do not overwrite them. HTTP 200 alone is access evidence. Unknown publication/public-availability dates remain unknown; retrieval is not historical availability. This dataset is a retrospective reconstruction made on 12 November.

Expert learning is a proposed claim/evidence schema, not a trained model. A concrete parser issue was observed: Canara PDF extracted text contains stale unrelated company/date strings while its rendered cover correctly identifies NSDL. Validate identity using visible headings/context rather than first text or filename. Retained selected text and rendered cover support this observation. Do not copy report ratings as our factual truth or claim evaluated investment accuracy.

## Archive and working-tree state

- `archive/legacy-20261022/` contains the old app, notebook, outputs/poc, old engine test, four demo/proposal/browser builders and three root survey/source scripts.
- Nineteen non-cache files were moved and verified against original SHA-256 values; [archive manifest](../archive/legacy-20261022/manifest.json) retains original/new paths. Archived code retains old path assumptions and is not maintained as runnable.
- Useful research, native evidence, research scripts and historical proposals remain accessible. Do not revive old demo/Excel builders as current architecture or regenerate canonical Markdown from them.
- Work is local and uncommitted; `git status` includes old-path deletions and new archive paths because moves have not been staged. Those deletions are archived moves, not lost files. Do not discard the working tree or stage/commit/push everything without reviewing it.
- No branch switch, commit, remote push or deployment was performed. Origin remains the existing GitHub repository. Inspect current Git state before further work; do not assume the working tree is clean.

## Commands and verification already completed

From project root `C:\Users\chava\Miscellaneous\MBA\ProgAnalytics\Project`:

```powershell
python -m portal.main
# Open http://127.0.0.1:8766; Ctrl+C stops the server.
python research/prepare_unlisted_pilot.py
python -m portal.snapshot
python -m unittest discover -s tests -v
python research/validate_markdown_research.py
node --check portal/web/app.js
# Optional, with server running and installed Playwright/Chrome:
python scripts/check_portal.py
```

Last implementation checks: seven active tests passed; JavaScript syntax passed; register check found 74 records, 705 migrated-field checks and zero broken active-document links. Browser checks passed company/year/unit selection, negative cash conversion, source dialog, Python sensitivity, JSON download, reference status and four-view mobile overflow. Desktop 1440x1050 and mobile 390x844 screenshots were inspected. Final mobile navigation wraps into two columns; chart labels were enlarged. All 19 archive and 16 architecture-file hashes independently rechecked. `git diff --check` passed, with line-ending conversion warnings only.

First browser attempt encountered a sandbox subprocess permission error; permitted retry passed. Source download restrictions also required permitted network retries. Do not interpret these environmental failures as source financial failures. The final preview server was stopped after QA; do not assume it remains running. No new numerical validation was performed during the subsequent sample-company explanation or this log-writing turn.

## Exact next bounded task and completion criteria

Start M2 with IGX primary reconciliation, not another broad source survey or UI redesign:

1. Locate one clearly accessible issuer financial statement/DRHP covering FY25/FY26. Prefer an official issuer/regulator link; preserve bytes, source/publication dates, retrieval time and hash. Do not infer authenticity solely from a third-party filename.
2. Review the selected five items against provider observations. Establish actual periods, standalone/consolidated scope, continuing-profit definition, original unit and CFO composition, including settlement/client money where relevant.
3. Write a compact comparison table with source pages, raw values, explicit conversions, residuals and unresolved definitions. Preserve conflicts rather than overwrite N05/raw provider facts.
4. Add/update source records, topic findings, evidence index and work queue together. Update mappings only where the evidence supports them. Do not mark every observation approved merely because arithmetic matches.
5. If approved definitions change, update the adapter/data and projection, run relevant existing tests and inspect affected UI. Add tests only for substantive new rules or failure cases.

Completion means a retained primary document plus a reproducible selected-fact comparison and explicit review outcomes. Then implement one reusable adapter and candidate/review persistence. Later: compatible references/cohort, eligible valuation, saved workspace, durable jobs/publication, optional cited AI explanation. Do not build all of these in the next session.

The next expert-method task, after the reconciliation slice, is one accessible individual Chittorgarh article: trace two strengths and two weaknesses to evidence, with author/date and fact-versus-opinion separation. Do not claim that this article tracing has already occurred.

## Suggested fresh-session prompt

> Continue IPO-Ready from docs/SESSION_LOG_2026-11-12.md. Read AGENTS.md and the linked research status/current architecture/strategy first. Preserve the existing uncommitted work and archive. Complete only the next bounded IGX primary-statement reconciliation, recording native evidence, basis/period/unit definitions and conflicts. Update the research queue and implementation only where supported. Do not restart the old US-first survey, rebuild the archived demo, or implement all future milestones together.
