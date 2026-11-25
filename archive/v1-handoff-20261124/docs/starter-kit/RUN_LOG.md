# Run log

One entry per session, newest last. Launch commands and artifact paths live in the [working state](WORKING_STATE.md).

## 2026-11-23 · Session 1 (kickoff)

**Tasks:** T00, PL1–PL5, H1–H4, AI1 done; D1–D9 report started.

**Outcome.** Page 1 opens on IGX (unlisted, pre-IPO) with the following:
- company and period selectors, KPIs and a trend chart;
- a source drawer on every figure;
- a reconciliation against the issuer's restated statements;
- the disclosure-gap agent, saved with the build and re-runnable live through the Python API;
- a market, news and discovery rail.

The pipeline captures six sources with hashes and builds versioned JSON online, offline or through a fallback drill. Pages 2 and 3 are placeholders with working navigation and direct URLs.

**Owner direction received mid-session:** "Ignore anti robot concerns as this is prototype stage, not mass scraping." Recorded as D11. Sensex now comes from Yahoo (D12).

**Discovery findings that shaped decisions:**
- WWIPL `/unlisted-shares/<slug>` pages give a quote, shares and statements for 20 companies. They use two layouts and four raw units.
- IGX's investor page links restated financials and a DRHP, but WWIPL says "DRHP Filed? No".
- Moneycontrol `priceapi` returned "No data found" for IEX.
- NSE EOD archives (index file and bhavcopy) return 200.
- A BSE API probe with spoofed Referer/Origin headers was blocked by the permission classifier and was not retried.

**Changed / added files:**
- `ipo_ready/` (package): `capture.py`, `sources.py`, `parse_wwipl.py`, `issuer.py`, `company.py`, `metrics.py`, `agent.py`, `market.py`, `news.py`, `pipeline.py`, `server.py`, `config.py`, `universe.json`.
- Site: `site/index.html`, `compare.html`, `portfolio.html`, `assets/app.css`, `assets/core.js`, `assets/page1.js`.
- Checks: `tests/test_pipeline.py`, `scripts/check_site.py`.
- Docs and config: `requirements.txt`, `.gitignore` (caches), `docs/starter-kit/WORKING_STATE.md`, this log, `docs/report/IPO_Ready_Report.md`.
- Captures: `data/captures/{wwipl,issuer,news,screener,nse_eod,yahoo}/…`.

**Commands and results:**
- `python -m ipo_ready.capture --sources issuer,wwipl`: 40/40 WWIPL pages 200; the IGX PDFs were reused from run 20261123T163845Z (restated financials 2.2 MB, DRHP 13.6 MB, abridged prospectus 0.5 MB; SHA-256s in the manifest).
- `python -m ipo_ready.capture --sources news,screener,nse_eod`: news 21/21. Screener 46/50 (LTIM and SUPREMEPET 404 on both bases). NSE: 67 trading dates stored, holidays recorded as "no file".
- `python -m ipo_ready.capture --sources yahoo`: 4/4 200.
- `python -m ipo_ready.pipeline --offline`: build OK, 20 companies, checks 128 pass / 2 fail / 5 conflict / 1 stale, about 5 s (the first build took 65 s while it extracted PDF text).
- `python -m ipo_ready.pipeline --offline --simulate-failure market,wwipl:igx-overview`: 5 fallbacks recorded. Market as-of moved to 20 Nov. The IGX overview came from the previous run. The simulated runs were deleted afterwards. Screenshot: `outputs/preview/page1-desktop-fallback-drill.png`. A normal build was restored after the drill.
- `python -m unittest discover -s tests -v`: 17/17 OK. The tests caught a real period-regex bug (`31-Mar-23`), now fixed.
- `python scripts/check_site.py` with the server running: 28/28 pass at 1440 px and 390 px, including the live agent run (about 1.4 s) and no console errors after adding a favicon.
- Manual check: Python reproduces IGX's published FY25 current ratio (1.80), ROE (23.30%) and net profit ratio (63.10%) from the restated inputs. ROCE gives 26.88% against the issuer's 27.66%, because the issuer does not state how it defines capital employed.

**Known gaps:**
- Issuer documents exist for IGX only. Hero FinCorp's NPA shows "not disclosed" and is not yet searched.
- No provider states basis except in a few headings.
- News is headlines only.
- Sensex uses an unofficial feed.
- Haldia's quote fails the sanity check.
- OYO FY22 and HDFC Securities FY26 fail the balance identity (provider inconsistencies, kept).
- The report has *Pending* markers for Pages 2 and 3 and the international site comparison.

