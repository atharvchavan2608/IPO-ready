# Implementation backlog

Baseline: 29 October 2026. All implementation tasks are pending.

1. Specify company, offering, evidence, fact, peer, model-policy, run and research-snapshot contracts and database migrations. Preserve raw/canonical values, temporal eligibility, source anchors and missing states.
2. Establish modular backend/domain interfaces, durable job contracts and investor/operations access boundaries.
3. Implement one reviewed-data adapter and financial reference suite; use curated pilot only as a labelled fixture and preserve unresolved issues.
4. Build published company, screener and comparison projections with snapshot/freshness identifiers.
5. Implement peer membership, compatibility gates and explainable exclusions for a representative cohort.
6. Implement versioned financial factors, explicit selection policies and eligible valuation/scenario models. Test missingness, invalid denominators, factor contributions and weight sensitivity.
7. Add account-authorized saved criteria, shortlists and watchlists.
8. Add source adapters, extraction, quality rules and material-exception review.
9. Add outbox dispatch, idempotent jobs, dependency-aware refresh, atomic publication and change detection.
10. Add optional cited retrieval/explanation after deterministic research works.
11. Verify recovery, release rollback, freshness and serving performance before expanding coverage.

First work item: domain/schema contracts and a reviewed end-to-end fixture independent of the mockup UI. Sector/jurisdiction scope and numeric model thresholds remain decisions to validate.
