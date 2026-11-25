# IPO-Ready: target fintech product architecture

Revision 2, 29 October 2026. This proposal defines the intended product independently of the GitHub mockup. The repository and supplied report describe objectives, data categories and examples; their implementation choices are not architectural constraints. The earlier design put too much weight on the curated demo and its reuse. This revision replaces that framing.

## 1. Product and design thesis

IPO-Ready is a financial intelligence and research advisory platform. It helps a user discover companies, compare relevant alternatives, evaluate financial quality, understand valuation and risks, select a defensible shortlist and monitor what changes. IPO issuers are the starting universe; relevant listed companies provide comparison context. Companies with inadequate disclosure can have coverage/status pages without unsupported financial conclusions.

The design is organized around investor decisions, intelligence models, trusted data and reliable delivery. Document processing enables those capabilities. Models should work on a reviewed dataset even if it was supplied manually; new models should not require redesigning source connectors.

There are two product experiences:

- **Investor application:** discovery/screening, company research, peer comparison, scenario evaluation, evidence explanations, saved criteria, shortlists, watchlists and research changes.
- **Research operations console:** coverage/freshness, data exceptions, classification and peer review, financial definitions, model-policy approval, publication and operational monitoring.

The initial launch supports explicit research criteria and disclosed ranking policies. User-selected weights create a distinct saved research view. A future personalized recommendation mode would require a separately designed profile, policy and evaluation workflow.

## 2. Diagram structure

The seven views are: C4 container architecture; C4 system context; logical intelligence design; data/model production lifecycle; evidence/version/consistency contracts; deployment/operating model; architecture decisions and roadmap. The overview is A2 landscape; supporting pages are A3 landscape.

In C4, a container is an application or data store, not necessarily Docker. Logical financial engines are components inside runtime containers. PostgreSQL stores can be separate schemas on one managed service initially. The diagram does not require a microservice per feature.

## 3. Product domains and ownership

| Domain | Owns | Output |
| --- | --- | --- |
| Company and offering universe | Canonical company IDs, source identifiers, classifications and offering versions | Company/offer catalog and eligible universe |
| Evidence and data operations | Acquisition, source versions, parsing, canonical mapping and review cases | Approved point-in-time facts and narrative |
| Financial intelligence | Metric definitions, features, business/financial factors and lineage | Versioned metric/factor results |
| Comparable-company research | Peer rules, matching, approved sets and compatibility exclusions | Reproducible comparison cohort |
| Valuation and scenarios | Price/share compatibility, market snapshots and assumptions | Relative valuation and scenario results |
| Screening and selection | Filters, factor orientation, weights, missingness and ranking policy | Explainable shortlist and factor contributions |
| Research publication | Run manifests, release decisions, projections and report history | Immutable published research snapshot |
| User workspace | Accounts, criteria, comparison sets, bookmarks, watchlists and private annotations | Account-scoped saved research |
| Monitoring and changes | Snapshot differences, watchlist rules and freshness | Relevant company/research changes |
| Evidence explanation | Source retrieval, verified results and optional LLM adapter | Cited explanation tied to a snapshot |

## 4. Runtime responsibilities

**Web applications:** TypeScript/React investor and operations interfaces. They can share a frontend deployment with different permissions. Responses show snapshot identity, coverage and relevant as-of times. This technology choice is proposed independently of the mockup.

**Product API:** A modular Python/FastAPI backend handles queries and business commands: screen companies, compare peers, request a scenario, save a shortlist, review an exception, approve a model policy or publish research. It authorizes account and analyst operations. It does not parse long filings or run heavy models inside normal browsing requests.

**Data workers:** Source-specific adapters version evidence; parsers extract document or structured observations; normalization preserves original definitions; quality rules reconcile and route exceptions. Parser failures retain evidence for bounded repair.

