# IPO-Ready November exploration strategy

> Historical as of 23 November 2026. The milestones below describe the [archived exploration](../../archive/portal-exploration-20261123/README.md). Use the [starter prompts](../starter-kit/PROMPTS.md) for the fresh prototype.

Created: 2026-11-12. Working plan; visual design remains provisional.

## Product direction

Build an interactive investor analytics portal for unlisted/pre-IPO companies. Use recent IPO companies as dated research references and admit them to a peer cohort only after compatibility review. Start with free public sources in India; retain SEC and other jurisdictions as later adapters. The user's 2026-11-12 direction supersedes the older US-first planning queue and notebook/demo framing.

Design authority: [meeting framework](../architecture/IPO_Ready_Design_Framework.md), revision 2 dated 2026-10-29, from [commit 5b71ab3](https://github.com/atharvchavan2608/IPO-ready/tree/5b71ab3e0fea6dff294519fc2f6560aad5a059aa/docs/architecture). The framework is a target, not a claim of implemented services or verified free data access. Its first backlog item is contracts and a reviewed end-to-end dataset. Existing Aether/XBRL knowledge informs definitions, provenance and tests; it does not dictate the new interface.

## Delivery strategy

Each milestone produces a usable vertical slice and records evidence, verification and remaining gaps. Build one milestone at a time. Avoid building all the target services before validating a company workflow.

| Milestone | Deliverable | Completion condition | State |
| --- | --- | --- | --- |
| M0: align | Pinned design reference, this strategy, rough architecture and explicit data contracts | Current scope and next task are discoverable in repository entry points | Complete 2026-11-12 |
| M1: research workspace | One real pre-IPO candidate plus one recent IPO reference; interactive trends, evidence, Python ratios and sensitivity | Native source/hash; traceable decimal calculations; missing/basis limitations visible; meaningful engine and browser checks | Prototype complete 2026-11-12; primary financial review remains M2 |
| M2: free-data pipeline | WWIPL/UnlistedZone source adapters; two issuers; issuer-document reconciliation and exception review | Repeatable capture -> candidate observations -> reviewed facts -> snapshot; no silent overwrites; access/reuse limits recorded | Next |
| M3: comparisons | Recent IPO reference dataset and a small sector-compatible cohort | Period, basis, business-fit and definition gates; explainable exclusions; descriptive comparison before ranking | Queued |
| M4: modelling | Eligible relative valuation; assumptions and sensitivity tables; sector ratios | Dated price and share basis; compatible earnings; coverage gates; formula and scenario tests | Queued |
| M5: investor workflow | Screening, saved criteria, shortlists, watchlists and research changes | Version-pinned saves; clear changes and freshness; user review of usefulness | Queued |
| M6: operations | Persistent jobs/review, accounts, coherent releases, recovery and deployment | Authorization, source policy, restore/rollback and measured serving checks | Queued |
| M7: optional explanation | Grounded search/AI explanation of deterministic results | Verified citations and numerical consistency; useful beyond existing explanations | Deferred |

## Rough architecture

```mermaid
flowchart LR
    Public[Free provider pages and issuer disclosures] --> Capture[Bounded capture: native bytes and hashes]
    Capture --> Candidate[Source-specific candidate observations]
    Candidate --> Review[Definition / period / basis / conflict review]
    Review --> Facts[Versioned fact snapshot]
    Facts --> Python[Python metrics and scenario policies]
    Python --> Projection[Company / comparison read projections]
    Projection --> API[Product API]
    API --> UI[Investor dashboard]
    Review --> Ops[Research exceptions and coverage]
    UI --> Evidence[Operand facts and exact source anchors]
```

Target runtime follows the meeting proposal: React/TypeScript investor and operations views, modular Python/FastAPI API, separate background jobs, PostgreSQL and immutable object storage. M1 deliberately starts with a dependency-free browser interface and Python HTTP adapter; domain calculations and versioned JSON contracts are independent of that adapter. This is a replaceable local prototype, not completion of the production infrastructure backlog. Do not add authentication or hosted deployment to this first slice.

## M1 boundaries and data policy

Initially selected NSE India from the provider's unlisted category. Subsequent issuer-status review established its September-2026 listing; it is now a recent-IPO reference. IGX is the active pre-IPO candidate, supported by IEX's October-2026 call discussing its IPO in progress. This recorded correction demonstrates why provider categories and issuer status are separate. Source observations remain secondary and provisional until reconciliation; preserve provider labels and unspecified reporting basis. No forecast IPO date or executable price is asserted.

Use annual operating revenue, total income, continuing-operations profit and cash flow only where their definitions are supplied. Financial outputs disclose periods, denominator, source, state and calculation version. Missing/nil/zero/not-applicable/conflicting values remain distinct. A user-controlled one-period sensitivity is assumption arithmetic, not a forecast or investment recommendation. Do not calculate P/E from unreviewed EPS or compare companies with unknown reporting basis.

NSDL is a recent-IPO reference candidate (2025 listing); capture reference/discovery status first. A depository is not automatically a comparable exchange. Financial comparison and historical pre-offer reconstruction remain M3 work.

## Task checklist

- [x] Read existing research entry/status and inspect the latest design branch.
- [x] Pin the design baseline; retain the older implementation as historical reference.
- [x] Write strategy and rough architecture before implementation.
- [x] Retain bounded free-source capture with hashes and access failures.
- [x] Specify observation, derived-result and snapshot contracts.
- [x] Curate small real-source datasets with exact row/year anchors (IGX active, NSE reference).
- [x] Implement deterministic Python calculations and invalid-input handling.
- [x] Build and inspect the interactive company workflow.
- [x] Record executed checks, update research register/status and name the next bounded task.
- [x] Archive superseded code with original hashes and refresh the architecture package.
- [x] Add bounded Chittorgarh/expert-method findings and a later claim/evidence pipeline proposal.

Stop this pass after M1; do not attempt M2-M7 together. After M1, reconcile this issuer's selected observations against an issuer filing before expanding automated collection.
