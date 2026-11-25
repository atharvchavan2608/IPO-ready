# IGX restated cash-flow reconciliation

Checked 24 November 2026. [N13 source register](../sources/N13.md) · [Retained issuer capture](../../../data/captures/issuer/20261123T163845Z/manifest.json) · [Retained WWIPL capture](../../../data/captures/wwipl/20261123T164433Z/manifest.json)

## Source observations

The auditor's examination and board approval are dated 14 July 2026. Annexure III covers years ended 31 March 2024, 2025 and 2026 and uses the Ind AS 7 indirect method. The issuer includes the IGX ESOS employee share trust. The audit report identifies that perimeter and the notes explain the treatment of trust flows. Physical page 7 prints the periods newest first and amounts in ₹ million, with outflows in parentheses. The capture was retrieved 23 November 2026. Its SHA-256 is `d6fcbfb703f9a261511d0bbbd3a11b1b8e4426a89e6ac650f37c5c16c442ca8a`. [Auditor's report, physical p. 1](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=1) · [Annexure III, p. 7](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=7) · [Trust note, p. 55](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=55)

The issuer defines net movement as operating plus investing plus financing and closing cash as opening cash plus net movement. It shows no separate reconciling effect and no separately identified non-lease principal repayment in that statement. Lease principal and interest and overdraft/other interest have their own rows. FY2024 and FY2025 dividends are dashes in the filing. FY2026 shows a payment of ₹112.50 million. The data preserves the dash, absence and a numeric zero as distinct states. [Annexure III, p. 7](https://testwebcms.igxindia.com/files/financials-5bCIC136dXcpEa1daoEb.pdf#page=7)

WWIPL's IGX cash-flow summary has an unspecified reporting basis. Its FY2026 operating cash flow is ₹156.89 crore, compared with ₹1,566.85 million from the issuer. The oldest tab period, FY2022, has a blank financing cell. WWIPL's three activity lines alone cannot establish opening or closing statement cash. The retained provider page is dated by its 23 November 2026 capture. Its SHA-256 is `40a00d8792602d1301f4ecdd099dd7d5a5a2c1003e874f16e6ab3b788c46e3a9`. [Retained WWIPL financial snapshot](../../../data/captures/wwipl/20261123T164433Z/igx-financial.html)

## Executed calculations

Physical page 7 was rendered and checked against the `pypdf` extraction. The application preserves the original token and evidence location, converts with `Decimal` by dividing by ten, then tests activity and balance identities within the restated perimeter. Both residuals are zero at the disclosed precision in every year.

| ₹ crore | FY2024 | FY2025 | FY2026 |
| --- | ---: | ---: | ---: |
| Opening cash and equivalents | 18.736 | 15.464 | 13.217 |
| Operating cash flow | -189.819 | 3.287 | 156.685 |
| Investing cash flow | 187.572 | -4.366 | -153.535 |
| Financing cash flow | -1.025 | -1.168 | -12.410 |
| Net movement | -3.272 | -2.247 | -9.260 |
| Closing cash and equivalents | 15.464 | 13.217 | 3.957 |
| Closing cash in settlement accounts | 13.943 | 0.342 | 3.671 |
| Payables, provisions and other liabilities movement | -196.416 | -16.977 | 138.628 |
| Cash capex, as an outflow | -2.157 | -0.701 | -0.698 |
| Lease principal paid | -0.613 | -0.588 | -0.831 |
| Dividends paid | Dash | Dash | -11.250 |

The FY2026 operating difference is issuer minus provider = **−₹0.205 crore**. Differences for the other eight period/activity pairs are within ₹0.005 crore, the half-step at WWIPL's two-decimal display precision. The comparison is descriptive because WWIPL's perimeter is unspecified. [Generated IGX company data](../../../site/data/current/company/igx.json)

## Interpretation and next decision

FY2026 positive operating cash flow coincides with a ₹138.628 crore inflow on the grouped liability line and a lower closing cash balance. Settlement accounts held ₹3.671 crore of the ₹3.957 crore close. The grouping does not quantify how much of the liability movement came from settlement counterparties. Any later cash-quality or liquidity claim should use the balance and working-capital composition and assess the settlement terms before inferring discretionary cash.

The implemented route uses reported statement values and tests the identities. An alternative was a provider activity bridge with a balance-sheet plug. That approach fails on FY2022's blank financing amount and would also hide the FY2026 provider difference. Any broader cash-flow adapter should add same-perimeter source rows when verifiable. See [V2-04 and V2-06](../../starter-kit/WORKING_STATE.md#prioritised-to-do-list).
