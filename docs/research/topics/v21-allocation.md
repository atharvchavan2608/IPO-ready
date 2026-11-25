# V2.1 · Allocation and illustrative return method

## What changed

V2 set a fixed bond target even if the seven-year bond could not be purchased at the modeled horizon. In the ₹10 lakh, 36-month balanced baseline the V2 method left ₹3,53,922.60 at a zero reserve. V2.1 replaces that unused sleeve with an exchange-traded overnight money-market fund whose purchase lot, dated price, product terms and daily turnover are evidenced offline. A zero cash reserve is the default for new scenarios. An explicitly selected or previously saved reserve is still respected. [Liquid BeES sources](../sources/N26.md) · [RBI bond terms](../sources/N18.md)

SEBI's investor material gives the design criteria of horizon, risk tolerance and diversification. Markowitz's covariance method is the relevant quantitative alternative if all assets have comparable return histories. The pre-IPO dealer quotes lack a verified trade series, the fund's returns include reinvested distributions, and the equities have a short captured price sample. Estimating a common covariance matrix would either discard the requested pre-IPO company or invent its input. A continuous equal-weight trial over Liquid BeES, HDFC Bank, Gold BeES and MCX produced **21.14% modeled stress** (`(1 + 31.24 + 22.33 + 30) ÷ 4`), above the balanced 19% limit. The constrained approach below produced 15.66% and 99.98428% deployment in that baseline. Revisit covariance-based or integer optimization when there are sufficiently long aligned total-return series, executable trading constraints and a way to validate estimates out of sample. [Methods reviewed](../sources/N27.md)

## What Python does

1. Keep the explicit cash reserve. Verify a scenario-date close where the position is listed. Keep the requested company independent of the shortlist. Without a request, consider one candidate from the screened shortlist, preferring listed coverage, then lower modeled position stress, with shortlist order breaking ties. Verify the dealer price and lot for an off-exchange example and require a 36-month liquidity-planning window. The model checks a dated quote and indicative dealer lot, while legal transfer eligibility, execution and exit remain to be verified. Cap focus sleeves at 5%, 10% and 20% of budget under conservative, balanced and growth respectively, subject to lots and stress.
2. Size the remaining sleeves from their policy targets. HDFC Bank, Gold BeES and MCX targets are 20%/15%/5%, 22%/20%/13% and 28%/22%/20% respectively across the three profiles. Use half of risky targets up to 12 months, three quarters at 13–35 months and the full target from 36 months. A contractual seven-year bond enters at 84 months or longer, at up to 40%, 30% or 20% of the remaining sleeve. The portfolio exchange-industry cap is 25%, including an exchange focus. Do not duplicate a position in the same stock.
3. Apply a modeled 1%-of-daily-turnover limit when matching captured turnover is available. Measure stress with a scenario floor or a deeper observed price drawdown. The profile maximum losses are 13%, 19% and 25%. For an unlisted focus, the 35% price fall and 25% exit haircut on the remaining value imply 51.25% combined loss. Preserve 1% modeled stress for the liquid sleeve, then scale eligible risky targets down proportionally to fit. Quantize purchases to whole units or dealer lots.
4. Fill what remains with whole Liquid BeES units at the dated close, subject to turnover and stress capacity. Report purchased amount, explicit reserve and residual separately. A sub-unit remainder may remain. A missing quote or lot receipt, market participation cap or lack of stress headroom can leave more cash. The low-risk position is the largest risk band in the balanced ₹10 lakh cases. The growth case shifts more of the budget toward risk assets. The prototype models a small basket and concentration can remain within a risk sleeve.

[`allocation.py`](../../../ipo_ready/allocation.py) · [`portfolio.py`](../../../ipo_ready/portfolio.py) · [Portfolio instruments and histories](../../../site/data/current/portfolio.json)

## Return assumptions and historical observations

Downside, base and upside are annual scenario assumptions. They are not probabilistic forecasts or targets used to size holdings. The rates are deliberately sleeve-specific. Higher volatility supports a wider range of outcomes. It does not support a higher dependable rate.

