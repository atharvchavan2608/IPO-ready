# IPO-Ready V2 report and client playbook

25 November 2026 · Local V2.1 prototype · Offline build 20261125T065438Z. The [working state](../starter-kit/WORKING_STATE.md) tracks acceptance and remaining coverage.

## 1. Problem Statement

An Indian retail investor researching a company before it lists needs understandable financial drivers, verified offering status, comparable facts and a path from diligence to an illustrative investment decision. V2.1 leads with Indian Gas Exchange (IGX) and Oravel Stays (OYO), using listed benchmarks where disclosures support comparison. The investor can start from a company, a screen or a budget and arrive at a sourced diligence decision or a portfolio scenario.

## 2. Similar research already done in that area

V1 demonstrated evidence drawers, narrow operating cohorts, a read-only screener and whole-lot allocation. A keyword search found 31 IGX liability references of varying meaning and zero at sparse Aether. Typed rules isolated the cash-flow movement and captured its settlement context. This informed the repeatable workflow of calculating, interpreting and linking evidence. Retrieval or a model can suggest additional passages for review. [Expert-method study](../research/topics/expert-analysis-pipeline.md) · [V1 review](../../archive/v1-handoff-20261124/docs/starter-kit/REVIEW.md)

A four-question audit against free coverage tested the research gap directly. Angel One already gives IGX operating figures and a peer table. The demo adds a volume/rate and settlement cash bridge with explicit scope checks. StopDown and Priveq already address Oravel's IPO stage, growth and valuation. Priveq also calculates FY2026 cash after selected obligations. The demo carries that sensitivity across both audited years, links it to the original cash reconciliation and uses the same data on both pages. The audit covers two issuers and three retained free pages. [Free-research audit](../research/topics/v21-pre-ipo-cases.md)

SEBI's investor guidance informed tolerance, horizon and diversification. A covariance model would need matched, reliable histories, including for dealer-quoted assets. A policy-sleeve approach uses dated holdings, whole units and explicit stress and return assumptions. [Allocation research](../research/topics/v21-allocation.md)

## 3. Data Sources, Data Quality, and Data Information

The 29-record base catalogue comprises 25 inherited company records, IEX, MCX, Aether and Lemon Tree Hotels. BSE, CDSL and Astral extend it to 32 through lookup. BSE and CDSL have standalone annual tables and three dated closes. Astral has FY2015–FY2026 standalone annuals and one close. Aether has verified identity and sparse financial coverage. User attachments retain their supplied identity source until financials can be reviewed. [Lookup evidence](../research/topics/company-lookup.md) · [Aether source](../research/sources/X11.md) · [Build manifest](../../site/data/builds/20261125T065438Z/manifest.json)

The 14 July IGX restated accounts cover the issuer and its employee share trust. Its three annual cash statements retain source units, labels, periods and reconciliation states. WWIPL carries an unspecified reporting basis and remains a separate observation. The IEX exchange notice confirms IGX received SEBI's draft observations on 12 October. Oravel's June updated draft and October addendum support its stage, and the audited consolidated FY2026 annual report provides matched FY2025 and FY2026 inputs. A compact PDF preserves the reviewed pages with the original digest and page map. The cutoff search did not find a final price band for either issuer. Lemon Tree's annual report provides statutory group values and contextual third-party fee information. [IGX cash source](../research/topics/igx-cash-flow.md) · [IGX stage](../research/sources/N22.md) · [Oravel sources](../research/sources/N23.md) · [Lemon Tree evidence](../research/sources/N24.md)

Unlisted prices are dated dealer indications. Listed prices come from retained NSE closes. Loan, lease, regulatory, source coverage and corporate action differences constrain interpretation. Polymatech's FY2025 final and owner-attributable PAT and reported EPS remain separate from its pre-associate subtotal and calculated PAT/share proxy. [Review repairs](../research/topics/v2-review-repairs.md) · [Instrument terms and retained closes](../research/topics/portfolio-instruments.md)

## 4. Overall Approach to solve the problem

