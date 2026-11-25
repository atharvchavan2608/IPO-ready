# IPO-Ready V2 working state

25 November 2026 · V2.1 · Pipeline 0.10.0 · Offline build 20261125T065438Z. The [V2 brief](PROTOTYPE_BRIEF.md) and [owner steering](steering.md) govern further work.

## Product strategy

Help an investor move from a company or a budget to a traceable diligence decision. Page 1 gives the company record with figures, periods and sources. Page 2 keeps the selected companies, comparisons, discovery and scenario together. Prioritise data that changes a decision, make incompatible observations inspectable, and require verified constraints before suggesting an illustrative position. Prove both journeys on a small set of real disclosures before widening the catalogue.

Lead with the two evidence-backed pre-IPO issuers. Compare IGX with IEX on matched energy-exchange operating rows, and use Lemon Tree for a narrow Oravel business-model reference. Leave the named company visible if its executable terms are missing. The client playbook follows the same four research questions for each issuer and uses zero reserve for the primary allocation example.

- **Company in mind.** Open IGX on Page 1, add it to Page 2 with its period, compare operating metrics against IEX and open IGX's detailed cash bridge. Add a distinct-sector company to expose the comparison gates. Start the ₹10 lakh example with IGX explicitly requested. Preserve IGX when its lot or liquidity constraint prevents a position. Show the diversified alternative and the change against the same assumptions without IGX.
- **Budget first.** Set ₹10 lakh, tolerance, horizon and liquidity needs. Run a documented query, inspect why candidates qualify, and shortlist candidates from the results. Add one result as a comparison column and open its full detail. Run the diversified scenario from that shortlist. If evidence or diversification is weak, show cash or an eligible liquid alternative and the diligence needed to use the shortlist.
- **Workspace state.** Share a serialisable state containing ordered company IDs, per-company period and basis, expanded detail section, query text, executed result build ID, explicitly shortlisted IDs, requested company ID and scenario inputs. Keep the requested ID independent of the shortlist and compare order. Revalidate stored IDs, quotations and eligibility against the current build on restore, and surface stale or unresolved records.

## Architecture decisions

| Status | Decision | Rationale |
| --- | --- | --- |
| Used | Retain `ipo_ready.pipeline`, Flask, static JS/CSS, native capture manifests, SHA-256 PDF text cache and dated per-company JSON. | The baseline runs offline and its evidence drawers and selectors transfer to V2. Reuse the Python modules for validated screens and whole-lot scenario arithmetic. Keep the archived V1 data builds available. |
| Used | Add `cash_flow.by_period` to the same company JSON. Each period keeps basis, typed source lines, evidence IDs, reconciliation residuals and separate provider comparisons. | Reconcile within the issuer's reporting perimeter. Mixing provider opening cash or adding a balancing plug would conceal disclosure gaps. Provider-only periods stay partial. |
| Used | Put the cash renderer in `site/assets/cash-flow.js` with `renderCashFlow(container, company, period)`. | Page 2 details can pass the same data and period and reuse the drawer. Extract the other Page 1 views as they mature. |
| Used | Select final PAT, retain owner and pre-associate facts, distinguish basic EPS from the proxy and restrict IGX nil-inventory inference to filed years. | The repaired arithmetic and approval scope carry through dashboard, evidence and screening. |
| Used | Build an indexed catalogue keyed by exchange plus ticker or a retained provider identity. Attach a minimal sourced record keyed by an exchange or security identifier. | User attachments retain their evidence URL in this browser and remain outside price-based analytics until reviewed. |
| Used | Gate comparison on business, period, basis and definition. Embed the same Page 1 along with its Python-derived data. | The operating-only IGX/IEX scope mapping admits compatible metrics and leaves cash and earnings basis differences visible. |
| Used | Derive evidence-linked claims from auditable rules. Fit whole lots and preserve a comparison with the baseline. | An ambiguous position or weak shortlist can return the diversified baseline. Repeatable source links support review from company detail and the comparison. |
| Used | Render history from the same reporting perimeter as the selected figure. Plot one quote as a point and leave incompatible periods as gaps. | Prevents an issuer restatement from being connected to a differently scoped provider series. |
| Used | Overlay locally added companies on the immutable built catalogue. Verify an NSE identity before admitting dated closes and validated annual rows. | Keeps lookup records durable and traceable without forcing a full base rebuild. Astral proved the first online addition and is available from the retained data afterward. |
| Used in V2.1 | Publish a sourced IPO milestone and four-question issuer case from Python. Prefer matching audited consolidated periods for Oravel. | Drafts prove stage and capitalization assumptions. The Oravel annual report provides full-year financials, including the FX effect and separate rounding discrepancy. Provider-only fallback withholds the superseded valuation. |
| Used in V2.1 | Persist ratio choices in the existing workspace and replace the separate peer page section with issuer-specific benchmark controls. | Aligned columns use Page 1 evidence. The app keeps contextual and incompatible facts individually visible. |
| Used in V2.1 | Keep the legacy Lab and use risk-based whole-unit sizing with a liquid overnight fund in the current workspace. | Zero default reserve avoids stranded cash when the dated evidence and constraints support deployment. Risk, observed history and illustrative returns remain distinct. |

