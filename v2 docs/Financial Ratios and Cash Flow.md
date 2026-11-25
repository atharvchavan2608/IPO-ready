# IPO-Ready Version 2 financial ratios and cash flow

24 November 2026

Make every ratio in the current and Version 2 catalogues available for display. On Page 1, show a short set of metrics by default, with a checkbox panel for adding or removing ratios on the main dashboard. Keep the three linked financial statements on the same page. Each displayed ratio should show the inputs and evidence investors need to interpret it and compare it with suitable peers.

## Current prototype

| Measure | Current formula | Where it is used |
| --- | --- | --- |
| Revenue growth (YoY) | Current operating revenue ÷ prior-year operating revenue − 1 | Dashboard and screener |
| Profit after tax (PAT) margin | PAT ÷ total income | Dashboard and screener |
| Net profit ratio | PAT ÷ operating revenue | Peer comparison |
| Other-income share | Other income ÷ total income. Peer comparisons also include separately disclosed other gains where available. | Dashboard and peer comparison |
| Current ratio | Current assets ÷ current liabilities | Dashboard and screener |
| Quick ratio | (Current assets − inventory) ÷ current liabilities | Dashboard and screener |
| Return on equity (ROE) | PAT ÷ average opening and closing equity | Dashboard and screener |
| Return on capital employed (ROCE) | (Profit before tax + finance costs) ÷ (total assets − current liabilities) | Dashboard and screener |
| Operating cash flow to profit | Operating cash flow ÷ PAT | Dashboard |
| Price-to-earnings (P/E) | Price ÷ earnings per share (EPS) | Dashboard, screener and peer comparison |
| Price-to-book (P/B) | Indicative market capitalisation ÷ total equity | Screener |
| Price-to-sales (P/S) | Indicative market capitalisation ÷ total income in the current calculation | Company data |

P/E on the dashboard and screener uses a calculated EPS proxy. The peer comparison uses reported annual EPS. The company data uses total income for the P/S denominator. Before exposing P/S in Version 2, use operating revenue for a sales-based multiple and label any legacy total-income value explicitly. Portfolio risk measures, including allocation weights, sector concentration, annualised volatility, drawdown and modelled stress loss, are tracked on Page 3. [Company calculations](../ipo_ready/company.py) · [Screener fields](../ipo_ready/screener.py) · [Prototype methodology](../archive/v1-handoff-20261124/docs/report/IPO_Ready_Report.md)

## Version 2 ratio catalogue

For a typical non-financial company, lead with **revenue growth, EBITDA margin, ROCE, operating cash flow to profit, net debt ÷ EBITDA, and indicative P/E**. Show the latest comparable year, a three-year trend and a peer reference where available. EBITDA margin and net debt ÷ EBITDA are the two new measures in this starting set. Use measures that fit the business model for lenders and insurers.

The **Choose ratios** panel lists the full catalogue by category. The default metrics start checked. Checking a ratio adds it to the main dashboard, and unchecking it removes it from the dashboard. If a selected ratio has missing inputs or does not apply to the selected company and period, show **Unavailable** or **Inapplicable** with the reason.

| Investor question | Proposed additions |
| --- | --- |
| Is profitability improving? | Gross margin, operating margin, EBITDA margin, return on assets (ROA) |
| Is growth reaching shareholders? | Three-year revenue CAGR and diluted EPS growth. Show reported basic EPS, diluted EPS and book value per share alongside them. |
| Can the company meet its obligations? | Cash ratio, debt-to-equity, interest coverage, net debt ÷ EBITDA and debt service coverage. Use disclosed scheduled principal and interest for debt service coverage. |
| How much cash does the business generate? | Operating cash flow margin, operating cash flow ÷ current liabilities and free cash flow margin. Use disclosed cash capex for free cash flow. |
| How efficiently does it use assets and working capital? | Asset turnover, fixed-asset turnover, inventory days, receivable days, payable days and cash conversion cycle. Label revenue or cost-of-sales proxies when used. |
| What does the price imply? | EV/EBITDA and EV/revenue where enterprise value inputs are supported, alongside existing P/E, P/B and P/S. |
| What has the company paid shareholders? | Dividend payout ratio, indicative dividend yield and dividend per share. Label special dividends. |

