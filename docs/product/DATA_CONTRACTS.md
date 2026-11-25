# November exploration first-slice contracts

> Historical reference for the [archived portal](../../archive/portal-exploration-20261123/README.md). The [V2 prototype brief](../starter-kit/PROTOTYPE_BRIEF.md) guides the upgrade.

Version: `portal-contract-v1`, 2026-11-12. Implements a local subset of the [target framework](../architecture/IPO_Ready_Design_Framework.md), not the production database migrations. Domain packages stay independent of HTTP and presentation.

## Source observation

Required fields: immutable `id`, `company_id`, canonical `metric_id`, exact `source_label`, `raw_value` (string or null), `state`, `raw_unit`, `currency`, `period_start`, `period_end`, `basis`, `source_id`, `source_url`, `source_date`, `retrieved_at`, `evidence_path`, `evidence_sha256`, `locator` and `review_state`.

States: `reported`, `explicit_zero`, `missing`, `nil`, `not_applicable`, `conflicting`, `unresolved`. Only reported/explicit-zero observations can become numeric operands. Null is not zero. Decimal lexical input is authoritative; reject nonfinite values. Keep provider origin even after a transcription check. Unknown public-availability/source date and accounting basis stay null/unspecified. `transcription_checked` means checked against retained provider HTML, not primary filing approval.

M1 stores one active pre-IPO candidate (IGX), one recent-IPO reference (NSE) and three annual periods per company, INR crore, five observations per year. Provider `Revenue` is mapped provisionally to `provider_total_income`, with the source label retained and its sum checked against revenue from operations plus other income. This is a candidate mapping, not a universal provider taxonomy. Continuing-operations profit stays separate from total profit and owners' profit. Exact table/year/row anchors link all values to captured bytes. Unknown accounting standard and dimensions are not inferred.

## Derived result

`id`, `value` (decimal string or null), `unit`, `state`, `reason`, `formula`, `formula_version`, `operand_fact_ids`, `period_end`, `basis` and `review_state`. Available results remain `provisional_secondary`; arithmetic checks cannot promote them to primary-reviewed financial facts. YoY pairs must have matching definitions, units, basis and consecutive annual dates. Negative/zero growth bases are unavailable; negative continuing profit is allowed in the profit/revenue ratio. A nonpositive profit denominator suppresses cash conversion. CAGR uses actual elapsed fiscal years and positive endpoints.

M1 metrics: operating-revenue YoY; continuing-profit / operating-revenue percentage; CFO / continuing-profit; provider income-component residual. The last is a reconciliation, not an investment factor. CFO interpretation for an exchange requires settlement/client-money review; do not interpret a high ratio as superior earnings quality. Debt/EBITDA, ROE, P/E, ranking and predictive confidence are unavailable until reviewed compatible operands exist.

## Research snapshot

Immutable content-derived `snapshot_id`; `contract_version`; `calculation_version`; input-file SHA-256; source evidence SHA-256; source retrieval time separate from build time; source availability date unknown; `historical_reconstruction: true`; issuer, observations, per-period metrics, known limitations and coverage. M1 freezes annual FY24-FY26 coverage. More recent interim disclosures are outside this slice and must not be implied to be incorporated.

A snapshot is reproducible from the checked-in observation file and code. It is not a publication approval. Reference companies with no reviewed dataset get coverage records and exclusion reasons, not invented financial values. NSDL reference discovery is not peer approval.

## Scenario command/result

Input: company ID, selected annual period, operating-revenue growth percentage in [-30, 30], assumed continuing-profit / operating-revenue percentage in [0, 100]. All numeric inputs must be finite; reject booleans and missing/extra fields. This bounded one-year sensitivity has formula `base operating revenue * (1 + growth / 100) * assumed profit percentage / 100`. Return all inputs, base fact ID, base snapshot ID, formula version and hypothetical revenue/profit. No probability, recommended price, target return or forecast accuracy is asserted.

## HTTP adapter

`GET /api/snapshot`: prepared active-company projection. `GET /api/reference`: separately identified recent-IPO reference projection. `POST /api/scenario`: validated bounded scenario, no persistent write. Static browser assets use the same origin. `python -m portal.main` serves on loopback only; no authentication or production exposure. Operations/evidence view is read-only. A later FastAPI adapter can preserve these domain contracts while adding account authorization, durable jobs and reviewed publication.