## Prioritised to-do list

Dependencies refer to task IDs. Section numbers refer to the [V2 report](../report/IPO_Ready_V2_Report.md).

- [x] **V2-00 · Establish V1 baseline.** Launch the retained build, inspect all three V1 pages at both widths, reproduce both review findings, and record identifiers, commands and observed behaviour. Report §§2–3.
- [x] **V2-01 · IGX Cash Flow.** Reconcile the three restated periods in Python, publish versioned JSON, show the Page 1 tab with native links and working-capital, capex, lease and dividend detail, retain provider differences and partial states, and check desktop/mobile. Put the affected V1 metrics on hold. Report §§3, 5–8.
- [x] **V2-02 · Repair the V1 review findings.** Depends on V2-01. Recognise Polymatech's final PAT separately from pre-associate profit, owner-attributable profit and reported EPS. Disclose the chosen P/E basis and rerun 3.82×, 3.90× and 15× cases. Use period-bounded IGX inventory evidence from pages 5 and 54, distinguish assumed nil from zero, and show drawers and results for FY2026 and FY2022 on both widths. Verify consistent Python, JSON, comparison and screen outputs. Report §§3, 5, 7.
- [x] **V2-03 · Shared company model and sourced attachment.** Depends on V2-01. Normalize at least two listed and two unlisted examples plus a sourced sparse issuer outside V1's catalogue. Use verified identifiers and one evidence model across search, detail, queries and scenario eligibility. Test a duplicate alias, missing quote and conflicting basis. Report §§3–6.
- [x] **V2-04 · Page 1 statements, ratios and charts.** Depends on V2-02 and V2-03. Complete the linked P&L, Balance Sheet and Cash Flow views, including source-specific coverage. Make every current and new ratio selectable with six appropriate defaults or sector defaults, formula, inputs, history and peer reference where eligible. Correct P/S to operating revenue. Validate EPS types, invalid denominators, inventory and explicit zero, comparable FCF, and lender/insurer/exchange metrics. Keep cash versus profit and test at least one chart answering a cash or leverage question with sparse periods. Report §§3, 5–8.
- [x] **V2-05 · Comparison workspace and full detail.** Depends on V2-03. Implement ordered columns with company lookup and attachment, sector discovery, remove/reorder, compatible values and reasoned incompatibilities. Render full Page 1 company detail inside Page 2 using the same facts and renderers. Show listed-only, unlisted-only and mixed sets, including an out-of-list company and a sparse or incompatible example. Recheck expanded detail after V2-04. Report §§1, 4, 5, 7–8.
- [x] **V2-06 · Pros, cons, risk and horizon.** Depends on V2-03 and V2-05. Run deterministic rules and a bounded retrieval alternative against listed and unlisted cases with counterevidence. Show claim, date and location, interpretation and coverage. Exercise business, financial, valuation, liquidity and event risk. Separate verified restriction from review horizon, explain when three years is plausible, and test review triggers plus base/upside/downside or sensitivity. Report §§2, 5, 7–9.
- [x] **V2-07 · SQL-style query to shortlist.** Depends on V2-03 and V2-05. Extend the read-only grammar to documented mixed-instrument fields and explicit units, missing values and invalid input. Use query results to add a column, start a shortlist scenario or nominate an issuer. Check saved state across section switches, reload and data revision. Report §§4–5, 7–8.
- [x] **V2-08 · Budget-first selection and allocation.** Depends on V2-06 and V2-07. Exercise ₹10 lakh with configurable tolerance, horizon and liquidity constraints. Explain inclusions, exclusions, diversification, quantities, residual cash and a baseline. Compare a constrained whole-lot method with a simple template and demonstrate weak/unavailable evidence and a material input change. Report §§4–9.
- [x] **V2-09 · Requested-company scenario.** Depends on V2-08. Carry the requested ID and its price, lot and transfer evidence from search or comparison. Exercise both feasible and infeasible ₹10 lakh cases. Keep the requested name visible, quantify the alternative and compare removal under the same settings. Report §§4–9.
- [x] **V2-10 · Migration and offline recovery.** Depends on V2-07 and V2-09. Route old Portfolio Lab links, query parameters and saved inputs into Page 2 with working equivalents. Test a failed source, older capture and absent local data without losing company or scenario context. Document rebuild and migration. Report §§3–4, 6, 8.
- [x] **V2-11 · Walkthrough, independent review and repairs.** Depends on V2-02, V2-04 through V2-10. Cover the brief at both widths, including the required cash, ratio, claim, query and both allocation reproductions. Open `REVIEW.md` with ranked findings and limits, then fix or substantiate findings in a repair run. Verify every section and schematic against executed work. Report §§1–9.