Page 1 presents the source-backed IPO stage and four research questions above selectable statements, ratios and charts. Page 2 aligns figures across ordered company columns and opens the same Page 1 inline. Its ratio chooser uses the same catalogue. Reviewed benchmarks appear inside comparison with their scope visible. The workspace stores order, period, statements, ratios, query, shortlist, request and scenario inputs in the same browser. A legacy peer link leads to the workspace.

In the budget-first path, the investor sets tolerance, horizon and optional cash reserve, runs a read-only screen and shortlists candidates. In the company-first path, the request persists through the sizing and eligibility checks. Both paths see the budget ledger, a baseline, risk and separate return cases. Earlier Portfolio Lab links preserve explicit company and amount. The legacy Lab remains available for the baseline walkthrough.

## 5. Detailed Analytics Methodology(ies)

- **Statements and ratios.** Use Decimal to reconcile activities and balances. Keep missing, disclosed dash, explicit zero and conflict distinct. The 50 selectors share formula, operands, unit, source and scope. FCF adds signed cash capex to matching CFO. P/S uses operating revenue. Positive denominator checks prevent misleading multiples. P/E prefers reported basic EPS where available and retains distinct query fields for earnings definitions.
- **Comparison and claims.** Require aligned business model, period, basis, unit and definition. IEX provides IGX with matching annual operating revenue and growth context. PAT-based ratios, cash flows and P/E remain individual where bases differ. MCX and Lemon Tree provide contextual figures. Deterministic claims link to source records and limitations. A three-year unlisted window is an illiquidity assumption. Revisit at material filings, changes in executable quotes and changes to transfer terms. A ±10% revenue sensitivity illustrates operating exposure. [Comparison research](../research/topics/v21-pre-ipo-cases.md)
- **Issuer methods.** A fixed-prior-rate bridge attributes IGX fee growth to volume and the remaining change to fee rate and mix. Remove one disclosed group from CFO to test sensitivity to working-capital timing. For Oravel, attribute the change in bookings to G6 and reconcile consolidated CFO through cash capex, borrowing interest and lease payments. Use annual basic EPS at the dated dealer quote. Oravel's conditional equity value uses draft preference conversion. Headline revenue, CFO/PAT and broad group multiples provide context and omit several of these effects. Cash conversion, organic growth and peer definitions need primary evidence specific to each model. [Cases and alternatives](../research/topics/v21-pre-ipo-cases.md)
- **Query and lookup.** Python validates the read-only grammar, numeric filters, AND and OR, and optional SELECT company FROM companies WHERE clause. Missing inputs can make a result undecided. A decisive failed predicate excludes the company from its AND group. NSE lookup validates identity, keeps dated source receipts and uses the shared company schema. Sparse identities preserve their field gaps. [Lookup method](../research/topics/company-lookup.md)
- **Allocation and scenarios.** New scenarios default to zero cash reserve. The engine sizes one eligible focus and balances it against listed-equity, gold and low-risk sleeves. It applies concentration, whole-unit, liquidity and stress constraints and fills remaining capacity with dated Liquid BeES units when the seven-year RBI bond does not fit. Keep the selected reserve and quantify any whole-unit or capacity residual. A balanced equal split of the four baseline sleeves would give 21.14% modeled stress above the 19% cap. The executed baseline gives 15.66%. Return cases compound explicit holding assumptions at the chosen horizon and show observed price-only or fund history separately. Cash earns zero in the calculation. Fees, taxes and future execution are outside the scenario arithmetic. [Portfolio model and alternatives](../research/topics/v21-allocation.md)

## 6. Using a schematic diagram, mention the Python libraries being used in different stages

~~~mermaid
flowchart LR
  A["Issuer PDFs, provider HTML and NSE price CSV"] --> B["hashlib and pypdf verify and read PDF evidence"]
  A --> C["BeautifulSoup and lxml inspect HTML; csv reads closes"]
  B --> D["re reads IGX statement and activity lines; reviewed Oravel and Lemon Tree rows retain physical page coordinates"]
  C --> E["decimal computes matched facts, ratios, reconciliation and findings"]
  D --> E
  E --> F["json writes dated build and active projection"]
  F --> G["Flask serves Page 1 and Page 2 company detail"]
  F --> H["Flask exposes screens and scenarios"]
  H --> I["re validates predicates; decimal evaluates and sizes lots and values horizon cases"]
  I --> J["Page 2 query, shortlist and portfolio"]
  G --> J
  E --> K["Jupyter and nbconvert reproduce the issuer cases"]
