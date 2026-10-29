# Eraser AI brief: target fintech product architecture

This is a natural-language diagram specification, not proprietary Eraser DSL. The target is the proposed product, independent of the repository mockup.

Create a large C4 container diagram for IPO-Ready, a financial intelligence platform for discovering companies, comparing peers, assessing financial quality/risk/valuation, selecting shortlists and monitoring changes.

Use an explicit system boundary. Inside it, place an Investor Web App and Research Operations Console above a modular Python Product API. Proposed frontend: React/TypeScript. Proposed API: Python/FastAPI. The API owns discovery/screening, comparisons, saved criteria, shortlists/watchlists, research queries, review commands and publication commands. Web interfaces call it over HTTPS/JSON.

Below it show a Durable Task Queue, Data Processing Workers and Intelligence Workers. The API schedules asynchronous research/refresh/scenario work. Data workers acquire immutable source versions, extract facts and narrative, normalize/reconcile and route exceptions. Intelligence workers compute features, peer matching, sector factor/ranking policies, valuation scenarios, research packaging and change detection. Expensive parsing/models/AI must stay outside normal browsing requests.

At the bottom show four internal logical stores:

- Application Database [PostgreSQL]: accounts, criteria, shortlists/watchlists, reviews, jobs, release state and outbox.
- Research Database [PostgreSQL]: point-in-time facts, features, peer sets, model registry, research runs and lineage.
- Evidence/Artifact Store [Object Storage]: immutable filings, source snapshots, parsed text/tables, model artifacts and frozen research payloads.
- Research Read Models [PostgreSQL]: approved screener, company, comparison, scenario and evidence projections; optional cache.

The API writes authorized commands and queries read models. Data workers write facts/evidence. Intelligence workers read approved facts, policy versions and market snapshots, then prepare versioned research projections. Responses identify the research snapshot, coverage and relevant as-of dates. PostgreSQL responsibilities may share one physical service at launch.

Outside the boundary show External Identity Provider, Financial Disclosure/Market Systems and Optional LLM Provider. Identity handles sign-in/tokens; the API enforces permissions. Source adapters cover filing indexes, prospectus/amendments, listed-peer reports/XML/XBRL/JSON, offer terms and dated market prices. Metadata locates filings; it is not itself financial statements.

Connect intelligence workers to the LLM using constrained retrieval/explanation tools. The LLM receives verified results, contributions and cited passages. It cannot overwrite accepted facts, invent authoritative arithmetic/ranking policy or publish. Optional search/embedding indexes are rebuildable derivatives, not sources of truth.

Add a cross-cutting band for role/account access, audit, source lineage, model versions, observability, secrets and recovery. Reliable refresh uses atomic state/outbox writes, idempotent workers, dependency-aware computation, coherent publication pointers and cache/watchlist updates. Earlier snapshots remain frozen.

Create a separate logical intelligence diagram: research criteria -> eligible universe -> business-fit peer selection -> financial features -> sector quality/risk factors plus valuation scenarios -> disclosed cohort ranking -> contributions/sensitivities/evidence -> saved shortlist and change monitoring. Quality, risk, valuation and coverage remain distinct; persist weights, cohort, missingness rules and model version.

Colors: blue applications/workers; teal stores/trusted outputs; gold external systems; dashed purple optional AI. Label each relationship. Keep context, runtime/container, logical models and deployment as separate views. Avoid mandatory Kubernetes/Kafka, a service per metric, broker custody/trading modules, opaque 'AI predicts IPO success' boxes or mockup-file-centered architecture.