**Next action:** C3, the unlisted screener (query parser plus `/api/screen`, CEO example, empty-result feedback), then C1/C2 peers from the retained Screener.in captures (IEX standalone basis).

## 2026-11-23 · Session 2

**Completed C3 and L1.** The Page 2 screener runs the CEO example on load, lets the investor edit conditions, shows the requested metrics and data coverage, and links matches to the company dashboard. The Windows batch launcher opens Page 1 after binding an available localhost port.

**Steering applied.** The owner added same-domain peer groups across several sectors, Page 1 upgrades where Page 2 requires them, cached results and a launcher. C3 used existing retained captures. The company build files provide persistent versioned results, and repeat screens reuse the parsed current company snapshot until the pipeline replaces it. C1 now covers sector examples, versioned peer results, and any supporting data or dashboard changes.

**Executed results.** The CEO query matched Polymatech (FY2025 consolidated) from 19 eligible records. Its ₹36 captured dealer quote yielded ₹1,434.38 crore market cap and 3.8249× P/E, and statement operands yielded 35.41% ROCE. There were 13 definite non-matches and 5 undecided companies. `Market capitalization > 10000000` returned zero matches, 18 definite non-matches and one undecided company. Retained listing evidence removed NSE from the screen. [Methods, operands and source anchors](../report/IPO_Ready_Report.md#7-analysis-resultsoutput) · [N07 listing note](../../../../docs/research/sources/N07.md)

**Changed files.** Added `ipo_ready/screener.py`, `site/assets/page2.js`, `tests/test_screener.py` and `view-local.bat`. Updated `ipo_ready/server.py`, `ipo_ready/universe.json`, `site/compare.html`, `site/assets/app.css`, `scripts/check_site.py`, the report and working state. Rebuilt `site/data/current/` from retained captures and refreshed `outputs/preview/`.

**Commands and checks**

- `python -m ipo_ready.pipeline --offline` produced build `20261123T172305Z` with 20 records, 128 passing checks, two failures, five conflicts and one stale flag. No fallback was needed.
- `python -m ipo_ready.server --port 8766` served the current code. Port 8765 was already serving an older instance.
- `python -X utf8 -m unittest discover -s tests -v` passed 22/22. Covered compound comparisons, Decimal boundary cases, missing and suspect values, exclusions, invalid queries and parsed-cache refresh. The sandbox blocked writes to test fixture subdirectories. The permitted retry passed.
- `python -X utf8 scripts/check_site.py --base http://127.0.0.1:8766/` passed 44/44 at 1440 and 390 px. The permitted retry enabled the headless browser. Inspected both Page 2 screenshots and verified all three default metrics fit on mobile, empty and invalid feedback, example recovery, result navigation, and the existing Page 1 evidence and live agent interactions. [Check results](../../outputs/preview/check_results.json)
- `node --check site/assets/page2.js` and `python -m py_compile ipo_ready/server.py ipo_ready/screener.py tests/test_screener.py scripts/check_site.py` passed.
- `cmd.exe /d /c view-local.bat --help` reached the Python launcher. A separate loopback smoke check confirmed that `--open-browser --port 0` passes the actual bound URL to browser dispatch and Page 1 returns HTTP 200. Browser dispatch was mocked during that launcher check.

**Known gaps.** Screen results use each company's latest available period and provider basis. Polymatech is a discovery result from secondary data and indicative valuation inputs. Listed-peer comparisons and their derived cache are pending.

**Next is C1.** Audit the retained listed captures for IGX, PharmEasy, Polymatech and India Carbon. Document business fit and compatible periods and bases, route any required changes through Page 1, and write versioned peer results and exclusions for C2.

## 2026-11-23 · Session 3

**Completed C1.** Page 2 reads the saved peer cache and opens four company cohorts. IEX and MCX cleared the FY2026 checks for IGX, and Goa Carbon cleared them for India Carbon. PharmEasy and Polymatech show industry context with zero operating matches. The Page 1 link carries the selected company to its peer evidence, and IGX's reconciliation cites the employee share trust perimeter and IEX relationship. Page 1 discovery now follows the screener's NSE listing-status exclusion. No new steering was supplied.

**Executed results.** For FY2026, PAT ÷ operating revenue was 68.8829% for IGX, 77.9605% for IEX, 47.7716% for MCX, −12.0499% for India Carbon and −6.8966% for Goa Carbon. Annual P/E used reported EPS and dated 23 November prices, giving 85.9155×, 20.5556× and 88.7413× for IGX, IEX and MCX respectively. India Carbon and Goa Carbon had losses and P/E was withheld. [Methods and evidence](../report/IPO_Ready_Report.md#7-analysis-resultsoutput)

**Changed files.** Added `ipo_ready/parse_screener.py`, `ipo_ready/peers.py`, `site/assets/peer-coverage.js`, and `tests/test_peers.py`. Updated `capture.py`, `universe.json`, `issuer.py`, `company.py`, `pipeline.py`, `site/compare.html`, `site/assets/page1.js`, `site/assets/app.css` and `scripts/check_site.py`. Added N11–N13 and updated the coverage topic, register and research queue. Refreshed the report, working state and previews, and published both the versioned and current `peers.json`.

**Commands and checks**

- `python -c "from ipo_ready.capture import capture_screener, run_id; capture_screener(run_id(), ['LTM', 'SPLPETRO'])"` is the standalone form of the bounded capture call used in the run. The initial combined Python probe hit a sandbox proxy failure. The permitted retry retained four provider HTML responses and two native NSE identity PDFs under run `20261123T174054Z`. All six returned HTTP 200. [Identifiers and sources](../../../../docs/research/sources/N12.md)
- `python -m ipo_ready.pipeline --offline --simulate-failure screener:IEX-standalone` produced build `20261123T174407Z`. It used IEX's retained standalone capture from `20261123T164603Z` and kept both IGX comparisons eligible. A Headless Edge check opened `/compare.html?company=igx#peer-coverage` and verified the fallback notice and two eligible peers. [Fallback screenshot](../../outputs/preview/page2-desktop-peer-fallback.png)
- `python -m ipo_ready.pipeline --offline` restored normal build `20261123T174815Z`. The final rebuild `20261123T175216Z` applied the discovery exclusion, preserving the peer cohort values. It has 24 parsed listed captures, 20 company records, 128 passing checks, two failures, five conflicts and one stale flag. Compared current and versioned peer JSON byte for byte and independently recomputed operating ratios and annual P/E from the cached operands with Decimal.
- `python -X utf8 -m unittest discover -s tests -v` passed 29/29. An interim balance-sheet column was initially included in the annual inventory. The parser now takes period keys from the annual P&L and the regression test passed.
- `python -m ipo_ready.server --port 8767` and `python -X utf8 scripts/check_site.py --base http://127.0.0.1:8767/` passed 58/58 browser checks. Verified and inspected the peer coverage UI at 1440 and 390 px, including source links, a missing basis, a December year-end, preserved company selection and the Page 1 discovery exclusion. [Browser checks](../../outputs/preview/check_results.json)
- `node --check site/assets/peer-coverage.js`, `node --check site/assets/page1.js`, `python -X utf8 research/validate_markdown_research.py` and `git diff --check` passed. Research validation counted 77 records with zero broken local links.

**Known gaps.** Listed financial values use secondary captures and the annual P/E uses one day's retained prices. Pharmacy and optical chip peers have context coverage. A shared ROCE definition, comparable-segment evidence and primary reconciliation of material provider differences remain open.

**Next is C2.** Render side-by-side metrics from the versioned peer cache, show the evidence and limitations in the view, and summarize dated company plans and news.

## 2026-11-23 · Session 4

**Completed C2 and the owner's expansion.** Page 2 puts the side-by-side table first, with a jump to the unlisted screener. Domain and company pickers cover 24 off-exchange entries across eight domains, each with at least two options. Added Pharmed, Group Pharmaceuticals, Kannur International Airport, Axles India and GKN Driveline. Figures link to input values, annual basis, capture hash and original source. The view shows calculated percentage-point differences, candidate reasons and six dated research notes.

**Executed results.** Eleven of 46 pairings qualify across six domains. New FY2026 examples include Pharmed and Alkem (12.9293% and 15.9802% PAT ÷ operating revenue), CIAL and GMR Airports (37.5848% and 3.1877%), and Axles India and Automotive Axles (8.4069% and 7.5480%). CIAL and Automotive Axles use primary annual statements. The CEO screen still returns only Polymatech, from 24 eligible records. [Report and source links](../report/IPO_Ready_Report.md#7-analysis-resultsoutput)

**Changed files.** Updated the universe, bounded capture functions, annual parsers, peer builder, company build, Page 1 and Page 2, shared styling and evidence drawer, Python and browser tests, and the report and working-state files. Added `ipo_ready/peer_context.py`, native source captures, N14–N17 and the expanded research topic. Published the current and versioned snapshots and refreshed the desktop, mobile and fallback previews.

**Commands and checks**

- `capture_wwipl(run, companies)`, `capture_screener(run, ['ALKEM', 'IPCALAB', 'COLPAL', 'AUTOAXLES', 'GNA'])` and `capture_news(run, companies)` ran through `python -X utf8 -u -` with `companies = ['pharmed', 'grouppharma', 'kial', 'axlesindia', 'gkndriveline']`. All 25 requests returned HTTP 200 in run `20261123T175837Z`. [Native capture manifests](../../../../docs/research/sources/N14.md)
- `python -X utf8 -u -m ipo_ready.capture --sources peer_context` and the targeted `capture_peer_context(run_id(), source_ids)` calls retained eight HTTP 200 responses in context runs `20261123T180022Z`, `20261123T180745Z` and `20261123T181120Z`. The two targeted lists were `['autoaxles-annual-2026', 'cial-terminal-tender']` and `['alkem-fy26-release']`. [Source locations](../../../../docs/research/sources/N15.md) · [Plans and article](../../../../docs/research/sources/N16.md)
- `python -m ipo_ready.pipeline --offline --simulate-failure screener:IEX-standalone` produced fallback build `20261123T180924Z`. A headless Edge spot check confirmed the retained IEX notice and both IGX benchmark columns. [Fallback preview](../../outputs/preview/page2-desktop-peer-fallback.png)
- `python -m ipo_ready.pipeline --offline` restored clean build `20261123T181612Z`. Current and versioned peer snapshots match byte for byte. The build has 146 passing checks, two failures, six conflicts and one stale flag. Reproduced the new comparisons from their raw operands with Decimal and ran the CEO and zero-match screens through the Flask API.
- `python -X utf8 -m unittest discover -s tests -v` passed 32/32. The first Automotive Axles adapter check exposed a rendered table header using `th` cells. The fixed adapter verified the annual period, audited scope and units before reading its operands. Reviewed gains and job-work lines explained four income identity flags. The two differently valued Group Pharmaceuticals FY2026 profit rows remain visible as a conflict.
- `python -X utf8 scripts/check_site.py --base http://127.0.0.1:8767/` passed 78/78 at 1440 and 390 px. Verified all domain selectors, evidence drawers, reporting and plans, period and basis exclusions, the ambiguous profit state, the screener and the existing Page 1 agent. Inspected the comparison previews and added a mobile scroll hint and full-width selectors. [Browser results](../../outputs/preview/check_results.json)
- `python -X utf8 research/validate_markdown_research.py`, `git diff --check`, JavaScript syntax checks and Python compilation passed.

**Known gaps.** Matching technology and consumer statement scopes and closer operating peers are still needed. Annual P/E coverage depends on reported EPS and same-day prices. Group Pharmaceuticals' conflicting FY2026 profit awaits a primary filing. Curated news and plans are bounded, with remaining feeds labelled as headline-only.

**Next is R1.** Build the portfolio instrument universe with verified product terms, dated return history and liquidity attributes.

## 2026-11-24 · Session 5

**Completed R1.** Page 3 identifies Government of India Floating Rate Savings Bonds 2020 (Taxable), HDFC Bank equity, Nippon India ETF Gold BeES and MCX equity. MCX replaced Hindalco after the shared sample showed 37.02% volatility for MCX, 24.04% for Hindalco and 25.04% for HDFC Bank. The page gives terms, latest closing prices, turnover, volatility and sampled drawdown where available. The unlisted selector has 24 companies and retains dealer quote, lot, capture date and source states. IGX opens by default. [Evidence and selection notes](../../../../docs/research/topics/portfolio-instruments.md)

**Executed results.** Across 49 shared weekly closes through 20 November, 44 returns qualify for volatility. Four weeks are missing. HDFC Bank, Gold BeES and MCX measured 25.04%, 23.61% and 37.02% volatility respectively, with sampled drawdowns of −31.24%, −22.33% and −22.21%. The bond coupon was 8.05% p.a. before tax for July–December 2026. One 500-share IGX dealer lot at the indicative ₹488 quote would cost ₹2,44,000. [Report](../report/IPO_Ready_Report.md#portfolio-risk-inputs)

**Changed files.** Added `ipo_ready/portfolio.py`, `ipo_ready/portfolio_terms.py`, `site/assets/portfolio.js`, `tests/test_portfolio.py` and research N18–N20 plus the portfolio topic. Updated capture, market statistics and delivery, Page 3 and shared CSS, browser checks, report and handoff files. Published the current and versioned `portfolio.json` and refreshed previews.

**Commands and checks**

- `python -m ipo_ready.capture --sources portfolio_terms` retained five primary documents in discovery run `20261123T182731Z`, including Hindalco's FY2026 report page. `python -m ipo_ready.pipeline --sources portfolio_terms` retained the revised five sources, including the MCX split circular, in capture run `20261123T183201Z` and built `20261123T183206Z`. All five requests succeeded on the revised run. [Capture manifest](../../../../data/captures/portfolio_terms/20261123T183201Z/manifest.json)
- `python -m ipo_ready.pipeline --offline --simulate-failure market,portfolio_terms:frsb-coupon-2026h2` generated `20261123T183325Z`. A headless Edge Playwright check via `python -X utf8 -` verified 20 November market data and the retained 8.05% coupon, both labelled as previous captures at 1440 and 390 px. [Fallback preview](../../outputs/preview/page3-desktop-fallback.png)
- `python -m ipo_ready.pipeline --offline` restored `20261123T183559Z`, with zero source fallbacks and 146 company checks passing, two failing, six conflicts and one stale flag. A separate `python -X utf8 -` check read `CLOSE_PRICE` from all 49 retained selected-symbol files using `csv.DictReader`, reproduced volatility with `statistics.stdev` and drawdown with cumulative peaks, checked five native terms hashes and confirmed that the current and versioned portfolio files match byte for byte.
- `python -X utf8 -m unittest discover -s tests -v` passed 35/35, including nonadjacent returns, split evidence and unavailable coupon coverage. `python -X utf8 scripts/check_site.py --base http://127.0.0.1:8767/` passed 94/94 at 1440 and 390 px. The Page 3 previews, source drawer, method, navigation, withheld quote and delisted label were checked. [Desktop](../../outputs/preview/page3-desktop.png) · [Mobile](../../outputs/preview/page3-mobile.png) · [Browser results](../../outputs/preview/check_results.json)
- `python -X utf8 research/validate_markdown_research.py` returned 84 records and zero broken local links. `node --check site/assets/portfolio.js`, `python -m compileall -q ipo_ready scripts/check_site.py tests/test_portfolio.py` and `git diff --check` passed.

**Known gaps.** Price risk excludes distributions and relies on sampled closes. NSE turnover is one session's activity. The RBI coupon expires on 31 December 2026. Bond lockup and unlisted transfer risk need explicit scenario treatment. The dealer quote date is the time of capture, and no verified unlisted trades or executable lots are available.

**Next is R2.** Implement the allocation calculation and API. In the ₹5 lakh example, show how the IGX dealer lot and the exchange exposure shared with MCX affect feasibility, position size and concentration under different risk tolerances.

## 2026-11-24 · Session 6

**Completed R2.** A deterministic Python allocation API compares portfolios with and without a selected unlisted issuer. It uses whole units and dealer lots, profile limits, a common stress budget and a cap on combined exchange exposure. Page 3 previews the ₹5 lakh balanced scenario and recalculates on issuer selection. The response includes holdings, cash, risk mix, stress components and the data build. Risk settings are illustrative, including the 35% unlisted price shock and 25% haircut on residual value.

**Executed results.** A ₹2,44,000 IGX lot exceeds the ₹50,000 balanced limit on ₹5 lakh. The baseline leaves ₹3,752.10 cash and models ₹90,563.30 in stress loss. One ₹25,300 NCDEX lot fits the same budget. It contributes ₹8,855 in modeled price shock and ₹4,111.25 in modeled exit haircut. The larger ₹12.5 lakh growth case fits one IGX lot and limits MCX to 19 shares versus 87 without IGX. [Reproduction and assumptions](../report/IPO_Ready_Report.md#executed-allocation-scenarios)

**Changed files.** Added `ipo_ready/allocation.py` and `tests/test_allocation.py`. Updated `server.py`, the portfolio snapshot and pipeline, Page 3 HTML, JavaScript and styling, browser checks, report, research notes and working state. Refreshed current and versioned JSON and previews.

**Commands and checks**

- `python -m ipo_ready.server --port 8769` served the updated routes. `python -m ipo_ready.pipeline --offline --simulate-failure market,portfolio_terms:frsb-coupon-2026h2` generated `20261123T184609Z`. A Playwright spot check via `python -X utf8 -` verified 20 November prices and the matching allocation build, both source fallback labels, and a visible scenario error with evidence still accessible under a simulated HTTP 503 at both widths. [Fallback preview](../../outputs/preview/page3-desktop-fallback.png)
- `python -m ipo_ready.pipeline --offline` restored `20261123T184820Z` with zero source fallbacks, 146 checks passing, two failing, six conflicts and one stale flag. A separate `python -X utf8 -` check reproduced the baseline using whole units and Decimal from the retained JSON, reproduced the NCDEX haircut and the IGX/MCX cap, and matched the versioned and current portfolio snapshots byte for byte.
- `python -X utf8 -m unittest discover -s tests -v` passed 41/41, including input extremes, missing data, the exact IGX lot threshold, risk and budget invariants, and API errors and cache refresh.
- `python -X utf8 scripts/check_site.py --base http://127.0.0.1:8769/` passed 98/98 across all three URLs at 1440 and 390 px. Verified the IGX refusal reason, the NCDEX scenario update, Haldia's gap and the existing evidence screens, then inspected both previews. [Desktop](../../outputs/preview/page3-desktop.png) · [Mobile](../../outputs/preview/page3-mobile.png) · [Browser results](../../outputs/preview/check_results.json)
- `python -X utf8 research/validate_markdown_research.py` found 84 records and zero broken local links. `node --check site/assets/portfolio.js`, `python -m compileall -q ipo_ready tests/test_allocation.py scripts/check_site.py` and `git diff --check` passed.

**Known gaps.** The visible preview runs the fixed balanced budget. Amount, tolerance and inclusion can be changed through the API. Dealer values and stress losses are scenario inputs, and verified exit costs are unavailable. The method excludes execution fees and tax and tracks restricted capital alongside the modeled price loss.

**Next is R3.** Add amount, tolerance, mix and issuer controls to Page 3, then render the holdings, risk mix pie and comparison with the baseline. Show the assumptions and constraint reasons while preserving evidence access at both widths.

## 2026-11-24 · Session 7

**Completed R3 and D1–D9.** Page 3 submits amount, risk tolerance, company and inclusion to the Python API. The result shows whole-unit holdings, amounts and weights, a risk-mix pie, stress and restricted-capital metrics, and the reasons an unlisted lot fits or is skipped. Scenario and Baseline switch the pie and table. The legend shows both risk mixes. The last successful inputs are saved in the URL, and the result links to its exact JSON and company evidence. The report covers all nine sections and includes the interactive walkthrough.

**Executed results.** At ₹5 lakh balanced, NCDEX's ₹25,300 lot raised the high-risk weight from 14.33% to 17.95% and the modeled stress loss from 18.11% to 18.84%. At ₹12.5 lakh growth with IGX, the pie shows 30.78% low, 44.26% medium and 24.96% high. The combined exchange cap leaves 19 MCX shares versus 87 in the baseline. At ₹1.01, the allocation stays 100% in cash. [Results and reproduction](../report/IPO_Ready_Report.md#executed-allocation-scenarios)

**Changed files.** Updated `site/portfolio.html`, `site/assets/portfolio.js`, `site/assets/app.css`, `scripts/check_site.py`, the report, research status and handoff documentation. Rebuilt current and versioned JSON from the retained source files and refreshed the screenshots.

**Commands and checks**

- `python -m ipo_ready.pipeline --offline --simulate-failure market,portfolio_terms:frsb-coupon-2026h2` generated `20261123T185821Z`. Headless Edge via `python -X utf8 -` verified source fallback labels, 20 November prices and the updated risk legend and baseline toggle at 1440 and 390 px. [Fallback preview](../../outputs/preview/page3-desktop-fallback.png)
- `python -m ipo_ready.pipeline --offline` restored `20261123T190022Z` with zero capture fallbacks. An independent `python -X utf8 -` run checked the current and versioned portfolio files byte for byte and summed the live API's holding amounts and risk weights for IGX, NCDEX, the larger IGX case, ₹1.01 and ₹10 crore. Each risk mix totals 100%.
- `python -X utf8 -m unittest discover -s tests -v` passed 41/41. `python -X utf8 -u scripts/check_site.py --base http://127.0.0.1:8769/` passed 120/120 across Pages 1–3. The Page 3 checks covered each control, baseline switching, lot constraints, keyboard submission, URL restore, HTTP 400, HTTP 503 and recovery. Both default previews and the larger IGX scenario were inspected. [Desktop](../../outputs/preview/page3-desktop.png) · [Mobile](../../outputs/preview/page3-mobile.png) · [Growth](../../outputs/preview/page3-desktop-growth.png) · [Browser results](../../outputs/preview/check_results.json)
- A separate Playwright check via `python -X utf8 -` followed the shared navigation from Page 1 through Pages 2 and 3, opened the scenario JSON, returned to the selected scenario and checked the ₹10 crore layout without page overflow at both widths.
- `python -X utf8 research/validate_markdown_research.py` found 84 records and zero broken local links. `node --check site/assets/portfolio.js`, `python -m compileall -q scripts/check_site.py` and `git diff --check` passed.

**Known gaps.** The allocation continues to use indicative dealer quotes and illustrative stress and exit assumptions. Live transaction and transfer evidence could change the modeled result. The independent reviewer has yet to give a demo-readiness verdict.

**Next is V1.** Follow the independent review prompt, run the playbook from a fresh session and record findings in `docs/starter-kit/REVIEW.md`.

## 2026-11-24 · Session 8

**Completed V1.** Ran the playbook on a fresh local server at 1440 and 390 px before reading build verification. All three pages are usable for an internal walkthrough. The review found a high-priority Polymatech PAT mapping error that affects P/E screening near the threshold and a missing issuer link and period scope in the IGX quick-ratio drawer. [Independent review](REVIEW.md)

**Independent reproductions.** IGX's FY2026 quick ratio is 1.5137× under the disclosed nil-inventory assumption. Polymatech is the sole CEO query match, with 17 definite non-matches and six undecided. The provider's final PAT is ₹375.5864 crore, while the app used the ₹375.0116 crore pre-associate subtotal. For ₹12.5 lakh Growth with IGX, independently reproduced 19 MCX shares, ₹1,83,739.40 cash and ₹2,95,884.49 modeled stress loss from retained prices and the dealer lot.

**Changed files.** Added `REVIEW.md` and two review screenshots, then updated the working state and this log. Rebuilt the clean and simulated-failure snapshots from retained captures.

**Commands and checks**

- `python -m ipo_ready.pipeline --offline` built review candidate `20261123T190410Z`. `python -m ipo_ready.server --port 8770` launched the fresh review server. Independent Playwright and Decimal checks via `python -X utf8 -u -` exercised navigation, direct URLs, source drawers, agent, peer exclusions, filter boundaries, allocation inputs and recovery. All 31 JSON files matched the versioned snapshot and sampled native hashes matched their records. [Mobile review](../../outputs/preview/review-page2-mobile.png) · [Desktop review](../../outputs/preview/review-page3-desktop.png)
- `python -m ipo_ready.pipeline --offline --simulate-failure market,portfolio_terms:frsb-coupon-2026h2,wwipl:igx-financial,screener:IEX-standalone` produced `20261123T191215Z` with seven fallback records. Headless Edge showed earlier statements, retained IEX evidence and older market and product data at both widths. A clean `python -m ipo_ready.pipeline --offline` restored `20261123T191506Z` with zero fallbacks. Verified the live health and allocation API build and the local review links.
- `python -X utf8 -m unittest discover -s tests -v` passed 41/41. `python -X utf8 -u scripts/check_site.py --base http://127.0.0.1:8770/` passed 120/120 on the restored build. `python -X utf8 research/validate_markdown_research.py` returned 84 records and zero broken links. `git diff --check` passed.

**Next is F1.** Repair the earnings mapping and P/E basis disclosure and the IGX evidence scope, then rerun the affected build, queries and browser checks. [Reproduction and corrections](REVIEW.md#severity-ranked-findings)