- **Lenders such as Hero FinCorp** — Net interest margin, gross and net NPA ratios, provision coverage and capital adequacy on the issuer's disclosed basis. [RBI glossary](https://m.rbi.org.in/scripts/Glossary.aspx)
- **General insurers such as SBI General** — Incurred claims ratio, combined ratio and solvency ratio. [SBI General financial disclosure](https://content.sbigeneral.in/uploads/51fd9860c2bf4f088cf5e5c6a93b74c4.pdf)
- **Exchanges such as IGX** — Other-income share, traded-volume growth and transaction fee income per unit traded where disclosures cover the same contracts and periods. Include settlement context when explaining operating cash flow. [IGX results and peer comparison](../archive/v1-handoff-20261124/docs/report/IPO_Ready_Report.md#7-analysis-resultsoutput)
- **Manufacturing, retail and inventory-heavy pharma** — Prioritise inventory days and the cash conversion cycle. [CFA Institute ratio list](https://www.cfainstitute.org/sites/default/files/-/media/documents/support/programs/cfa/cfa_program_level_ii_financial_ratio_list.pdf)

[Moneycontrol IEX ratio table](https://www.moneycontrol.com/financials/iex/consolidated-ratiosVI/IEE) · [Valuation definitions](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/definitions.html)

## Cash flow statement on Page 1

Put **Cash Flow** beside **Profit & Loss** and **Balance Sheet**. Show opening cash, operating, investing and financing cash flow, any other reported reconciling effects, net change and closing cash. Let investors expand the line items to see working capital, cash capex, debt and lease repayments, and dividends. Keep the Cash vs profit chart as a way to read the trend. The current build already has the chart and the three activity totals in the reported statements table. Its latest period contains all three totals for 19 of the 24 unlisted companies. [Current dashboard](../site/index.html) · [Company data](../site/data/current/company)

### Verified IGX example

IGX's restated filing supports FY2024 through FY2026 on the issuer-and-employee-trust basis. The FY2026 example below converts the original ₹ million figures to ₹ crore by dividing by ten.

| FY2026 line | ₹ crore |
| --- | ---: |
| Opening cash and cash equivalents | 13.217 |
| Operating cash flow | +156.685 |
| Investing cash flow | −153.535 |
| Financing cash flow | −12.410 |
| Net change in cash | −9.260 |
| Closing cash and cash equivalents | 3.957 |

The three activity totals sum to **−₹9.260 crore**, and opening cash plus the movement equals **₹3.957 crore**. Settlement accounts held **₹3.671 crore** of closing cash. The grouped payables and other liabilities line contributed **₹138.628 crore** of operating inflow, so that year's cash flow needs the working-capital explanation alongside it. The provider showed **₹156.89 crore** of operating cash flow. Use the issuer's **₹156.685 crore** for the restated view and make the provider difference visible. [IGX restated cash flow and notes, p. 7](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=7) · [IGX prototype reconciliation](../site/data/current/company/igx.json)

## Build priorities and acceptance checks

1. **Start with the IGX Cash Flow tab.** Render FY2024–FY2026 from Python-generated JSON and link each total to the original filing. Reconcile opening cash, reported movement and closing cash before displaying a complete reconciliation. For partial disclosures, show the available lines and mark missing rows **Unavailable**.
2. **Add the overview metrics and the Choose ratios panel.** Verify that Page 1 opens with only the default metrics checked, that every catalogue entry is listed in the panel, and that checking and unchecking a ratio updates the dashboard. Keep each value paired with its formula, inputs, unit, fiscal period and reporting basis. Preserve explicit zeros. Keep **Unavailable** and **Inapplicable** distinct, and explain unusable denominators. Verify that cash and capex figures use the same period and scope before computing free cash flow.
3. **Extend peer comparisons and screening.** Require compatible reporting periods, bases and definitions for peers. Use an indicative quote and its date for unlisted valuation. Show minimum lot, total purchase amount and verified transfer or exit terms beside the valuation. Surface a short, source-linked note on material debt maturities, dilution, related-party transactions and auditor observations where disclosed.

The current review records two issues to resolve before using the affected figures as Version 2 reference results. These concern the PAT row and P/E basis for Polymatech, and the period scope and source for IGX's nil-inventory quick-ratio assumption. [Independent review](../archive/v1-handoff-20261124/docs/starter-kit/REVIEW.md)
