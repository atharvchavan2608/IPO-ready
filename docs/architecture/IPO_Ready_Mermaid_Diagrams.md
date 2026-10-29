# IPO-Ready: target product Mermaid sources

Revision 2, 29 October 2026. These semantic diagrams complement the seven-view PDF and diagrams.net layout. The design is independent of the GitHub prototype.

## Container architecture

```mermaid
flowchart TD
    subgraph Product["IPO-Ready system boundary"]
        Web["Investor web app"]
        Console["Research operations console"]
        API["Product API and domain services"]
        Queue[("Durable jobs and outbox dispatch")]
        Data["Data processing workers"]
        Models["Intelligence workers"]
        Ops[("Application database")]
        Research[("Point-in-time research database")]
        Objects[("Evidence and model artifacts")]
        Read[("Published research projections")]
        Web -->|HTTPS queries and commands| API
        Console -->|Review and release commands| API
        API -->|Authorized writes| Ops
        API -->|Prepared queries| Read
        API -->|Schedule work| Queue
        Queue -->|Data jobs| Data
        Queue -->|Model and scenario jobs| Models
        Data -->|Facts and review cases| Research
        Data -->|Immutable evidence| Objects
        Models -->|Approved facts and policies| Research
        Models -->|Read or write artifacts| Objects
        Models -->|Versioned projections| Read
    end
    Providers["External disclosure and market systems"]
    Identity["External identity provider"]
    LLM["Optional LLM provider"]
    Data -->|Acquire source versions| Providers
    API -->|Validate identity| Identity
    Models -.->|Grounded explanation tools| LLM
```

Database nodes can be schemas on one PostgreSQL service. Workers share domain packages but have distinct job types. A durable DB job table is a valid launch queue implementation.

## Product context

```mermaid
flowchart TD
    User["Investor or research user"] -->|Discover, compare, evaluate, shortlist, monitor| IPO["IPO-Ready financial intelligence platform"]
    Analyst["Research and operations team"] -->|Manage coverage, models and releases| IPO
    IPO -->|Acquire disclosures and dated prices| Sources["Financial disclosure and market systems"]
    IPO -->|Authenticate accounts| Identity["Identity platform"]
    IPO -.->|Cited explanation| LLM["Optional language model"]
```

## Intelligence and selection

```mermaid
flowchart TD
    Criteria["Saved research criteria and cutoff"] --> Universe["Eligible company universe"]
    Facts["Approved point-in-time facts"] --> Features["Financial metrics and sector features"]
    Universe --> Peers["Peer matching and compatibility gates"]
    Features --> Peers
    Peers --> Quality["Quality and financial-risk factors"]
    Peers --> Value["Valuation and scenario models"]
    Market["Dated market and offer snapshots"] --> Value
    Policy["Versioned selection policy and weights"] --> Rank["Cohort-relative ranking and trade-offs"]
    Quality --> Rank
    Value --> Rank
    Rank --> Explain["Contributions, sensitivities and evidence"]
    Explain --> Shortlist["Saved shortlist linked to research versions"]
    Shortlist --> Monitor["Watchlist research-change detection"]
```

Keep financial quality, risk, valuation and coverage distinct. Cohort and minimum coverage are explicit; missing inputs never silently become zero or a better rank.

## Research lifecycle

```mermaid
flowchart TD
    New["New filing, price, correction or policy"] --> Acquire["Preserve source version"]
    Acquire --> Extract["Extract facts and cited narrative"]
    Extract --> Normalize["Map definitions, dates, units and basis"]
    Normalize --> Gate{"Quality and eligibility pass?"}
    Gate -->|No| Review["Review exception or repair"]
    Review --> Normalize
    Gate -->|Yes| Facts["Freeze approved fact snapshot"]
    Facts --> Run["Compute features, peers, models and scenarios"]
    Run --> Evaluate["Evaluate output constraints"]
    Evaluate --> Publish["Approve and prepare coherent projections"]
    Publish --> Pointer["Atomically release snapshot pointer"]
    Pointer --> Serve["Serve company, comparison and screener reads"]
    Pointer --> Event["Committed invalidation and change event"]
    Event --> Refresh["Idempotent watchlist and cache refresh"]
```

## Core data relationships

```mermaid
erDiagram
    COMPANY ||--o{ OFFERING_VERSION : issues
    COMPANY ||--o{ DOCUMENT_VERSION : discloses
    DOCUMENT_VERSION ||--o{ FACT_VERSION : evidences
    DOCUMENT_VERSION ||--o{ NARRATIVE_SECTION : contains
    FACT_VERSION ||--o{ FEATURE_OPERAND : contributes_to
    METRIC_FEATURE_SET ||--o{ FEATURE_OPERAND : contains
    PEER_SET_VERSION ||--o{ PEER_MEMBER : contains
    COMPANY ||--o{ PEER_MEMBER : participates_in
    METRIC_FEATURE_SET ||--o{ RESEARCH_RUN : input_to
    PEER_SET_VERSION ||--o{ RESEARCH_RUN : selected_for
    MODEL_POLICY_VERSION ||--o{ RESEARCH_RUN : governs
    RESEARCH_RUN ||--o{ RESEARCH_SNAPSHOT : produces
    ACCOUNT ||--o{ SAVED_CRITERIA : owns
    ACCOUNT ||--o{ SHORTLIST : owns
    ACCOUNT ||--o{ WATCHLIST : owns
```

Run-input association tables also pin market/offer versions, criteria, scenarios and artifacts. Shortlist entries reference exact research versions. These are logical entities, not a complete migration specification.
