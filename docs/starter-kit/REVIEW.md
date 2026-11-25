# IPO-Ready V2 demo review

24 November 2026 · Offline build `20261124T133618Z` · Chromium/Edge at 1440 × 900 and 390 × 844. The build agent ran the client journeys in clean browser contexts and recomputed selected values from retained inputs. The review covers the local prototype and its dated examples.

## Verdict

Ready for an internal walkthrough with the dated IGX, IEX, MCX, Hero FinCorp and Aether cases. Both ₹10 lakh journeys reach a deterministic allocation or a visible reason to use the baseline. Even within the starter set, several sector ratios and some quote or transfer inputs remain unavailable.

## Findings and repairs

| Severity | Reproduction and observed result | Resolution |
| --- | --- | --- |
| High, V1 findings | Use default P/E under the CEO screen for Polymatech, or open IGX quick ratio for FY2022. V1 chose the pre-associate subtotal and applied the inventory assumption outside the retained balance sheet. | Published final PAT and separated EPS definitions. FY2026 quick ratio opens p. 5 and p. 54, and FY2022 shows unavailable. The 3.82×, 3.90× and 15× boundaries reproduced using the updated data. |
| Medium, repaired | Load the default CEO result on a 390 px viewport with the new Compare, Shortlist and Model actions. The first release candidate required horizontal scrolling for the three default metrics. | Adjusted narrow-screen column padding and placed EPS labels under values. The legacy browser check passes again. |
| Medium, repaired | Add or remove a shortlisted company after the retained-build status message was introduced. A status callback threw a JavaScript reference error after updating the selection. | Moved the fallback message to the catalogue load handler. The workspace test repeats shortlist actions and asserts no page errors. |
| Low, environment | Check the release on port 8765 in this workspace. A pre-existing Flask process occupied that port, and Windows accepted a second binding. The browser reached the older API, which returned 404 for the new endpoint. | Verified the release on port 8773. Documented the free-port launcher and preserved the pre-existing process. |

## Reproductions

| Check | Procedure and observed result |
| --- | --- |
| Cash, ratio and claim | Open IGX FY2026 Cash Flow. Sum ₹156.685 − ₹153.535 − ₹12.410 = −₹9.260 crore. Opening ₹13.217 crore plus the movement gives ₹3.957 crore. Select FCF margin and recompute (156.685 − 0.698) ÷ 61.005 × 100 = 255.6954%. The pros/cons claim links the ₹138.628 crore contribution to p. 7, and the settlement balance on the same page is ₹3.671 crore. |
| Incompatibility and sparse issuer | Compare IGX, IEX, Hero FinCorp and Aether. IGX and IEX qualify for standalone operating comparison. The IGX trust scope differs for CFO, and Hero's business model differs from both exchanges. Aether shows identity and absent numeric coverage. The IGX detail panel and column both show FY2026 CFO of ₹156.685 crore. Switch the detail to FY2025 and observe the period persist on the column. |
| Query and budget-first scenario | For mixed scope run **SELECT company FROM companies WHERE Revenue > 20**. It returns 21 matches, one definite non-match and five undecided. Shortlist IEX. At ₹10 lakh balanced with 36 months and 10% minimum cash, 916 whole shares × ₹109.15 gives ₹99,981.40. Cash is ₹3,82,276.80 and modeled stress is 17.60%, versus 16.42% for the baseline. |
| Requested position and alternative | Request IGX. The ₹488 quote × 500 shares = ₹2,44,000, exceeding the ₹1 lakh cap at the same budget. The baseline returns with ₹4,17,681.50 in cash. NCDEX fits three ₹25,300 lots under the same inputs. At ₹12.5 lakh and growth, IGX fits one lot. Reducing the horizon to 12 months blocks it. |
| Unavailable data and recovery | Request Aether or shortlist it alone. The result stays on the baseline. An injected V2 allocation HTTP 503 preserves both inputs and the previous result. Retry restores the computation. A Python case removes the active projection and confirms fallback to the matching retained release. Legacy URLs restore explicit company and amount and respect the saved horizon. |

Primary evidence includes the [IGX filing p. 7](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=7), the [IGX cash-flow and ratio research](../research/topics/igx-cash-flow.md), the [NSE closing price capture](../../data/captures/nse_eod/store/bhav_selected_23112026.csv) and the [active build](../../site/data/builds/20261124T133618Z/manifest.json).

## Review limits

The walkthrough uses retained issuer filings, provider records and market closes. Portfolio shocks and the injected outage are modeled inputs. Broad issuer acquisition, live prices, current execution terms, forecast validation and actual performance are outside these checks. Source-link and value coverage outside the named cases remains selective. Attachments are browser-local. The review used automated browser scenarios and source reproduction by the build agent.

## Desktop demo follow-up · V2-16

The desktop demo using build `20261124T180834Z` is ready for the rehearsed paths. Edge at 1440 × 900 passed seven groups, including multi-company comparison, both ₹10 lakh scenarios, source failure recovery and the eight-column limit. The overflow cue now appears when columns extend beyond the comparison viewport. [Desktop checks](../../outputs/v2-steering/desktop/workspace-checks.json) · [Four-company preview](../../outputs/v2-steering/desktop/workspace-desktop.png)

The first Astral add returned annual coverage and one dated close. The three native capture hashes verified. Replay the issuer from either page, open **Company detail**, and check revenue and quote evidence. Lookup by exact ISIN reuses the same company, and reload preserves the comparison column. A test initially assumed that no full NSE directory had been captured. Isolating that fallback test restored all 53 Python passes with the full directory present. [First add](../../outputs/v2-steering/verified/lookup-astral-desktop.png) · [Lookup replay](../../outputs/v2-steering/verified/lookup-astral-checks.json) · [Native sources](../research/sources/N21.md)

