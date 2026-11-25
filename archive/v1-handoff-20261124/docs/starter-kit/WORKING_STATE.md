# Working state — IPO-Ready fresh prototype

Updated 2026-11-24 (session 8). Read with [AGENTS.md](../../V1_AGENT_INSTRUCTIONS.md), the [brief](PROTOTYPE_BRIEF.md), [steering](steering.md) and the [run log](RUN_LOG.md).

## Product strategy

**IPO-Ready is a research desk for Indian unlisted shares.** A retail investor considering a pre-IPO or unlisted position opens a company, sees what is actually disclosed (and what is not), compares it with listed businesses that earn money the same way, screens other unlisted names, and tests what a small illustrative position does to a ₹5 lakh portfolio. The product's credibility comes from three habits visible on every screen: every figure opens its source, every gap is named rather than filled, and every calculation runs in Python from a dated, hashed input.

**Demo case.** Indian Gas Exchange Ltd (IGX) is unlisted and has a DRHP, restated financials and an indicative WWIPL quote. IEX, its promoter and associate investor, and MCX provide operating exchange references. BSE and CDSL provide market-infrastructure context. The issuer's balance sheet and the disclosure review support treating IGX's inventory and NPA fields as inapplicable.

## Launch and artifacts (current)

| What | Command / path |
| --- | --- |
| Install | `python -m pip install -r requirements.txt` (Python 3.12; uses requests, beautifulsoup4, lxml, pypdf, Flask; playwright only for checks) |
| Full pipeline (online capture + build) | `python -m ipo_ready.pipeline` |
| Offline rebuild from retained captures | `python -m ipo_ready.pipeline --offline` |
| Fallback drill (simulates a failed market feed) | `python -m ipo_ready.pipeline --offline --simulate-failure market` |
| Listed peer fallback drill | `python -m ipo_ready.pipeline --offline --simulate-failure screener:IEX-standalone`. Rebuild normally after inspection. |
| Run the site | `python -m ipo_ready.server` → http://127.0.0.1:8765/ (Page 1). Page 2 `/compare.html`, Page 3 `/portfolio.html` |
| Windows preview | `view-local.bat` starts the server on an available localhost port and opens Page 1. Close the server window or press Ctrl+C to stop it. |
| Unlisted screener | Page 2 runs the CEO query on load. `GET /api/screen?query=…` evaluates it in Python using the current company summary. |
| Listed comparisons and cache | `/compare.html?company=igx#peer-coverage`. Choose among eight domains and 24 company records. The table reads `site/data/current/peers.json`, also retained in the versioned build directory. |
| Portfolio instruments | `/portfolio.html?company=igx`. Page 3 reads `site/data/current/portfolio.json`, mirrored in the versioned build. `python -m ipo_ready.pipeline --sources portfolio_terms` refreshes the five public terms documents. |
| Portfolio allocation | `/portfolio.html?amount=500000&tolerance=balanced&company=igx&include_unlisted=true`. Page 3 starts on this scenario and saves the latest successful inputs in the URL. **Open scenario JSON** opens `/api/portfolio/allocate` with those inputs. The response includes the build, method and baseline. |
| Portfolio fallback drill | `python -m ipo_ready.pipeline --offline --simulate-failure market,portfolio_terms:frsb-coupon-2026h2`. Rebuild normally after inspection. |
| Tests | `python -m unittest discover -s tests -v` |
| Browser check + screenshots | `python scripts/check_site.py` → `outputs/preview/` |
| Dashboard data (pages read this) | `site/data/current/*.json`; versioned builds in `site/data/builds/<build_id>/` |
| Raw captures | `data/captures/<source>/<run_id>/` with `manifest.json` (URL, time, status, bytes, SHA-256) |
| Report / playbook | [docs/report/IPO_Ready_Report.md](../report/IPO_Ready_Report.md) |

## Decisions (reversible unless noted)