### Owner steering follow-up

- [x] **V2-12 · Chart workspace and insight history.** Implemented revenue, growth and price defaults, checkbox options and scope-aware insight histories. JavaScript checks reproduced chart inputs for IGX and BSE. Combined browser verification is tracked in V2-16. Report §§5, 7–8.
- [x] **V2-13 · Fintech frontend and moving market strip.** The frontend specialist revised the theme and checked animation, pause, keyboard use, reduced motion and no page overflow at desktop and mobile widths. Report §§4, 8.
- [x] **V2-14 · Lookup workflow and source validation.** Public endpoints responded in a bounded probe. Verified the retained route, fixture ISIN search, duplicate handling and missing-source behavior. Full live acquisition is tracked in V2-16. Report §§3, 5–6.
- [x] **V2-15 · Add companies from the interface.** Published BSE and CDSL; wired NSE search and add into both pages. The Python/API tests exercise first add, duplicates, catalogue overlay, shared detail, query eligibility, and sparse state. Report §§4, 7–8.
- [x] **V2-16 · Verify the desktop demo and import a fresh online issuer.** Depends on V2-12 through V2-15. Ran the desktop walkthrough with chart history and retained lookup. Added Astral through the browser, verified three native capture hashes, and checked annual and price evidence, ISIN deduplication, comparison persistence and the dashboard handoff. Added the desktop horizontal scroll cue and tested eight columns and the capacity message for a ninth. Report §§3–5, 7–8.

### V2.1 owner steering

- [x] **V2-17 · Validate stage and capture cases.** Depends on V2-01 and V2-03. Verify IGX and Oravel at the cutoff, retain a primary annual and draft trail, and distinguish pre-IPO from generic unlisted, dealer terms and official terms. Report §§1, 3, 7.
- [x] **V2-18 · Publish issuer analytics and free-research audit.** Depends on V2-17. Work the four diligence questions for both issuers, evaluate alternative methods, onboard Lemon Tree context, compare three captured free pages and execute the notebook against the app build. Report §§2–3, 5–9.
- [x] **V2-19 · Integrate comparable rows and benchmarks.** Depends on V2-05 and V2-18. Verify aligned ratio values, persistence, scope and formula evidence. Retire the Page 2 peer section and migrate its old URLs. Report §§4–5, 7–8.
- [x] **V2-20 · Rework allocations and returns.** Depends on V2-08 and V2-09. Verify dated liquid-sleeve terms, deploy within risk and whole-unit constraints, split reserve and rounding cash, show horizon cases and dated holding history, and preserve missing-price and infeasible requests. Report §§2, 4–9.
- [x] **V2-21 · Verify integrated release.** Depends on V2-17 through V2-20. Run both page entry points, both allocation paths, the V1 repair regressions, source recovery and the two-issuer notebook. Inspect desktop and mobile artefacts and update the nine-section report and review. Report §§1–9.

## Coverage and follow-up

