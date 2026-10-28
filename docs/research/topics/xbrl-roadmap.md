# Bounded XBRL research stages

The user explicitly allowed multiple stages. Stage transitions depend on evidence, not elapsed time. This roadmap is research planning, not a commitment to build every capability.

| Stage | Question | Bounded work | Exit evidence | State |
| --- | --- | --- | --- | --- |
| 1. Reconnaissance | Which sources and formats exist? | Official directories, one real rendered filing, selected parser code and fixtures | Source map and explicit limitations | Complete for this bounded scope |
| 2. One real instance | Can we preserve and interpret a raw filing? | One non-financial issuer; exact XML, companion report and exact taxonomy | Hash, contexts, units, validation log and 10–15 reconciled facts | Next |
| 3. Small coverage study | Does the approach survive variation? | Roughly 3–5 issuers, at least two periods, standalone/consolidated and one revision if available | Coverage and mismatch table; no extrapolation to all issuers | Pending |
| 4. Semantic mapping | Can we compare metrics consistently? | Ten core metrics across observed taxonomy versions | Versioned mappings, definitions, exclusions and regression cases | Pending |
| 5. Historical evaluation | What was available at the time? | Preserve publication/revision times; reconnect with IPO assessment cutoffs | A reproducible as-of reconstruction | Pending |
| 6. Agent integration | Where does agency add value? | Tool contracts for discovery, discrepancy review and explanation | Agent uses verified facts and deterministic calculations with traceable evidence | Pending |

## Stage 2 procedure

1. Identify a specific filing and its publication metadata through a public source. Prefer the same Aether September-2025 period already inspected; an accessible alternative non-financial issuer is acceptable and must be named.
2. Obtain native XML and preserve bytes, URL and hash. Record retrieval failures without treating them as missing company data. Do not mistake an HTML report for an XML instance or infer an unobserved download URL.
3. Inspect root format, namespace URIs, schemaRef and actual contexts/units. Distinguish monetary, per-share and pure/ratio units.
4. Resolve the exact taxonomy package and dependencies, or explicitly record why validation remains partial. Do not silently date-substitute schemas.
5. Run a standards-aware validator if the matching package is available. Save logs and distinguish instance validity from economic correctness.
6. Reconcile operating revenue, other income, total income, PBT, tax, PAT, D&A and finance costs; add balance sheet/CFO where the filing provides them. Keep quarter and YTD separate.
7. Produce a small fact table with full source metadata and mismatches. Record remaining coverage gaps before attempting more issuers.

## Deliberately deferred in this stage

Bulk exchange crawling, full MCA ingestion, financial institutions' taxonomies, universal concept mapping, live updates, prediction models and multi-agent application architecture. These are separate scope decisions after feasibility evidence.

## Stage 2 progress, 2026-10-22

[Stage 2A](xbrl-stage-2.md) preserves and reconciles the real companion PDF against the exchange rendering. Raw-instance acquisition remains open, so the original stage-2 completion criterion is not yet met. Next is stage 2B: accessible primary XML, actual concept/context/unit inspection, and targeted review of the observed classification conflicts.

## Stage 2B progress, 2026-10-22

[Archived Infosys XML inspection](xbrl-stage-2b.md) records 417 facts, 81 contexts and four units. Sixteen selected numbers match official PDF text, but annual contexts conflict with explicit reporting-start fields. Original primary-download criterion remains open; defer primary verification and exact-taxonomy validation to stage 2C. Return next to financial-strength and IPO peer-valuation literature, keeping this bounded XBRL research available for later development.
