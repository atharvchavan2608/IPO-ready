# IPO-Ready capabilities and roadmap

**24 November 2026**

IPO-Ready is a local research prototype for Indian unlisted and pre-IPO companies. An investor can inspect an issuer’s financials and sources, compare it with eligible listed businesses, screen the unlisted universe and test how a whole-lot position would change a portfolio. The three-page workflow passed the independent desktop and mobile walkthrough. Before presenting the screening figures as verified, correct Polymatech’s earnings mapping and make the P/E basis explicit. The same repair run should tighten the evidence behind IGX’s quick ratio. [Independent review](../starter-kit/REVIEW.md)

## Current capabilities

### Company dashboard

The home page opens on Indian Gas Exchange (IGX). The investor can switch company or reporting period, inspect trends and financial statements, open the evidence behind a metric and move to a related company from the discovery panel. Evidence drawers can show the original label, reported unit, date, statement basis, source link and capture hash. IGX’s issuer reconciliation displays differences between the retained provider figures and the restated issuer figures. The market rail gives dated Nifty, Sensex and selected equity context alongside news headlines. [Company methodology](../report/IPO_Ready_Report.md#page-1-metrics-implemented-ipo_readymetricspy)

The disclosure-gap agent checks inventory and non-performing asset (NPA) disclosures on demand. It applies business-model rules, searches retained issuer documents and exposes its trace and page references. The reviewed IGX inventory run linked the issuer’s note on PDF page 54. Hero FinCorp illustrated the complementary case where an NPA figure was expected and the local agent lacked the issuer documents needed to verify one. The workflow uses deterministic rules and document search without a live language-model dependency. [Agent review](../starter-kit/REVIEW.md#walkthrough-failures-and-source-checks)

### Listed peers and unlisted screener

The prototype stores 25 company records. The screener and company discovery use 24 off-exchange choices across eight domains. The NSE record is retained as a listed reference, with the listing evidence available from the screener’s coverage section. The listed-peer view shows the business hierarchy, reporting period, eligible peers, metric origins and the reasons a candidate was excluded. A pairing needs an appropriate business model, the same annual year-end, a compatible reporting basis and usable inputs. The reviewed dataset admitted 11 of 46 candidate pairings. IEX and MCX cleared the operating checks for IGX. [Peer coverage](../../../../docs/research/topics/listed-peer-coverage.md) · [NSE listing evidence](../../../../docs/research/sources/N07.md)

The unlisted screener evaluates bounded `AND` and `OR` queries in Python. It distinguishes matches, definite non-matches and companies left undecided by unavailable inputs. Each result carries the fiscal period, statement basis and quote capture date where relevant. In the reviewed build, the example of market cap above ₹500 crore, P/E below 15× and ROCE above 22% returned Polymatech as its sole match. Seventeen companies failed at least one required condition and six were undecided. Polymatech clears the broad 15× threshold under each earnings measure tested by the reviewer. Its sensitivity to tighter thresholds is an open issue. [Screening method](../report/IPO_Ready_Report.md#page-2-unlisted-screener-implemented) · [Earnings finding](../starter-kit/REVIEW.md#p1--polymatech-uses-a-pre-associate-subtotal-as-fy2025-profit-after-tax)

### Portfolio Lab

An investor can change the budget, risk tolerance, unlisted company and inclusion setting. The lab compares a scenario with a baseline at the same amount and tolerance, showing whole-unit holdings, cash, low/medium/high allocation weights, modeled stress loss, exchange concentration and restricted capital. It can explain why a dealer lot fits or why it was skipped. The scenario URL preserves successful inputs, and the JSON response identifies the build and method used. [Allocation method](../report/IPO_Ready_Report.md#page-3-allocation-model-implemented)

The named instruments are Government of India Floating Rate Savings Bonds 2020 (Taxable), HDFC Bank equity, Nippon India ETF Gold BeES and MCX equity. The Python engine models whole bond denominations, shares, ETF units and unlisted lots. Its rules include a risk-tolerance stress budget, an unlisted exit discount and a shared 25% exposure cap when the unlisted holding and MCX are both classified as exchange businesses. [Portfolio instruments](../../../../docs/research/topics/portfolio-instruments.md)

| Reviewed scenario | Result | What it shows |
| --- | --- | --- |
| ₹5 lakh balanced, IGX | ₹0 unlisted allocation. A ₹2.44 lakh lot exceeds the ₹50,000 position limit. | The minimum lot can make an otherwise interesting issuer infeasible at a small budget. |
| ₹5 lakh balanced, NCDEX | One ₹25,300 lot. Modeled stress loss rises from 18.11% to 18.84%, and the high-risk bucket rises from 14.33% to 17.95%. | A lot that fits the budget can still change the risk mix and modeled loss. |
| ₹12.5 lakh growth, IGX | One IGX lot fits. The shared exposure cap reduces MCX from 87 baseline shares to 19 scenario shares. | Separate investments can compete for the same concentration budget. |

The figures above use retained closing prices and indicative dealer quotes. Scenario results and arithmetic are reproduced in the report. [Executed allocations](../report/IPO_Ready_Report.md#executed-allocation-scenarios)

### Data delivery and reproducibility

Python captures and normalizes source data, checks financial identities and input states, and publishes versioned JSON to the local Flask application. Captures retain source URLs, retrieval times and SHA-256 hashes. The pipeline can rebuild from retained files and record when it substitutes a last successful capture. Versioned JSON and file-revision caches serve the current demo. The build manifest identifies the inputs and flags data issues for review. [Data sources and quality](../report/IPO_Ready_Report.md#3-data-sources-data-quality-and-data-information) · [Build manifest](../../../../site/data/current/manifest.json)

The independent review reproduced a displayed metric, the compound screen and a growth allocation. It also exercised source fallback, missing values, incompatible peers, empty results, malformed input and recovery from an unavailable allocation endpoint. The restored build passed 41 Python tests and 120 browser checks at 1440 and 390 pixels. The two findings below require targeted tests beyond the existing suite. [Verification results](../starter-kit/RUN_LOG.md#2026-11-24--session-8)

## Current limitations

| Limitation | Effect on interpretation |
| --- | --- |
| **Polymatech’s earnings row** | The FY2025 mapper selects ₹375.0116 crore of profit before the associate contribution. Final consolidated PAT is ₹375.5864 crore. With the existing proxy formula, P/E moves from 3.8249× to 3.8190×, enough to change a screen at 3.82×. The retained reported basic EPS of ₹9.07 is a separate measure. |
| **IGX’s quick-ratio evidence scope** | The FY2026 calculation reproduces at 1.51× using the nil-inventory assumption. The drawer links the two balance-sheet operands and lacks a direct link to the issuer evidence behind that assumption. FY2022 reuses the explanation even though the retained issuer balance sheet covers FY2024 through FY2026. |
| **Disclosure and reporting basis** | Audited reports, statement scope and historical periods vary by issuer. The screener can mix fiscal periods or bases for discovery. The stricter peer gates leave some companies with contextual references only. A comparison gap can reflect missing evidence, incompatible business economics or both. |
| **Quotes and capacity to trade** | Dealer prices are indicative and the displayed date can be the page capture time. Executable quotes, transfer conditions, depth, fees and the practical lot available at a stated price require separate confirmation. One-day listed turnover gives context about activity. |
| **Sampled market risk** | The current listed risk sample contains 49 common weekly closes and 44 usable adjacent-week returns, through 20 November 2026. Weekly closes can miss intraweek losses and exclude distributions. There is no verified exchange price series for the bond or unlisted position. |
| **Illustrative model and liquidity** | Stress thresholds, the 35% unlisted price shock and the subsequent 25% exit discount are scenario assumptions. Interest, taxes and transaction costs are excluded. Bond lockup is reflected in restricted capital. The risk mix groups invested amounts and cash by assigned band. |
| **Coverage and operations** | The application is a local prototype with dated sources. Live coverage varies by feed, and access and reuse need review ahead of broader distribution. The independent run used retained data and spot-checked selected public links and filings. |

The review identifies the exact rows and evidence pages for both open findings. The portfolio research note documents the terms and price sample. [Review findings](../starter-kit/REVIEW.md#severity-ranked-findings) · [Portfolio evidence and coverage](../../../../docs/research/topics/portfolio-instruments.md)

## Implementation roadmap

### Demo sign-off repairs

1. **Correct earnings extraction and P/E presentation.** Select final consolidated PAT explicitly, preserve the pre-associate and owner-attributable rows separately, and keep conflicting final observations visible. Choose and display the P/E basis in the company view, screener and exports. Prefer verified, period-matched reported EPS when making a reported-earnings comparison. If a calculated proxy remains available, label it and expose its inputs. Rebuild the versioned data, confirm the original compound query and add boundary tests at 3.82× and 3.90× with expectations tied to the chosen basis.
2. **Scope the inventory assumption by period.** Attach the issuer balance sheet and inventory-turnover note to the IGX quick-ratio drawer. Provide a distinct label for assumed nil and retain a missing state where the period has insufficient evidence. Test at least FY2026 and FY2022 on both widths and keep the reporting-basis distinction visible when a provider figure relies on an issuer note.
3. **Recheck the affected workflow.** Rerun the offline and fallback builds, confirm the displayed numbers against retained inputs, and replay the dashboard-to-screen path with the patched data. Sign off when the disclosure, JSON and visible screen agree and the new tests cover both findings. [Repair task](../starter-kit/WORKING_STATE.md#current-task) · [Detailed reproduction](../starter-kit/REVIEW.md#independent-reproductions)

### Next pilot release

| Work item | Implementation | Acceptance check |
| --- | --- | --- |
| **Expand verified issuer coverage** | Add a primary annual report or filing for Hero FinCorp and a small set of pilot issuers across exchanges, lending and industry. Store original lines and typed values with reporting period, scope, unit, source and reconciliation status. Use an India filing or XBRL adapter after proving that it preserves these distinctions on real paired filings. | Reconcile a reviewed set of dashboard figures per new issuer against the primary source. Demonstrate an NPA result with a page, period, numerator and denominator when the issuer provides them. |
| **Make screening and peer fit easier to understand** | Add common-period and basis filters, a visible reported-versus-proxy P/E option and a result explanation showing which clause passed, failed or lacked data. Carry the peer exclusion reason next to the affected metric and offer a compact comparable-versus-context view on mobile. | A pilot user can explain why an issuer matched and distinguish a same-basis comparison from industry context. Test positive, empty, ambiguous and stale cases. |
| **Improve price and liquidity evidence** | Track an effective quote timestamp separately from retrieval time when the provider exposes it. Retain independent quote observations with explicit lot and transfer terms, add staleness and disagreement rules, and withhold valuation or execution-sensitive fields when the inputs fail them. | A dated quote, its lot and a disagreement state can each be reproduced from evidence. A fallback never inherits a fresher effective date than its source. |
| **Make scenario assumptions adjustable** | Add bounded inputs for the exit discount, costs and liquidity constraints, with documented presets and side-by-side sensitivity. Expose how one minimum lot changes results near a budget cutoff, and record the assumptions and data build in the exported scenario. | The same inputs and build reproduce the output. Tests cover lot thresholds, zero allocations and the fact that the reported weights sum to 100% after rounding. |
| **Save and export research** | Support named local watchlists, saved screen queries and an evidence-linked scenario export. Start with local persistence if the pilot remains single-user. | A saved scenario opens against the recorded inputs and build, and the user can tell when refreshed inputs change the result. |

### Capabilities to validate before expanding

- **Evidence-linked AI summaries.** Start with dated issuer announcements and evidence passages. Require each claim to link to a source, retain source dates and distinguish management statements from model interpretation. Use a small reviewed evaluation set to test citation accuracy, numeric fidelity and abstention. Keep financial formulas and decisions about missing data in Python. [Disclosure agent and extension options](../report/IPO_Ready_Report.md#8-client-playbookinteractive-dashboard)
- **Broader portfolio analytics.** Add more instruments and optional return or correlation estimates only once comparable, corporate-action-aware histories and a defensible treatment of unlisted exposures are available. Retain the transparent stress scenario for users who want to see the impact of specific shocks. [Portfolio evidence](../../../../docs/research/topics/portfolio-instruments.md)
- **Hosted pilot.** Confirm source reuse and distribution rights, determine whether accounts and shared datasets are needed, and implement scheduled ingest, permission boundaries, observability and recovery around the chosen operating model. Adopt a relational datastore and job queue when shared writes or scheduled loads justify them. Preserve source hashes and a previous-build recovery path. [Architecture context](../../../../docs/architecture/CURRENT_ARCHITECTURE.md)

## Suggestions for the founder

- **Prioritize traceability in the first pilot.** Ask participants to open a ratio’s source, explain why a peer was excluded and determine whether an unlisted lot fits a ₹5 lakh scenario. Observe which step requires a prompt and whether participants can explain the result in their own words. Use those observations to prioritize interface work.
- **Choose a pilot coverage standard before adding names.** Start with a small number of well-documented issuers across the existing domains. Expand when each new issuer can support a dependable financial profile or a clearly described coverage gap. Prioritize evidence that changes screening, comparison or feasibility decisions.
- **Make the demo decision concrete.** For IGX, distinguish the diligence decision from the simulated purchase decision. The user can shortlist the company for further research even when the recorded lot exceeds the balanced portfolio cap. Revisit the conclusion when verified lot terms, transfer conditions or new issuer evidence change the inputs. [Demo case decision](../report/IPO_Ready_Report.md#9-final-decisionstrategy)
- **Track a few pilot measures.** Use task completion across the three pages, the share of displayed key metrics with usable evidence, coverage by issuer and period, and how often a screen is blocked by missing inputs. Establish baselines during the pilot before setting targets.

## Local launch and project references

From the repository root, install the dependencies, rebuild from retained captures and start the local server. On Windows, the batch launcher can open the same prototype on a free port after the rebuild. [Windows launcher](../../../../view-local.bat) · [Full playbook](../report/IPO_Ready_Report.md#8-client-playbookinteractive-dashboard)

```powershell
python -m pip install -r requirements.txt
python -m ipo_ready.pipeline --offline
python -m ipo_ready.server
```

Open `http://127.0.0.1:8765/` for the company dashboard, `/compare.html` for listed peers and the screener, and `/portfolio.html` for the Portfolio Lab. See the working state for the latest build, demo URLs and repair sequence. [Working state](../starter-kit/WORKING_STATE.md)
