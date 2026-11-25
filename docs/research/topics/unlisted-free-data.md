# Free-source portal pilot

> This note records the [archived November exploration](../../../archive/portal-exploration-20261123/README.md). Use it when its coverage or methods inform the [V2 upgrade](../../starter-kit/PROTOTYPE_BRIEF.md).

Updated: 2026-11-12. Evidence classes: real secondary HTML, selected issuer PDF sections, executed local arithmetic and synthetic edge cases. This is a prototype dataset, not primary-reviewed reporting.

## Decision and scope

For this exploration, the user prioritised an interactive investor portal for unlisted/pre-IPO companies, with recent IPOs as references and unpaid data first. [N01](../sources/N01.md) pins the prior meeting architecture. The earlier US-first candidate work remains reusable. The [historical build strategy](../../product/BUILD_STRATEGY.md) records how this slice was staged.

## Source observations

| Source | Actual access/review | Implementation consequence |
| --- | --- | --- |
| [WWIPL NSE, N02](../sources/N02.md) | Native HTML 200; 15 exact row/year observations checked; basis absent | Reference dataset, provisional definitions |
| [UnlistedZone NSE, N03](../sources/N03.md) | Indexed search page; direct HTTP 404 retained | No facts imported; alternative clear route deferred |
| [NSDL annual report, N04](../sources/N04.md) | Selected web-extracted listing section, printed p61 | Reference identity only, no financial comparison |
| [WWIPL IGX, N05](../sources/N05.md) | Native HTML 200; 15 observations checked | Active company page and calculations |
| [IEX transcript, N06](../sources/N06.md) | Native PDF; physical p7/printed p6 IPO paragraph | Dated IGX pre-IPO context, no promised schedule |
| [NSE status, N07](../sources/N07.md) | Native PDF after size-bounded retry; note 7 | NSE recent IPO classification overrides stale provider category |

The first NSE candidate was selected from the provider's unlisted category, then reclassified when issuer evidence showed a 24 September 2026 listing. IGX became the active pre-IPO case. This is an executed example of stale source classification, not evidence that all provider fields are unreliable. The November IEX transcript includes later interim information; the first dataset deliberately covers annual FY24-FY26 only.

## Calculations and interpretation

Five selected items per company/year: operating revenue, provider-labelled Revenue (candidate total-income mapping), other income, continuing-operations profit and CFO. Original lexical values and INR crore remain separate from display conversions. Basis is unspecified, not inferred consolidated. See the [archived observations](../../../archive/portal-exploration-20261123/portal/data/observations.json).

Python calculates annual revenue growth, elapsed-year CAGR, continuing-profit/operating-revenue percentage, CFO/continuing-profit and income-component residual. A zero residual checks selected addition only. Profit includes other-income effects; the ratio is not operating margin. Clearing/settlement and client-money flows can dominate exchange CFO, so a high cash-conversion ratio is not an automatic strength.

The sensitivity model changes one-year revenue growth and assumed profit/revenue percentage. It has explicit input bounds and lineage. It is not a calibrated forecast. No price, EPS, P/E, distress score, ranking or automatic peer approval is supplied.

## Executed reproducibility

- `python research/unlisted_source_probe.py`: first run, four sandbox connection failures; second network-enabled run, WWIPL/NSE index 200, UnlistedZone 404, NSDL index certificate-chain failure. Separate manifests retained.
- `python research/unlisted_source_probe.py --followup`: six exact requests; WWIPL IGX, IEX transcript, Chittorgarh home, Canara note and ICICI note 200; NSE filing exceeded 5 MB cap.
- `python research/unlisted_source_probe.py --editorial`: review-index HTML 200, content inspected; zero captured review rows.
- `python research/unlisted_source_probe.py --issuer-status`: one explicit 16 MB cap; complete NSE filing retained. No login/challenge bypass, TLS disabling or repeated crawling.
- `python research/prepare_unlisted_pilot.py`: original NSE draft, then final IGX/NSE curation; final 30 exact checked observations. Read-only against native HTML; no generic scraper.
- `python -m portal.snapshot`, `python -m unittest discover -s tests -v`, and headless browser check; final results in [build status](../../BUILD_STATUS.md).

All run folders and request hashes remain under [native evidence](../../../research/unlisted_sources_20261112/). HTTP 200 is access evidence only. Source availability/publication time and reuse rights remain separate questions. No public release of retained third-party evidence was performed.

## Former next task

Reconcile IGX's five selected FY25/FY26 items against one accessible issuer filing. Retain that document/hash, confirm reporting basis, actual dates, cash-flow composition and continuing-profit definition; preserve differences as exceptions. Then specify one reusable source adapter with reviewed fixtures. Do not expand a company cohort or deploy unattended refresh before this small check is complete.