| Sleeve | Downside / base / upside annual assumptions | Basis for reading the result |
| --- | --- | --- |
| Liquid BeES | 2% / 5% / 7% | Compare the separate reported 5.24% one-year fund return as at September 2025 and the overnight index's 5.24% one-year reading as at September 2026. Neither fixes future money-market rates. |
| Floating rate savings bond | 6% / dated coupon if available, otherwise 7% / 9% | The July–December 2026 coupon is 8.05% before tax. Model principal at par and sum simple coupon income without automatic reinvestment. The rate resets every six months. |
| Gold ETF | −15% / 5% / 15% | Funding diversifies asset exposure. Exchange prices can fluctuate and have tracking risk. |
| Medium-risk listed share | −20% / 8% / 20% | Demonstrates a loss as well as a favorable growth outcome. |
| High-volatility listed share | −30% / 10% / 30% | Treat 30% as a sensitivity. Recorded sample returns vary widely across the selected companies. |
| Unlisted share | −35% / 0% / 30% | The downside applies a single additional 25% exit haircut at the horizon. The base assumes a flat indicative price because the app has no demonstrated IPO profit or exit value. |

For a compounding sleeve with amount `A`, return rate `r` and horizon `h` months, ending value is `A × (1 + r)^(h/12)` with a separate exit multiplier where applicable. Bonds use `A × (1 + r × h/12)`. Sum paise-rounded holding values. Cash earns zero in the model. Annualized scenario return is `(ending ÷ budget)^(12/h) − 1`. The horizon downside is distinct from the single additive stress-loss calculation. Values exclude investor costs, taxes, inflation and dividend reinvestment for equity scenarios. The model holds the starting basket without rebalancing. Unlisted outcomes remain mark-to-assumption until sale. [Python calculation](../../../ipo_ready/scenario_returns.py)

The retained sample from 21 November 2025 to 20 November 2026 produced HDFC Bank **−15.23%**, Gold BeES **+0.21%**, MCX **+82.54%** and IEX **−19.82%** before distributions. IEX returned `(end close ÷ start close − 1) × 100`; the data include 49 observed weekly points and 44 adjacent returns. MCX uses the NSE-confirmed five-for-one split. Historical prices are the retained sample, not a comprehensive corporate-action history. Where less than 40 adjacent observations or unresolved corporate actions prevent a calculation, the UI marks history unavailable. The Liquid BeES issuer return is shown separately on its reinvested-IDCW basis. [NSE capture and split record](../sources/N20.md) · [Fund disclosure](../sources/N26.md)

## Executed cases using the 23 November snapshot

| Case | Observed outcome | Modeled downside / base / upside ending value |
| --- | --- | --- |
| ₹10 lakh, 36 months, balanced, no reserve, shortlisted IEX | 916 shares × ₹109.15 = ₹99,981.40. ₹9,99,425.50 deployed and ₹574.50 remains. Stress 17.10%. | ₹7,17,916.73 / ₹12,14,943.24 / ₹15,86,255.17 |
| Same settings, request IGX | ₹488 × 500 = ₹2,44,000 exceeds the ₹1 lakh company cap. The baseline deploys ₹9,99,842.80, including ₹4,51,000 in 451 Liquid BeES units. ₹157.20 remains, or 0.016% of budget. Stress 15.66%. | ₹7,58,395.60 / ₹12,02,412.73 / ₹15,20,115.88 |
| Same settings, request NCDEX | Three ₹25,300 lots fit. ₹9,99,675.85 deployed, ₹324.15 remains and stress is 18.32%. | ₹7,17,394.27 / ₹11,86,806.56 / ₹15,70,287.30 |
| ₹12.5 lakh, 36 months, growth, request IGX | 500 shares fit at ₹2,44,000. MCX falls to 19 shares, for ₹3,12,050.40 combined exchange exposure within the ₹3,12,500 cap. ₹378.05 remains. | ₹8,15,512.82 / ₹14,49,028.84 / ₹20,41,464.06 |
| ₹10 lakh, 12 months, balanced, request IGX | Horizon blocks the requested position. 725 Liquid BeES units in the baseline. ₹987.50 remains and stress falls to 8.31%. | ₹9,58,248.55 / ₹10,56,461.63 / ₹11,07,001.46 |
| ₹10 lakh, 36 months, balanced, 10% reserve, no focus | ₹1,00,000 remains by choice, ₹555.90 remains due to whole units. Stress 14.05%. | ₹7,83,604.51 / ₹11,81,849.40 / ₹14,66,577.43 |

Missing Liquid BeES source data replays with unspent cash and a coverage reason. A stale IEX quote stays out of the requested scenario. Weak shortlists retain the baseline. Focused tests exercise these branches, historical-return provenance, whole-lot rounding, forecast totals and preservation of the legacy Lab. [Focused checks](../../../tests/test_v2_workspace.py)