| ID | Decision | Reason | Meaningful alternative |
| --- | --- | --- | --- |
| D1 | First issuer IGX | Unlisted + DRHP + issuer restated financials on IR page + listed peers + an honest inventory/NPA "inapplicable" case | Hero FinCorp (NBFC — NPA applicable; revisit as second disclosure case) |
| D2 | Unlisted data: WWIPL company overview + financial pages (robots permits `/unlisted-shares/`), bounded capture with hashes | Only free route that worked for many companies with price, shares, EPS and statements; UnlistedZone NSE page 404'd in Nov | UnlistedZone pages; paid provider later |
| D3 | Issuer evidence: IGX restated financial information + DRHP from igxindia.com, used to reconcile provider figures | Primary, audited-basis document; resolves inventory applicability | Exchange DRHP filing on SEBI site |
| D4 | Market context: Yahoo Finance chart JSON (unofficial, delayed) captured with timestamps; retained capture fallback; labelled DEMO only if no capture exists | Moneycontrol `priceapi` returned "No data found" for IEX on 2026-11-23; Yahoo returned dated JSON | NSE/BSE official pages (anti-bot), paid feed |
| D5 | Listed peer fundamentals: Screener.in public company pages, bounded capture | Ratio tables and P&L in one place; brief names it | Exchange XBRL filings (bounded XBRL queue) |
| D6 | Stack: Python pipeline → versioned JSON → static HTML/CSS/vanilla JS pages served by a small Flask app that also exposes Python APIs (screen, allocate, agent trace) | No build step, offline-safe (no CDN), calculations stay in Python | FastAPI + React (target architecture) |
| D7 | Charts drawn as inline SVG by our own small JS module | No CDN or npm dependency for a reviewer | Chart.js/Plotly via local vendor copy |
| D8 | AI/agentic feature: **disclosure-gap agent** — a deterministic tool sequence that checks provider fields, decides applicability from the business model, searches retained issuer PDFs with word-boundary patterns, extracts page-anchored passages, cross-checks values and emits a verdict + trace | Directly answers the brief's inventory/NPA question on Page 1; runs without model access; every step is inspectable | News/announcement summariser (planned as extension); LLM summarisation via Anthropic API when a key is configured |
| D9 | Visual direction: "research desk" — warm paper background, deep ink navy, saffron accent, dense tabular figures, market ticker strip and right rail like a finance portal; system fonts only | Fresh identity distinct from the archived portal; credible and fast | Dark terminal theme |
| D10 | Units: store raw (provider ₹ crore / lakh / thousand / million; issuer ₹ million) and normalise to ₹ crore; Decimal arithmetic | Preserve reported basis and avoid float drift | — |
| D11 | **Owner direction 2026-11-23:** robots.txt is not a blocker at prototype stage. Requests stay bounded and low-volume; no header spoofing, login or challenge bypass | User message in session 1 | Restrict to robots-permitted sources before any public deployment |
| D12 | Sensex from Yahoo chart JSON (unofficial, delayed); NSE official EOD files stay primary for Nifty indices and stocks | No free official machine-readable Sensex file verified; a BSE API probe with spoofed headers was blocked and not retried | BSE official index archive, downloaded manually |
| D13 | Market volatility from weekly closes (52 weeks) with automatic split detection (2, 3, 4, 5, 10, 20× within 8 %) | Bhavcopy is not corporate-action adjusted; MCX's 1:5 split on 2 Jan 2026 inflated volatility to 171 % | Daily closes plus the NSE corporate-actions file |
| D14 | Valuation shares: dated "share details" block, then summary table, then fundamentals; reject a more-than-100× outlier; quote sanity check (quote < ₹1 or P/E < 1 → valuation withheld) | IGX fundamentals figure = authorised capital; NSE summary in crore shares; Haldia ₹0.10 quote | Issuer paid-up capital ÷ face value where documents exist |
| D15 | Screen the latest available period per company and show its period and basis in the results | Discovery remains useful across year and basis gaps. The listed-peer cohort will gate those dimensions. | Require a single common period and basis for every screen |
| D16 | Use versioned JSON for company and comparison results, with a file-revision cache for the parsed screener input | Disk snapshots survive restarts and retain lineage. Page 2 can read `peers.json` without reparsing captures. | SQLite when indexed history or persistent writes are needed |
| D17 | Exclude NSE from the unlisted screener and discovery list using the retained issuer listing note | The provider still categorizes NSE as unlisted. The retained record and page-level evidence are available for review. [N07](../../../../docs/research/sources/N07.md) | Move NSE into a separate reference dataset when the listed adapter is ready |
| D18 | Use IGX's restated issuer-and-employee-trust P&L for the narrow operating peer comparison, with IEX standalone | The issuer calls the trust an extension and identifies IGX as an associate of IEX since 17 January 2022. Page 1 preserves the WWIPL basis and cites the restated scope separately. [N13](../../../../docs/research/sources/N13.md) | Wait for uniformly equivalent financial scopes and related-party adjustments before expanding the metric set |
| D19 | Show broad sector candidates as context and gate comparable ratios on business fit, exact annual end and verified basis | Similar industries can have different economics. India Carbon and Rain also illustrate why matching an FY label alone can admit the wrong period. | Compare segment disclosures if compatible revenue and capital bases become available |
| D20 | Give the demo a domain picker with multiple company choices per domain | Supports the owner's request while preserving each company's deeper hierarchy and eligibility rules. | Use a single flat list or split the picker into more granular subindustries |
| D21 | Use CIAL's audited PDF and Automotive Axles' audited rendered filing for the selected annual comparisons | The secondary pages leave the relevant basis unclear. Retained primary figures support the operating comparisons with a source link on each operand. [N15](../../../../docs/research/sources/N15.md) | Extend the primary route to a broader validated filing adapter when coverage warrants it |
| D22 | Use Floating Rate Savings Bonds 2020 (Taxable), HDFC Bank equity, Nippon India ETF Gold BeES and MCX equity on Page 3 | The first three identify sovereign debt, banking equity and physical gold. MCX had the highest sampled volatility among the chosen listed instruments after its verified split. Both MCX and the default IGX position have exchange-business exposure. [Portfolio evidence](../../../../docs/research/topics/portfolio-instruments.md) | A short Treasury bill for different exit timing or a volatile equity fund with less exposure overlap once comparable history is available |
| D23 | Use shared weekly NSE closes for listed risk and surface the bond and unlisted history gaps | The 49 closes give 44 adjacent returns. Keeping lockup and dealer lot terms visible supports separate liquidity assumptions. | Capture complete daily history and validate a transaction-based unlisted series when accessible |
| D24 | Size whole units using profile targets, an explicit stress budget and shared exchange exposure | Whole lots surface the IGX constraint. A simple adverse scenario can be reproduced with the available price history and unsupported trade history is visible. | Fit a portfolio covariance model when comparable, verified return data exists for the relevant positions |
| D25 | Apply the exit haircut after the unlisted price shock and keep unallocated capital as cash | Shows the liquidity penalty in rupees and preserves the user’s capital and risk budgets when an instrument cannot be sized. | Test different haircut values or executable lot terms when transaction evidence is available |
| D26 | Use one pie and holdings table with a scenario/baseline switch and both risk mixes in the legend | The comparison holds amount and tolerance constant and fits at narrow widths. The URL carries the last successful inputs for reproduction. | Use side-by-side pies for larger screens or exported reports |