**Intelligence workers:** Execute financial features, peer sets, factor/ranking policies, valuation scenarios, research packaging and change detection. They consume approved point-in-time snapshots and pinned policy versions. Data and intelligence pools can scale separately while sharing code packages.

**Durable queue:** Explicit job IDs, typed inputs, dependencies, attempts, states and idempotency keys. Start with durable database jobs or a managed queue. Deterministic validation failures become review cases rather than infinite retries. A dispatcher processes committed outbox events.

**PostgreSQL:** Separate logical schemas for operational records, research facts/features/model registry, and published read projections. Ordinary versioned tables can implement the feature/model metadata layer; a separate vendor feature-store platform is not required.

**Object storage:** Immutable source files, parser artifacts, cited sections, model artifacts and frozen reports. Database records retain object keys/checksums. File existence does not imply fact acceptance or publication.

**Identity and optional LLM adapters:** Identity provides sign-in/tokens; the API enforces permissions. A language model receives constrained tool results and cited text. It is not the authoritative calculator, ranking-policy owner or publisher. Start with full-text retrieval; add a separate search/vector service only if useful under measured workload.

## 5. How models support company selection

### Eligible universe and peers

Resolve company/offer identities. Apply explicit sector, geography, offer status, size, cutoff and coverage criteria. Keep reasons for excluded candidates. Peer selection uses business/industry fit and scale, then checks reporting dates, basis, metric definitions and coverage. Analyst-maintained sets and deterministic matching can coexist. Store peer-set version, rationale and rejected members.

### Financial features

Calculate growth, profitability, leverage, liquidity and cash conversion on reviewed definitions and matching periods. Add sector-specific features only with available inputs. Store formula/version, operand fact IDs, period, basis and availability state. A derived feature remains separate from a reported fact. Missing values never default to zero.

### Quality, risk and valuation

Keep financial quality, financial risk, valuation and data coverage as separate outputs. A model policy defines applicable metrics, factor orientation, transformations, outlier handling, weights and thresholds. Transparent sector-relative factors and filter/sort policies can provide useful advice without machine learning.

Valuation requires compatible prices, earnings/share basis, debt/cash definitions and dated market inputs. Relative multiples and explicit price/earnings scenarios are initial methods. DCF/forecast methods are optional separately versioned extensions with explicit assumptions and evaluation. Invalid/negative denominators produce unavailable or alternative-method states rather than spurious multiples.

### Ranking and explanation

Rank only within a named eligible cohort under a disclosed policy. Store membership, sample size, weights, factor contributions, missing-data treatment, tie handling and policy version. A minimum coverage/cohort gate can suppress ranking while retaining descriptive research. Avoid silent weight renormalization that rewards sparse data.

Users see advantages, drawbacks and scenario sensitivities. They can compare candidates and inspect how changing criteria changes the shortlist. Saved selections reference exact research versions and criteria. AI explains supplied results and cited disclosures; it does not invent scores or hidden arithmetic.

### Monitoring

New filings, prices, corrections or policy versions trigger dependency-aware recomputation. Watchlist logic compares successor snapshots for meaningful changes such as a revised factor, valuation scenario, material disclosure, offering status or lost coverage. In-app alerts are part of the proposed experience; external delivery can be added as another adapter.

## 6. Listed data and application use

Data access is assumed adequate for this proposal. No new source/API feasibility search was performed. These are source-adapter candidates from existing project context:

| Existing or listed input | Extract/capture | Where it is used | Important boundary |
| --- | --- | --- | --- |
| SEBI DRHP/RHP and amendments | Restated statements, business, risks, sector, peer names, offering terms | Issuer facts, financial trends, peer discovery, offer context, cited disclosures | Preserve each document version and its public availability date. |
| SEC S-1/F-1 and amendments | Public pre-offer statements, business/risk sections, offer structure | The same issuer workflow through a different source adapter | An initial filing, amendment and later annual report are different evidence versions. |
| NSE/BSE result disclosures, annual reports and XML/XBRL candidates | Listed-peer financial facts, contexts, units, reporting basis and notes | Peer metrics, historical comparisons, selected valuation denominators | Decode periods and dimensions; a familiar concept name is insufficient. |
| SEC Submissions JSON / filing indexes | Issuer IDs, filing type, accession, public release time and document links | Registry, discovery, refresh scheduling and evidence timeline | Metadata does not provide financial statements by itself. |
| Eligible Company Facts or other structured financial JSON | Supported concepts with filing/date/unit context | Candidate structured financial input, especially for peers | Filter to the analysis cutoff and confirm coverage. Do not substitute later facts for original pre-offer evidence. |
| Company annual reports and IR documents | Statements, notes, issuer KPIs and supplementary disclosure | Fill documented coverage gaps and explain financial definitions | Keep issuer-defined KPIs distinct from standardized metrics. |
| Price-band notices, final offer details and share records | Dated price range, primary/secondary shares, post-offer dilution and share basis | Offer context and valuation eligibility | Selling-holder proceeds and company proceeds remain separate. |
| Dated peer market prices | Price, currency, date, relevant share basis | P/E and other explicitly defined market multiples | A price date and denominator period must accompany every multiple. |
| Screener/broker/secondary references | Candidate peers, cross-checks and explanatory context | Discovery and review support | Keep secondary origin labelled; do not silently promote a reference into a reviewed primary fact. |
| Optional Aether reference fixture | 22 reported/issuer-defined metrics across five annual/interim periods, units, source pages and notes | Adapter and numerical-regression test fixture | A manually curated historical pilot with unresolved issues; not an automatic extraction benchmark. |
| FinQA, TAT-QA, FinanceBench and research papers in the source register | Evaluation examples and methodological ideas | Optional question-answering evaluation or design references | These are not issuer financial feeds. They do not populate the IPO universe or validate investment scores. |

Core product records include Company, OfferingVersion, DocumentVersion, FactVersion, NarrativeSection, MetricFeatureSet, PeerSetVersion, MarketSnapshot, ModelPolicyVersion, ResearchRun, ResearchSnapshot, SavedCriteria, Shortlist and Watchlist.

Research/QA datasets such as FinQA, TAT-QA and FinanceBench inform evaluation, not the issuer universe. The curated Aether dataset is an optional adapter/calculation fixture; it does not determine the product topology or feature scope.

## 7. Point-in-time data and reproducibility

Store the original concept/label, raw lexical value, unit/scale, actual fiscal dates, full context dimensions, reporting basis, accounting standard and exact source anchor. Normalize into Decimal-valued fact versions with mapping and review state. Preserve missing, nil, explicit zero, not applicable, conflicting and unresolved observations distinctly.

Record both when the source became public and when the platform obtained/learned it. The analysis cutoff constrains public evidence; market snapshots carry their own as-of dates. Historical reconstruction is labelled. Amendments create new versions and never rewrite older run inputs.

A run manifest pins source/fact snapshots, financial periods, cutoff, market times, currency/basis policies, metric definitions, features, code version, peers, ranking policy, factor weights, missingness rules, scenario assumptions, model artifacts, evaluation and release decisions. A result can expand to factors, formulas, operands and evidence.

## 8. Research production versus product serving

Acquisition, review and model execution are asynchronous write-side workflows. Investors browse prepared, approved projections for screeners, companies, comparisons and scenarios. This is pragmatic command/query separation and can initially share one PostgreSQL service.

Every response identifies snapshot and freshness. Comparisons pin compatible research versions rather than joining arbitrary latest rows. An on-demand scenario returns an accepted job ID; the completed result is stored against its input versions and parameters.

Prepare projections before switching a published pointer. Retain a previous valid snapshot if refresh fails. Cache keys include snapshot and normalized query/criteria identity. Display freshness/lag instead of mixing old metrics and silently refreshed market observations.

