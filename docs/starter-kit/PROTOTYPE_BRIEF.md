# IPO-Ready V2 prototype brief

Upgrade the runnable V1 into a research and decision workspace for Indian listed and unlisted investments. A retail investor should be able to start with a company or a budget, compare plausible alternatives, understand the evidence and risk, and see an illustrative allocation and next action. The CEO wants a fuller, more thoughtful prototype. The financial methods, data workflows and product design must work together.

[CEO notes](inputs/V2_CEO_NOTES.md) define the outcome. The [financial ratios and cash flow specification](../../v2%20docs/Financial%20Ratios%20and%20Cash%20Flow.md) defines the Page 1 catalogue, cash-flow priorities and acceptance checks. The [V1 baseline and review](../../archive/v1-handoff-20261124/README.md) supply reusable code, data and known gaps. The architect chooses the methods, interfaces, examples and scope of actual source coverage.

## Page 1 · Company research

- Deliver the full current and V2 ratio catalogues from the financial specification in a grouped **Choose ratios** panel. Open with a small, relevant default set. For a typical non-financial company that set includes revenue growth, EBITDA margin, ROCE, operating cash flow to profit, net debt to EBITDA and indicative P/E. Use business-appropriate measures for lenders, insurers, exchanges and other sectors.
- Make every catalogue entry selectable. Show the current value and useful history and peer context where supported. Expose formula, operands, unit, period, reporting basis and source. Carry the specification's distinctions for missing data, inapplicable ratios, invalid denominators, reported versus proxy EPS and the operating-revenue basis for P/S through to the dashboard and screener.
- Keep **Profit & Loss**, **Balance Sheet** and **Cash Flow** on Page 1. Cash Flow shows opening cash, operating, investing and financing flows, other reconciling effects, net change and closing cash. Expand disclosed working capital, cash capex, debt and lease repayments and dividends. Verify the reconciliation on the required IGX FY2024–FY2026 case with the restated filing and show issuer/provider differences. Partial disclosures retain their gaps.
- Add charts that answer investor questions. Keep cash versus profit and choose meaningful additions for questions such as what moved the cash balance, whether margins and cash generation are improving, or where leverage is building. Titles, periods, units and data gaps should make the graphs usable without explanation from the presenter. Build the data so the same sections can also be opened from Page 2.

## Page 2 · Comparison and investment workspace

### Add and compare companies

- Let the investor look up or attach any identifiable company or sector rather than requiring membership in V1's fixed peer lists. Support listed-only, unlisted-only and mixed sets, including across industries. Plan a way to add a company outside the starter universe from a verified lookup or minimal sourced record. Show what is available, including explicit coverage gaps for newly added or sparse companies.
- Display several selected companies in side-by-side columns with add, remove and reorder controls where useful. Lead with a few important comparable figures, risk and decision cues. Keep **all company data available on Page 1** reachable from the corresponding Page 2 card or column through an expandable detail view or panel. Reuse the same company, period and evidence rather than asking the user to change pages or relying on a separately maintained copy.
- Let the investor inspect any selection. Indicate where comparisons are meaningful by business model, reporting period, accounting basis, definition, units and currency. Mark incompatible metrics, explain the reason and show the individual values where available. Keep sector-specific risks and measures visible without forcing an overall cross-sector ranking.

### Pros, cons, risk and time horizon

- Implement a repeatable **pros and cons** workflow that can analyze an unlisted company as well as a listed one. Study how useful sites express strengths and weaknesses, then design an algorithm, evidence retrieval process or agentic workflow suitable for limited disclosures. Compare plausible approaches and implement one the investor can exercise in the suite.
- Generate company-specific points from sourced facts and explicit interpretations. Expose the evidence date, source location and why the observation matters. Consider operating trends, balance sheet, cash flow, valuation and issuer narratives when relevant. Show material counterevidence, conflict or sparse coverage. Distinguish a finding about the business from a concern about price, liquidity or the amount of evidence available.
- Show a short risk overview in each column and a fuller view on demand. Explain business, financial, valuation, liquidity and event risks as applicable. Provide a holding or review horizon and the reason for it. Treat the CEO's three-year example as a conditional scenario. State actual lockups or transfer restrictions separately from a modeled period to plan around. Give review triggers and the conditions that could shorten or extend the horizon.
- Show what could happen next through explicit assumptions and plausible base, upside and downside cases or an equivalent sensitivity view. State what evidence would change the conclusion and use indicative ranges or qualitative cases when the data cannot support precise estimates.