~~~

Requests captures public inputs. Playwright exercised the local app on desktop and mobile. Flask can serve the matching retained projection when an active JSON is unavailable. [Run log](../starter-kit/RUN_LOG.md)

## 7. Analysis results/Output

| IGX, ₹ crore | Opening | Operating | Investing | Financing | Net movement | Closing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FY2024 | 18.736 | −189.819 | 187.572 | −1.025 | −3.272 | 15.464 |
| FY2025 | 15.464 | 3.287 | −4.366 | −1.168 | −2.247 | 13.217 |
| FY2026 | 13.217 | 156.685 | −153.535 | −12.410 | −9.260 | 3.957 |

All six IGX residuals are zero. FY2026 FCF margin is (156.685 − 0.698) ÷ 61.005 × 100 = **255.6954%**. Removing the ₹138.628 crore grouped liability contribution leaves ₹18.057 crore. Settlement accounts held ₹3.671 crore. Gas volume grew 27.94%. Nearly all of the ₹12.567 crore fee increase came from volume at the prior rate. The ₹488 indication at ₹5.68 basic EPS gives **85.92×**. The 75 million draft shares imply ₹3,660 crore. The quick ratio is 1.5137× for FY2026 with inventory assumed nil and unavailable in FY2022. [IGX financial evidence](../research/topics/igx-cash-flow.md) · [Draft and stage](../research/sources/N22.md)

Oravel's FY2026 revenue rose **49.66%**. G6 contributed **73.44%** of incremental gross bookings. ₹2,511.210 crore operating cash falls to **₹408.465 crore** after cash capex, borrowing interest and lease payments, versus −₹1,038.572 crore in FY2025. Reported FY2026 closing cash is ₹1,007.533 crore including ₹52.043 crore of separate FX effects. FY2025 shows two −₹0.001 crore bridge residuals and a separate ₹0.002 crore cash composition discrepancy. The ₹20.45 dealer indication implies **30.07×** basic EPS and about **₹30,785 crore** on draft converted shares. Reported PAT includes a ₹595.251 crore tax credit. [Oravel audited and draft evidence](../research/sources/N23.md) · [Executed notebook](../../notebooks/02_pre_ipo_cases.ipynb)

Lemon Tree's ₹73.9 crore third-party management and franchise fees provide context. Its owned and leased inventory of rooms and Oravel's global booking and acquisition mix limit group comparison. Astral retains its dated ₹1,225 close and ₹5,908 crore standalone FY2026 revenue in the mixed workspace. Polymatech's reported EPS P/E is 3.9691× and the proxy is 3.8190×. At default P/E the 3.82× and 3.90× thresholds exclude it, and 15× includes it. The explicit proxy passes 3.82×. The mixed revenue-above-₹20-crore query returns **25 matches**, one definite non-match and five undecided across 31 evaluated records. [Lemon Tree evidence](../research/sources/N24.md) · [Astral sources](../research/sources/N21.md) · [Review repairs](../research/topics/v2-review-repairs.md)

| Executed scenario | Focus and amount invested | Cash remaining | Modeled stress loss | 36-month base value |
| --- | --- | ---: | ---: | ---: |
| ₹10 lakh, balanced, zero reserve, shortlisted IEX | 916 shares at ₹109.15. ₹9,99,425.50 invested. | ₹574.50 | 17.10% | ₹12,14,943.24 |
| Same settings, IGX requested | ₹2,44,000 lot exceeds ₹1 lakh cap. Alternative invests ₹9,99,842.80. | ₹157.20 | 15.66% | ₹12,02,412.73 |
| Same settings, NCDEX requested | Three ₹25,300 indicative lots fit. ₹9,99,675.85 invested. | ₹324.15 | 18.32% | ₹11,86,806.56 |
| ₹12.5 lakh, growth, zero reserve, IGX requested | One 500-share lot at ₹488. ₹12,49,621.95 invested. | ₹378.05 | 22.97% | ₹14,49,028.84 |

