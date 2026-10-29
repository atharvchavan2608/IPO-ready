# Active direction: target product architecture

Updated 2026-10-29. Start with the [product framework](../architecture/IPO_Ready_Design_Framework.md) and [implementation backlog](../architecture/IMPLEMENTATION_BACKLOG.md). The planning-only direction below is historical. Existing observations and evidence limits remain preserved. This update does not claim new source acquisition or financial validation.

---

# Current status and next work

Updated: 2026-10-22.

## Latest direction: global pre-IPO scope and initial planning

On 2026-10-22 the user opened scope to foreign companies, prioritised pre-IPO companies with limited accessible data/analysis and free APIs, and requested initial planning. The active deliverable is now the [US-first global pre-IPO plan](topics/pre-ipo-global-plan.md): visual workflow, analytical design, source collection strategy and API feasibility. Product design is later work. Investor audience and Python analytics remain unchanged.

Added U01–U06; current register: 64 research records, not 64 unique sources. Official SEC documentation supports a free route. A bounded live check downloaded Reddit's filing index, Submissions JSON and Company Facts JSON without a key. Metadata inspection found no original S-1 accession in Company Facts. Access success does not establish pre-IPO financial coverage. Financials of companies without public disclosures remain unavailable to this route.

Next bounded task: screen six candidate issuers for usable public pre-offer statements and limited accessible analysis, then propose two pilot cases, including a foreign SEC filer if feasible. Record coverage searches and exclusions. Do not substitute later annual reports for pre-offer evidence. The six-step queue and completion criteria are in the plan.

Executed: `research/us_scope_feasibility.py` twice (initial DNS failures; network-enabled retry: seven HTTP 200s, one F-1 PDF 403) and `research/us_scope_inspect.py` once against retained JSON. Native files, hashes and outcomes are linked in [U06](sources/U06.md). No prospectus values were extracted, no financial analysis validated and no app changed.

## Previous direction: proposal and bounded implementation

The user confirmed investors as the intended audience, including individual investors with small amounts and broker analysts, and authorized building. Today's primary objective is a proposal for the professor. Python programming analytics is the core academic work; the interface and future agent layer support it. See [build status](../BUILD_STATUS.md), [proposal](../proposal/IPO_Ready_Project_Proposal.md) and [demo guide](../proposal/Presentation_Guide.md).

The existing research queue below is retained for context. It no longer blocks a bounded prototype. Further research should resolve specific implementation decisions rather than extend the survey indefinitely.

## Completed

- Three survey passes: literature/product discovery, selected GitHub audits, and an Aether pre-offer financial reconciliation.
- Migration of all 45 Excel survey records and the full pilot into Markdown. IDs and review limits preserved.
- XBRL stage 1 reconnaissance: official source routes, one real Aether rendered filing, two pinned repositories, two XML test fixtures, a vendored taxonomy entry point and relevant standards/tool documentation.
- Added X01–X10 to the source register. Total: 55 research records, not 55 unique sources.
- Stage 2A: acquired Aether's official September-2025 results PDF, visually checked selected standalone pages, and recorded 26 comparisons against the NSE rendering. Sixteen same-label rows match after unit conversion; other rows expose numerical or classification conflicts. See [stage 2A](topics/xbrl-stage-2.md).
- Added X11; the current register contains 56 records, not 56 unique sources.
- Stage 2B: inspected a pinned repository copy attributed to Infosys FY24: 417 facts, 81 contexts, four units. Sixteen selected values match the official PDF numerically; eight annual rows have conflicting context dates. Primary exchange bytes and taxonomy validation remain unverified. See [stage 2B](topics/xbrl-stage-2b.md).
- Added X12–X13. At the end of stage 2B the register contained 58 records, not 58 unique sources; the latest scope update above adds six more.

## What has actually been executed

- Seven small Python probes from the prior GitHub audit; full applications were not run.
- Checks on a pinned ipo-ai CSV.
- Aether worksheet calculations and 20 internal arithmetic residual checks, now preserved in Markdown.
- Read-only XML inspection of two repository fixtures: 61 facts/four contexts and five facts/three contexts. No Arelle validation or XBRL package installation.
- Aether PDF versus rendering: manually transcribed observations, deterministic unit conversion and differences; no automatic extraction accuracy test.
- Infosys archived-copy XML inventory and 16 comparisons to selected official PDF text; 35 differing-value groups under inspected matching aspects retained as conflict candidates. No XBRL validator run.

## Evidence limits

- Real Aether exchange filing was read through web-extracted HTML text. Direct local HTML download timed out.
- Official NSE XBRL information page was read through the browser tool. Direct download timed out; official sample/taxonomy packages were not downloaded.
- Inspected raw XML examples are repository test fixtures, not verified Aether filings. One is explicitly synthetic; both are treated as test evidence.
- Update: an additional XML copy attributed to a real Infosys filing was acquired through GitHub's public API, with its hash matching the repository manifest. This is not independently authenticated primary exchange evidence. Its annual reporting-start field conflicts with context dates.
- A taxonomy entry point downloaded from a repository is a vendored copy. Official package equivalence, completeness and version compatibility remain unverified.
- No proof that an Indian IPO RHP is generally available as an XBRL instance. Prospectus-specific restated statements and narrative remain necessary.
- Prior pilot's price-band advertisement, broker denominators and repeated-asset discrepancy remain open.

## Deferred XBRL stage 2C: primary evidence and taxonomy

Acquire one real non-financial Indian issuer's raw XML instance through an accessible public filing link or a user-provided file. Prefer Aether to connect with the existing work. Match it to the same-period PDF/rendered filing. Preserve bytes and hash, identify the exact taxonomy and context dimensions, and reconcile 10–15 facts.

The Aether companion PDF is now preserved. Raw XML acquisition remains unresolved after bounded public requests. Inspect whether the observed classification conflicts exist in the actual XML before attributing a cause. An alternative issuer is appropriate if it has a clear accessible raw filing route.

Completion means a primary XML instance plus a reproducible fact/context/unit table and a small reconciliation. A HTML rendering or synthetic fixture does not satisfy it. See [the roadmap](topics/xbrl-roadmap.md).

Stage 2B provides useful real-world-copy inspection, but does not close primary acquisition. Avoid spending repeated passes on the same access failures. Resume this thread when a clear public route or matching official taxonomy package is available.

## Prior research task — deferred by the scope change

Deep-read original financial-strength and IPO peer-valuation research. Establish what the score would measure, which populations the papers tested, and what validation would be needed for Indian IPOs. Produce a source-backed comparison and a proposed small evaluation design before choosing a model.

## Other prior open work, retained and deferred

1. Deep-read original F-score and IPO valuation papers; assess applicability before adopting scores.
2. Confirm original Aether price-band and post-offer share evidence.
3. Verify the repeated December-2020 asset figures and any corrigendum.
4. Repeat the metric dictionary on another issuer after the XBRL feasibility check.
5. Test comparable products on the same document and interview potential users.

## Product direction

Working hypothesis: a reproducible financial-research workflow with explicit accounting definitions, evidence per value, and reliable review of missing/conflicting inputs. XBRL could reduce extraction effort for listed peers and subsequent results. Neither product demand nor broad data coverage has been established.