### Query, shortlist and allocate in one flow

- Keep the **SQL-style query** on Page 2. Support a bounded, validated, read-only query grammar over documented fields for listed, unlisted and mixed candidates. Explain filters, units, missing values and invalid input. Once results appear, let the user add a matching company to the comparison, start a portfolio from the shortlist or carry a selected company into an allocation. Keep the query, selected columns and allocation inputs coordinated as the user moves between sections.
- Integrate the portfolio controls and results into the same workspace. Use **₹10 lakh** as a walkthrough example and let the user change budget, tolerance, horizon and relevant liquidity constraints. Both entry paths must work end to end.
  - **No company in mind.** Guide the user from objectives and constraints through the available universe to a reasoned shortlist and diversified illustrative allocation. Explain the picks, exclusions, alternatives, cash and next diligence steps.
  - **Company already in mind.** Carry the selected company into the scenario and show what share of capital to consider in it and how to diversify the rest. Explain whether its quoted lot, price, liquidity and concentration fit the user's inputs. When a position is infeasible, show the reason and a workable alternative, rather than silently dropping the selected name or forcing a buy.
- Show amounts, weights, holdings or lots, residual cash, diversification and risk, and what changes with a material input adjustment or the removal of the selected company. Show a meaningful comparison with a baseline or alternative. Label prices, assumptions, shocks, horizons and quotes clearly. Use Python for calculations and keep model outputs reproducible as illustrative decisions.

## Shared workflow and release checks

- Evolve V1's repeatable Python source-to-JSON pipeline and caches to serve the same company model to Page 1, Page 2 details, queries and allocation inputs. Retain offline operation, evidence hashes, dated builds and honest fallback states. Keep company identity, source dates, reporting basis and units traceable across the end-to-end flow. Choose storage and cache changes based on what the upgrade requires.
- Reproduce the two open [V1 review findings](../../archive/v1-handoff-20261124/docs/starter-kit/REVIEW.md) early. Correct or explicitly withhold the affected Polymatech PAT/P/E and IGX quick-ratio results before using them as comparison, screen or recommendation inputs. Preserve the distinction between reported EPS and a calculated proxy, and scope any inventory inference to supporting evidence.
- The desktop walkthrough must demonstrate Page 1 statements, ratio selection and analytical charts, and both Page 2 entry paths. Exercise listed-only, unlisted-only and mixed comparisons. In the mixed case, show several columns across sectors, a company added from outside a fixed peer list, a sparse or incompatible case, the full company detail, an evidence-linked pros/cons result, risk and horizon, and a query result that reaches both comparison and allocation. Use real dated inputs where supported. Label fixtures, scenarios and unavailable data. [Owner steering](steering.md)
- Make Page 2 the destination for comparison and portfolio work. Consider existing V1 portfolio URLs, saved inputs and entry points during migration and document how to reach the equivalent V2 experience.

## Report and client playbook

Deliver the V2 prototype with a separate Markdown report and playbook. Keep these nine sections in order and use actually executed examples.

1. **Problem Statement** — whom the workspace serves and what investment research decisions it supports.
2. **Similar research already done in that area** — product and analytical precedents that changed an implementation or method decision.
3. **Data Sources, Data Quality, and Data Information** — sources, coverage, definitions, dates and known limitations for both listed and unlisted companies.
4. **Overall Approach to solve the problem** — how a company, query or budget leads to evidence, comparison and allocation.
5. **Detailed Analytics Methodology(ies)** — ratio eligibility, matching, pros/cons, query, risk, horizon and scenario and allocation methods, including relevant alternatives and edge cases.
6. **Using a schematic diagram, mention the Python libraries being used in different stages** — show the executed stages from input and evidence to the two pages, using the libraries and modules that actually run.
7. **Analysis results/Output** — reproducible results for the financial statement and ratio work, comparison cases and both allocation paths.
8. **Client playbook/interactive dashboard** — launch steps and walkthroughs from both starting points, including the implemented evidence workflow and options for extending it.
9. **Final Decision/strategy** — a concrete illustrative diligence or allocation decision, what would change it, and the next recommended product improvement.
