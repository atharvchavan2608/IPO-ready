# On-demand company acquisition

24 November 2026 · V2-14 through V2-16. [Source register and receipts](../sources/N21.md)

## Workflow

The investor opens **Look up on NSE** on Page 1 or Page 2, searches by company name, ticker or ISIN, and chooses a result. The Python adapter checks NSE's EQ directory, reads a bounded dated close and validates the symbol and annual reporting basis on a designated Screener.in page. It saves native successful captures and failure receipts when fetching. The same ratio, cash-flow and research functions build the local company JSON. A catalogue overlay makes it visible in the dashboard, mixed screener, comparison and allocation without rewriting the base snapshot.

The adapter uses specific public endpoints and places identity, annual numbers and dated market data in separate fields. It checks exact symbols and source basis before admitting values. Companies with missing statements, stale or missing quotes, or unclassified sectors are shown with gaps. These conditions prevent unsupported scenario sizing. A sourced identity-only attachment remains available for cases outside the NSE adapter.

## Method decision and execution

The alternatives were open-web retrieval at add time, and a bounded resolver with a stable identity source. An open-web result could lead to a namesake, an unrelated fiscal basis or an indicative price with no matching date. The bounded workflow uses deterministic extractors and a confirmed ticker as the join. The installed prototype supports the retained NSE and source-cache path. More issuers can be supported by adding separate identity and source adapters.

The offline execution added BSE and CDSL, each with standalone annual data, three dated closing observations and source links. API tests cover a successful first add, a duplicate, a mixed screen, malformed input, an unknown symbol, an ISIN fixture and a missing-financials path for HDFC Bank.

The desktop browser first imported Astral from the full online directory and got twelve standalone annual periods (FY2015–FY2026) and one ₹1,225.00 NSE close dated 23 November 2026. Its shared details showed both source links. Searching the exact ISIN reopened the same record, reload preserved the column, and the Page 1 lookup passed the company to Page 2. Astral also appeared in the mixed revenue screen with retained data. [First-add preview](../../../outputs/v2-steering/verified/lookup-astral-desktop.png) · [Browser result](../../../outputs/v2-steering/verified/lookup-astral-checks.json)

With the full NSE directory retained, offline search can identify more companies than the locally retained annuals and quotes cover. If the directory is unavailable, search falls back to covered NSE close symbols and names from the reviewed catalogue or portfolio. Quotes use retained trading dates. A fresh import can have one dated observation and a partial or unavailable history.