Write business state and its outbox event in one database transaction. Dispatch committed events; consumers deduplicate by event/job ID and process changes idempotently. Publication emits invalidation/change events. This supports reliable asynchronous refresh without requiring full event sourcing.

## 9. Model lifecycle and evaluation

The model registry stores definitions/artifacts, applicable sectors, assumptions, evaluation results, status and promotion decisions. It can be PostgreSQL metadata plus object files. Lifecycle: draft -> implemented -> tested -> evaluated -> approved -> active -> superseded/rolled back.

| Area | Evaluation evidence |
| --- | --- |
| Data | Reviewed reference facts, units/contexts, correct evidence locations |
| Calculations | Manual comparisons; period and denominator edge cases |
| Peers | Business-fit review, cohort stability and exclusions |
| Selection | Factor contributions, missingness bias, weights/outlier sensitivity |
| Valuation | Price/share/earnings compatibility and assumption sensitivity |
| Explanation | Citation accuracy, numerical consistency, unsupported-claim checks |
| User value | Ability to understand a comparison and justify a shortlist |
| Operations | Freshness lag, failed/duplicate jobs, restore success, query latency |

Arithmetic correctness is separate from predictive validity. A future return-prediction model would require defined labels, point-in-time cohorts, withdrawals, survivorship controls and temporal evaluation before predictive claims.

## 10. Deployment and growth

Launch with a modular backend, separately runnable workers, PostgreSQL, durable jobs and private object storage. Use HTTPS, scoped identities, secrets, account/role permissions, database recovery and artifact backups. Correlate request/job/run IDs and test restore/rollback. Shared financial evidence remains separate from private account research.

Use CDN/static delivery and managed services where practical. Add cache/read replicas for measured serving pressure, worker replicas for backlog, a search service for retrieval pressure and a warehouse for large analytical scans. Extract a service only for justified isolation, scaling or ownership needs. Kubernetes, Kafka and a dedicated feature store are not launch requirements.

Validate proposed nonfunctional targets under agreed workload: responsive prepared queries, explicit freshness, recoverable jobs, coherent snapshots and no duplicate release. No measured latency, availability, extraction accuracy or investment accuracy is claimed.

## 11. Decisions and scope

| Decision | Choice | Trade-off |
| --- | --- | --- |
| Viewpoint | Target product; C4 plus separate logical/model/deployment views | Multiple views, each with a clear abstraction level |
| Backend | Modular application with domain contracts | Services can be extracted when justified |
| Compute | Background data/intelligence pools | Job orchestration added; browsing stays lightweight |
| Serving | Approved, versioned projections | Eventual freshness needs timestamps/invalidation |
| Financial state | Point-in-time versions and lineage | More metadata, stronger reproducibility |
| Advice | Transparent sector/cohort policies | Advanced models need more data/evaluation |
| AI | Replaceable grounded component | Optional interaction improvement, no numeric authority |

Begin with a covered non-financial sector and selected market; add jurisdictions/sectors through adapters and model policies. Brokerage execution, custody and a live trading engine are separate scopes.

## 12. Primary architecture references

Checked 29 October 2026:

- [C4 context](https://c4model.com/diagrams/system-context) and [container](https://c4model.com/diagrams/container) guidance separates external relationships from internal runtime/data-store responsibilities. Other views describe deployment and models.
- [Microsoft Azure Architecture Center: CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) supports distinct command/query models, including a shared-store implementation. Applied to research production versus prepared reads.
- [AWS transactional outbox guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) motivates atomic state/event writes and idempotent consumers. Applied to source/model changes and publication refresh.

These references inform architectural patterns. The product requirements, financial policies, vendor choices and specific domain boundaries are proposed design judgments for IPO-Ready.

Context inputs are the [repository](https://github.com/atharvchavan2608/IPO-ready), its data contract/dictionary/source register and the supplied AI-generated report. Their objectives and listed data were considered; their code structure and API claims are not treated as authoritative design decisions. All components shown remain proposed.