## V2.1 release review · 25 November 2026

**Verdict.** Ready for a local walkthrough of the two pre-IPO cases and the two ₹10 lakh journeys. Replayed from clean browser contexts at 1440 × 900 and 390 × 844. The comparison is keyboard-scrollable at 320 px with reduced motion. This was a build-team review and primary-source reproduction. Independent investment validation and live trade execution were outside the demo.

| Severity | Reproduction and observation | Disposition |
| --- | --- | --- |
| High, repaired | On the retained V2 dashboard, open OYO's current valuation. The old P/E was about 7.70× from group PAT and 3,745,994,357 pre-conversion shares. Draft p. 132 has 15,053,791,264 shares on assumed conversion, and audited p. 164 reports ₹0.68 basic EPS. | Show 30.07× basic EPS and label the ₹30,785 crore indication conditional on draft conversion. Suppress the old proxy and unsupported Oravel EV multiples. A missing annual source retains provider financial coverage and suppresses the old valuation. |
| High, repaired | Run ₹10 lakh balanced with 36 months and zero reserve against the preceding allocation policy. It leaves ₹3,53,922.60 in the budget-first baseline because the seven-year bond cannot fit. | Replay on V2.1. The listed overnight sleeve has a dated ₹1,000 unit and takes unused eligible capacity. Named IGX uses the baseline and leaves ₹157.20. With IEX shortlisted, ₹574.50 remains. A missing sleeve quote retains the amount and a reason. |
| Medium, repaired | Open comparison with IGX, IEX and a cross-sector company. V2 had a separate fixed peer section. Additional ratios were in the single-company detail. An early click on an embedded statement tab could also race loading. | The aligned chooser reads the shared catalogue, marks incompatible scopes, and preserves choices. Detail enables statement controls when ready. Tested legacy peer URLs, 8 columns and the ninth-column message. |
| Medium, source discrepancy retained | Open Oravel FY2025 Cash Flow. The activity sum is ₹268.953 crore and the statement says ₹268.954 crore. Opening, stated movement and FX total ₹685.722 crore versus ₹685.723 crore reported closing. The composition total on the page is ₹685.721 crore. | Display both −₹0.001 crore residuals and the separate composition difference, using the source figures. FY2026 reconciles exactly with separate FX of ₹52.043 crore. |
| Medium, open evidence limit | Request Oravel and inspect the ₹20.45 indication. No dealer lot is captured. Neither case had an official price band in the reviewed cut-off sources. | Position gate returns lot unavailable for Oravel and keeps the named company and alternative. Official terms or verified executable off-exchange terms would be needed to change the decision. |
| Low, recovered | Default Windows sandbox denied Chromium subprocess pipes and temporary-directory writes. First direct downloads were blocked by the proxy. An escalated INDmoney request returned 403 and one public NSE notice request timed out. | Normal permissions cleared test failures. Retried the NSE notice successfully and audited the captured Angel One IGX page alongside web-readable INDmoney context. |

### Reproduction results on build 20261125T065438Z

- **Cash, ratio and claim.** IGX FY2026 activities add to −₹9.260 crore. Adding this to ₹13.217 crore gives ₹3.957 crore. The FCF calculation gives 255.6954%, and the grouped liabilities claim links to p. 7 and ₹138.628 crore. Oravel's FY2026 activity subtotal is ₹269.769 crore. Opening ₹685.721 crore plus the subtotal and FX ₹52.043 crore yields ₹1,007.533 crore.
- **Comparison.** The OYO and IGX columns both have Pre-IPO stage evidence. The listed-only session shows IEX and Lemon Tree. The mixed session checks IGX, IEX, Hero FinCorp and sparse Aether. Lemon Tree has the same annual period as Oravel, and the fee-model benchmark remains context only. The IGX operating revenue and incompatible CFO checks show the same numbers as the dashboard.
- **Query and allocation.** Mixed revenue above ₹20 crore yields 25 matches, one definite non-match and five undecided; both verified stage badges appear in the results. The IEX shortlist produces 916 shares at ₹109.15 and ₹9,99,425.50 invested. In the separate named request, the ₹2,44,000 IGX lot breaches the ₹1 lakh balanced limit. The baseline invests ₹9,99,842.80 with ₹157.20 remaining. At ₹12.5 lakh growth the modeled lot fits. A 12-month horizon blocks it.
- **Recovery and later use.** Tests cover absent or stale inputs, a weak shortlist, an injected allocation 503 and retained JSON fallback. A focused comparison drill also served a 503 for IGX JSON, preserved its identity and restored the ratio chooser through the IEX record. Astral's offline lookup replay checked the captured NSE close, source drawers, ISIN deduplication and Page 1-to-Page 2 persistence.

All 58 Python tests, 122 legacy regression checks, 15 integrated walkthrough groups and 12 issuer comparison groups passed. The notebook executed all five Python cells. [Integrated walkthrough](../../outputs/v21-release/workspace-checks.json) · [Issuer and ratio checks](../../outputs/v2.1-comparison/workspace-checks.json) · [Legacy regression](../../outputs/v21-release/regression/check_results.json) · [Astral replay](../../outputs/v21-release/lookup-astral-checks.json) · [Notebook](../../notebooks/02_pre_ipo_cases.ipynb)