- **Financial coverage:** onboard further reviewed annual statements, especially issuer-reported lender, insurer and debt-service inputs. Covered sectors can still have unavailable metrics. Aether and user attachments demonstrate the identity-only flow.
- **Evidence and allocation:** stock prices, off-exchange lots and model shocks are dated prototype inputs. The actual executable prices, restrictions and transfer terms require verification. The two journeys and a mixed comparison are reproducible with retained inputs.
- **Open issuer questions:** look for official offer pricing and terms when a new filing appears. Review IGX's settlement availability and Oravel's same-store G6 contribution and debt service. Lemon Tree is a contextual, annuals-only record in the retained catalogue. The free-source audit is bounded to the checked pages. A wider allocation universe and comparable total returns would support testing a different optimisation method.

## Run and reproduce

The public GitHub checkout can serve the dated projection directly. The rebuild and source-level test suite use the native captures in the local research workspace. Source receipts and published projections travel with the checkout.

```powershell
python -m pip install -r requirements.txt
python -X utf8 -m ipo_ready.pipeline --offline
$env:IPO_READY_LOOKUP_OFFLINE='1'
python -X utf8 -m ipo_ready.server --port 8785
# In another terminal
python -X utf8 -m unittest discover -s tests -q
python -X utf8 scripts/check_workspace.py --base http://127.0.0.1:8785/ --output outputs/v21-release
python -X utf8 scripts/check_workspace.py --comparison-only --base http://127.0.0.1:8785/ --output outputs/v2.1-comparison
python -X utf8 scripts/check_site.py --base http://127.0.0.1:8785/ --output outputs/v21-release/regression
python -X utf8 -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_pre_ipo_cases.ipynb
```

- Page 1 cash flow at `/?company=igx&period=FY2026&statement=cash-flow`. Full V2 workspace at `/compare.html`. The legacy lab interface remains accessible at `/portfolio.html?legacy=1`.
- Active JSON at [site/data/current](../../site/data/current/manifest.json), V2.1 build [20261125T065438Z](../../site/data/builds/20261125T065438Z/manifest.json), prior steering build [20261124T180834Z](../../site/data/builds/20261124T180834Z/manifest.json), and V1 snapshot [20261123T191506Z](../../site/data/builds/20261123T191506Z/manifest.json). The working-tree V1 baseline was supplied over Git HEAD `7e5731fa635d8e28f8e6a92eb22bf5db7705454a`.
- [Two-issuer notebook](../../notebooks/02_pre_ipo_cases.ipynb) · [Oravel desktop](../../outputs/v2.1-comparison/issuer-oyo-desktop.png) · [Oravel and Lemon Tree mobile](../../outputs/v2.1-comparison/oyo-context-mobile.png) · [Budget-first desktop](../../outputs/v21-release/allocation-budget-desktop.png) · [Named IGX mobile](../../outputs/v21-release/allocation-requested-mobile.png) · [Release walkthrough](../../outputs/v21-release/workspace-checks.json).
- Restore the retained BSE and CDSL records with `python -X utf8 -m ipo_ready.lookup BSE CDSL --offline --history-sessions 3` and Astral with `python -X utf8 -m ipo_ready.lookup ASTRAL --offline`. Run the server with `IPO_READY_LOOKUP_OFFLINE=1` for the retained demo. Leave the variable unset to retrieve public data for an issuer without local captures. [BSE JSON](../../data/derived/company_lookup/nse-bse.json) · [CDSL JSON](../../data/derived/company_lookup/nse-cdsl.json) · [Astral JSON](../../data/derived/company_lookup/nse-astral.json)
- [Desktop dashboard](../../outputs/v2-steering/fintech-theme-dashboard-1440.png) · [Desktop walkthrough checks](../../outputs/v2-steering/desktop/workspace-checks.json) · [Astral first add](../../outputs/v2-steering/verified/lookup-astral-desktop.png) · [Astral browser checks](../../outputs/v2-steering/verified/lookup-astral-checks.json).
- [V1 handoff and captures](../../archive/v1-handoff-20261124/README.md), [IGX source and calculation note](../research/topics/igx-cash-flow.md), [session log](RUN_LOG.md), [report and playbook](../report/IPO_Ready_V2_Report.md).
- [Desktop cash-flow preview](../../outputs/v2-preview/cash-flow-desktop.png) · [Expanded detail](../../outputs/v2-preview/cash-flow-desktop-details.png).
- [Desktop mixed comparison](../../outputs/v2-steering/desktop/workspace-desktop.png) · [Budget-first scenario](../../outputs/v2-steering/desktop/allocation-budget-desktop.png) · [Requested-company scenario](../../outputs/v2-steering/desktop/allocation-requested-desktop.png) · [Release review](REVIEW.md).