## Open questions (working assumption → what would change it)

- Q1 WWIPL's basis for IGX remains unspecified. Use the reviewed restated issuer-and-employee-trust statement when comparing IGX with listed exchanges. Change the WWIPL basis only if the provider labels the statement or the underlying period and source can be identified.
- Q2 WWIPL price is a dealer quote, not an exchange trade. Assumption: use as an indicative price with its date for P/E and market cap, labelled "dealer quote". Change if a second dealer quote diverges > 10 %.
- Q3 What stress values and exits to model. R2 uses a 35% unlisted price shock followed by a 25% discount on residual value, a 5/10/20% unlisted position limit by profile, and a 25% combined exchange cap. IGX's ₹2,44,000 lot exceeds the ₹50,000 balanced limit at ₹5 lakh. Smaller verified lots, matched quotes or executed transfer terms could change the result or the assumptions.
- Q6 Provider FY2025 figures for IGX differ from the restated FY2025 figures by ₹0.16–0.32 cr. Assumption: the provider used the originally audited FY25 accounts. Shown as ≠ in the reconciliation; change if the provider documents its source.
- Q4 Screener.in reuse terms for listed peer data. Assumption: bounded local capture for a prototype, no redistribution. Change before any public deployment.
- Q5 Google News RSS for dated headlines. Assumption: acceptable as headline + link only. Fallback: issuer announcements from retained documents.
- Q7 The demo covers 24 companies across eight domains. Eleven of 46 proposed pairings qualify across six domains. Technology and consumer remain context-only for the captured scopes, as do e-pharmacy and optical chips. Revisit with compatible issuer bases, closer listed peers, or verified segment statements. [Coverage review](../../../../docs/research/topics/listed-peer-coverage.md)

## Steering carried forward