A 12-month horizon blocks the IGX lot. Oravel stays named with its dated quote and an unavailable lot. Aether remains named with unavailable inputs. A shortlist containing only Aether uses the baseline. IEX's 21 November 2025–20 November 2026 retained sample returned −19.82% before distributions. The same holding has separate forward scenario assumptions. [Allocation method and evidence](../research/topics/v21-allocation.md) · [Verification](../starter-kit/REVIEW.md)

## 8. Client playbook/interactive dashboard

~~~powershell
python -m pip install -r requirements.txt
$env:IPO_READY_LOOKUP_OFFLINE='1'
python -X utf8 -m ipo_ready.server --port 8785
~~~

Start with the published snapshot. To regenerate it in the research workspace, run `python -X utf8 -m ipo_ready.pipeline --offline` with the matching native captures. The public checkout includes their receipts and original source references.

1. Open the [local dashboard](http://127.0.0.1:8785/). Select **IGX** in **Pre-IPO · verified filings**, click the stage badge and read the four research answers. Open **Cash Flow**, select FY2026, click **156.685** and inspect Working capital and the WWIPL comparison. Select Free cash flow margin in **Choose ratios** and inspect the formula and operands.
2. Select **OYO** and verify FY2026 **Cash Flow** includes FX. Open the growth and valuation sources. Switch to FY2025 to see the disclosed cash bridge discrepancy. Review **Choose charts** and select the company history for a sourced annual comparison.
3. Select **Compare this company** for IGX. Add IEX from the issuer's benchmark panel, then Aether and Hero FinCorp from **Find a company or sector**. Open **Choose ratios** and select revenue growth and Free cash flow margin. Compare the aligned figures and explanations. Open **Company detail** for IGX, change the reporting period and see it follow back to the column. Restore FY2026 and open **Pros, cons and risk**. Follow the ₹138.628 crore claim to p. 7.
4. Open OYO on Page 2 and add Lemon Tree through the issuer's benchmark panel. Read the group mismatch beside both figures. Open Lemon Tree's **Company detail** for the fee evidence. Scroll horizontally as needed. The comparison accepts up to eight companies.
5. For budget-first, choose **Listed and unlisted** and run **SELECT company FROM companies WHERE Revenue > 20**. Add IEX to the comparison and shortlist. Calculate at ₹10 lakh balanced with 36 months and zero cash reserve. Inspect modeled values, dated history, the alternative without IEX and the exact cash remainder. Enter a 10% reserve to see it kept separately.
6. For company-first, click **Model holding** for IGX. Compare the ₹2.44 lakh lot to the cap in the ₹10 lakh result. Raise the budget to ₹12.5 lakh and choose growth to fit one lot, then reduce the horizon to 12 months to test the liquidity assumption.
7. For lookup and migration, search **ASTRAL** or **INE006I01046** through **Look up on NSE**. A fresh record needs available public sources. The retained demo restores Astral and its evidence. The legacy URL **/portfolio.html?company=igx&amount=1250000&tolerance=growth** opens Page 2. **/portfolio.html?legacy=1** opens the legacy Lab.
8. Execute the [two-issuer notebook](../../notebooks/02_pre_ipo_cases.ipynb) in Jupyter against the published or rebuilt snapshot.

~~~powershell
python -X utf8 -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_pre_ipo_cases.ipynb
~~~

## 9. Final Decision/strategy

Keep IGX in diligence and use the diversified illustration at ₹10 lakh balanced. One IGX lot exceeds the position cap. The alternative holds ₹4,51,000 in the liquid sleeve and retains ₹157.20 after whole-unit sizing. A verified smaller lot or changed price could alter feasibility. Check recurrence of grouped liabilities and the availability of settlement cash before interpreting FY2026 CFO as sustainable.

For Oravel, review debt and lease commitments, official offer pricing and converted capitalization before modeling a position. Use the audited cash bridge alongside tax-sensitive earnings. Extend the same issuer workflow when another candidate provides repeatable primary evidence and an economically relevant benchmark.
