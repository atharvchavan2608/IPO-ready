# Portfolio instrument evidence and coverage

V2.1 adds Liquid BeES as an exchange-traded lower-risk sleeve and sizes it against the documented lot, retained closing price and daily turnover. The original portfolio Lab keeps its prior method. [V2.1 allocation method and results](v21-allocation.md) · [Fund and quote evidence](../sources/N26.md)

R1 reviewed exposure, observable price risk and evidence of exit access for the local demonstration. [Prototype brief](../../../archive/v1-handoff-20261124/docs/starter-kit/PROTOTYPE_BRIEF.md#page-3--portfolio-risk-and-diversification)

| Slot | Selected instrument | Evidence and rationale |
| --- | --- | --- |
| Lower credit risk | Government of India Floating Rate Savings Bonds 2020 (Taxable) | Seven-year, off-exchange sovereign instrument with a dated floating coupon. Its lockup needs separate treatment from credit risk. [N18](../sources/N18.md) |
| Medium demo risk | HDFC Bank equity (`HDFCBANK`) | Bank earnings and credit exposure. The retained weekly sample produced 25.04% annualized price volatility. [NSE observations](../sources/N20.md) |
| Metals | Nippon India ETF Gold BeES (`GOLDBEES`) | Domestic gold exposure through physical bullion, with tracking risk. The price sample produced 23.61% volatility. [N19](../sources/N19.md) |
| High observed volatility | Multi Commodity Exchange of India equity (`MCX`) | 37.02% on the same weekly dates after an NSE-confirmed five-for-one split. With IGX this adds exposure to exchange businesses. Hindalco, the first candidate, measured 24.04% on the same dates. [N20](../sources/N20.md) · [Hindalco capture](../../../data/captures/portfolio_terms/20261123T182731Z/manifest.json) |
| Unlisted | 24 off-exchange company choices, default IGX | The source supplies indicative quote and dealer lot where disclosed. IGX showed ₹488 and 500 shares at capture on 23 November 2026. The prototype has no verified traded series or execution evidence. [IGX evidence](../../../site/data/current/company/igx.json) |

The retained NSE sample has 49 shared weekly closes and 44 adjacent weekly returns across 21 November 2025 to 20 November 2026. Four intervening weeks are missing. Drawdown uses the retained closes, volatility skips pairs spanning a missing week, and current-week incomplete data is excluded. The 23 November closing quotes and one-day turnover are separate inputs. Turnover is limited evidence of order execution, spreads and depth. The risk bands are demo labels. [Inputs, dates and source URLs](../../../site/data/current/portfolio.json)

R2 models a 35% unlisted price shock followed by a 25% discount on the remaining value. These figures are illustrative assumptions. Whole lots, the risk-tolerance position limit and a 25% cap on combined exchange exposure determine whether the unlisted holding fits. The ₹5 lakh balanced case skips IGX and fits one NCDEX lot. A larger growth case fits IGX and reduces MCX under the shared cap. Verified transactions, transfer terms or a second dealer could change the assumptions. A shorter sovereign product and a broad volatile equity fund remain possible substitutions if their terms and comparable trading histories can be retained. [Model and executed scenarios](../../../archive/v1-handoff-20261124/docs/report/IPO_Ready_Report.md#executed-allocation-scenarios)