The owner asked for same-domain peers across multiple domains, Page 1 updates where comparisons require them, reusable cached results and a Windows preview launcher. In session 4 the owner asked for more domains and company choices per domain. C2 used the existing captures and added five companies, including two airports and two auto component companies in their respective domain pickers. The latest Page 1 build carries the source and provider listing labels. Licensed content remains the plan for a public version.

## To-do list (priority order)

Legend: `[x]` done · `[~]` in progress · `[ ]` open. "Dep" lists dependencies.

### Foundation and pipeline
- [x] **T00 Discovery and decisions** — issuer, data routes, stack, visual direction recorded above. Done when D1–D9 recorded.
- [x] **PL1 Bounded capture** (Dep T00) — `ipo_ready/capture.py` fetches WWIPL company pages, Yahoo charts, news RSS and issuer PDFs into `data/captures/<source>/<run_id>/` with manifest + SHA-256 and recorded failures. Done when one online run writes manifests for all sources.
- [x] **PL2 Parse and normalise** (Dep PL1) — WWIPL HTML → observations with raw label, raw text, unit, period, source anchor and state (reported / nil / missing / inapplicable / conflict). Done when IGX's 5 FY periods parse and tests pass.
- [x] **PL3 Issuer reconciliation** (Dep PL1) — extract IGX restated balance-sheet lines (p5) and ratio note (p54); reconcile with WWIPL in ₹ crore. Done when the reconciliation table is in JSON with per-line differences.
- [x] **PL4 Checks and metrics** (Dep PL2) — balance identity, conflict detection, freshness; Decimal metrics (growth, margins, current/quick ratio, ROE, ROCE, P/E, market cap) with zero-denominator handling. Done when unit tests cover zero/missing/negative cases.
- [x] **PL5 Versioned JSON delivery + offline + fallback** (Dep PL2–PL4) — build writes `site/data/builds/<id>/` and `site/data/current/`, manifest with input hashes; `--offline` and `--simulate-failure` work. Done when both reruns succeed and the page shows the stale/fallback label.

### Page 1 — Company dashboard (home)
- [x] **H1 Shell + company view** (Dep PL5) — shared nav for 3 pages; home opens IGX; company and period selectors; revenue/profit trend chart; KPI cards incl. quick ratio, inventory, NPA with honest states; every figure opens its source. Done when interactions work at 1440 px and 390 px.
- [x] **H2 Side rail** (Dep PL1) — Nifty/Sensex/selected stocks with timestamp and source; dated news with links; discovery list that opens another unlisted company. Done when each item shows source + freshness and discovery switches company.
- [x] **H3 Reports and evidence drawer** (Dep PL3) — issuer documents list with dates/hashes; drawer shows URL, retrieval time, page, raw label/value. Done when a KPI click opens the right anchor.
- [x] **AI1 Disclosure-gap agent** (Dep PL3) — `ipo_ready/agent.py` runs in pipeline and on demand (`/api/agent/disclosure?company=`); Page 1 shows verdict, trace steps, passages and links. Done when IGX inventory = inapplicable with p54 evidence, NPA = inapplicable by business model, and a no-document company gets "not found — what to check".
- [x] **H4 Page 1 verification** — desktop + mobile screenshots in `outputs/preview/`, interaction script passes. Done when screenshots saved and inspected.

- [ ] **H5 Page 1 follow-ups** (non-blocking) — (a) issuer documents exist only for IGX; WWIPL annual-report downloads are behind a form → add issuer-site discovery for one more company (Hero FinCorp DRHP) to exercise the NPA "found" path; (b) news shows headlines only, with no summary. Done when Hero FinCorp NPA verdict cites a page.

### Page 2 — Listed-peer comparison and unlisted screener
- [x] **C3 Unlisted screener** (Dep PL4) — bounded query parser (`AND`/`OR`, `> < >= <= =`), defined units (₹ crore, %, ×), Python API, selected metrics, coverage and empty-result feedback. The CEO example returns Polymatech and the zero-match case shows how to revise the filter.
- [x] **L1 Windows preview launcher** — `view-local.bat` opens Page 1 on an available port after the server binds. The batch reached the Python entry point and the bound server returned HTTP 200 with browser dispatch mocked.
- [x] **C1 Sector hierarchy, peer eligibility and cached comparisons** (Dep PL1) — offline build produces anchored facts, ratios, fit reasons and exclusions across four domains. Page 1 exposes the reviewed IGX scope and links into the coverage card. `LTM` and `SPLPETRO` replace the earlier 404 identifiers.
- [x] **C2 Comparison view and expanded demo** (Dep C1) — 24 selectable company records across eight domains with at least two per domain. The view shows side-by-side annual ratios with evidence, business drivers, six dated notes, candidate reasons, period and basis gaps, and a missing-company state at desktop and mobile widths.

### Page 3 — Portfolio risk and diversification
- [x] **R1 Instrument universe** — published the four source-backed instruments, bond and dealer liquidity terms, common weekly listed volatility and drawdown, and deliberate unavailable states. Page 3 can inspect the evidence and choose among 24 unlisted issuers.
- [x] **R2 Allocation algorithm** (Dep R1) — Decimal sizing with whole units, a stress budget, an unlisted exit haircut, concentration caps and a baseline. Built and checked the API and the fixed ₹5 lakh Page 3 preview. The larger IGX case and the balanced NCDEX case exercise both caps and the haircut.
- [x] **R3 Page 3 UI** (Dep R2) — amount, tolerance, company and inclusion call the Python API. The scenario and baseline have whole-unit holdings, amount and weight, a three-band pie, stress and liquidity context, and reproducible input URLs.

### Report and demo
- [x] **D1–D9 Report** — `docs/report/IPO_Ready_Report.md` has all nine sections, including the executed portfolio calculations, risk mix and an updated walkthrough across all three pages.
- [x] **V1 Independent demo walkthrough** — ran the playbook, reproduced the metric, screen and allocation from retained inputs and tested fallback. Recorded one P1 and one P2 finding in [REVIEW.md](REVIEW.md).
- [ ] **F1 Repair review findings** (Dep V1) — correct Polymatech's final earnings-row mapping and disclose the P/E basis. Anchor the IGX quick-ratio inventory assumption and scope it by financial period. Done when the repaired JSON, views, queries and report agree and the affected checks pass at desktop and mobile widths.

### Requirement → task map

| Requirement | Tasks |
| --- | --- |
| Page 1 company dashboard | H1, H2, H3, AI1, H4, F1 |
| Page 2 comparison + screener | C1, C2, C3, F1 |
| Page 3 portfolio lab | R1, R2, R3 |
| Python-to-JSON pipeline and cached results | PL1–PL5, C1, C3, R1 |
| AI / agentic workflow | AI1 (+ extension list in report §8) |
| Report §1 Problem, §2 Prior research | D1, D2 (from research KB) |
| §3 Data sources & quality | D3 ← PL1–PL4 |
| §4 Approach, §6 Schematic | D4, D6 ← PL5, R2 |
| §5 Methodology | D5 ← PL4, C1, C3, R1, R2, F1 |
| §7 Results, §8 Playbook, §9 Decision | D7–D9 ← C1–C3, R2, R3, L1, V1 |

## Current task

**Next is F1 (repair).** Follow the [repair prompt](PROMPTS.md#4-repair) and reproduce the findings in [REVIEW.md](REVIEW.md). Correct the final PAT mapping, preserve the distinction between reported EPS and calculated P/E inputs, and link the source for the period-specific quick-ratio assumption. Refresh the versioned build and rerun the CEO query and its 3.82× and 3.90× boundary cases, the FY2026 and FY2022 Quick ratio drawers, and both screen widths.

## Current preview

- Page 3 screenshots are `outputs/preview/page3-desktop.png` and `page3-mobile.png`. `page3-desktop-growth.png` shows the ₹12.5 lakh IGX case and `page3-desktop-fallback.png` shows previous market and product captures. Page 2 examples include `?company=pharmed`, `?company=cial` and `?company=axlesindia`.
- 41/41 Python tests and 120/120 browser checks passed at 1440 and 390 px. The fallback and endpoint error/retry were checked at both widths. Results are in `outputs/preview/check_results.json`.
- Current data build is `20261123T191506Z` in `site/data/current/manifest.json` (offline, zero fallbacks, 25 stored company records, 24 off-exchange demo choices, 146 checks pass / 2 fail / 6 conflict / 1 stale). The review preview uses port 8770. The batch launcher chooses an available port.
- The [independent review](REVIEW.md) records one high-priority earnings-row issue and one quick-ratio evidence issue. The reviewed build was `20261123T190410Z`. Reviewer screenshots are `outputs/preview/review-page2-mobile.png` and `review-page3-desktop.png`.
