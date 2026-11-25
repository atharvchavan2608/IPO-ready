# IPO-Ready prototype brief

An Indian-market investor should be able to open an unlisted company, understand the available financial picture, compare it with relevant companies and explore what an illustrative position would do to a portfolio. The product should feel like a credible finance site and be easy to demo. The startup founder should be able to react to a real screen early and change the design as the project develops.

The [CEO's original notes](inputs/Initial_design_thoughts.txt) supplied the product goals below. The owner confirmed that Pages 1, 2 and 3 are three required screens and set the nine numbered deliverables. Source availability, provider choices, sector and investment examples, and the choice of AI feature are open for the build lead to investigate and decide.

## CEO goals for the three pages

Deliver three distinct, directly navigable web pages with their own URLs and shared navigation. Opening the site lands on **Page 1**, with an unlisted company already selected. Keep unlisted companies at the center of the product. Listed peers, market context and other assets support that focus.

### Page 1 · Company dashboard and home page

- Show the selected unlisted company's financial trends and available reports. Let the investor change company or reporting period within the available coverage and open the supporting report or source from a figure.
- Show turnover or revenue, liquidity measures and the quick ratio where supported. Treat expected availability as a question to verify. Check explicitly for inventory and non-performing asset (NPA) figures at the individual-company level. Decide which fields apply to the business and whether targeted AI-assisted search can help find a missing disclosure. Show a plain-language gap when a suitable figure remains unavailable.
- Give the page the feel of an authentic finance site. Use side sections for recent news, selected stock prices, Nifty and Sensex, and small market charts. Use live charts if a reliable feed is feasible. Use clearly timestamped delayed or dated charts and quotes as the fallback, with visibly labelled demo values if needed. Show source and freshness.
- Give the side section a discovery area that suggests other unlisted companies or research leads and lets the user open one.

### Page 2 · Listed-peer comparison and unlisted screener

- Compare the selected unlisted company with relevant **listed peers** side by side. Use a business or sector hierarchy and explain why each example fits. The notes illustrate the desired depth with Commodities → Chemicals → Chemicals & Petrochemicals → Carbon Black.
- Show ratios on comparable bases where the data supports them and explain major drivers, differences and gaps in a short overview. Summarize the companies' disclosed future plans and relevant news articles where available, with links and dates.
- On the same page, let users run a database-style query on **unlisted companies** and compare the matching companies across the selected metrics. Show coverage gaps and useful feedback for an empty result. The CEO gave this Screener.in-style example:

```text
Market capitalization > 500 AND
Price to earning < 15 AND
Return on capital employed > 22%
```

Define units and comparison rules. Demonstrate a working compound filter. Use supported fields or a labelled demo dataset if real unlisted valuation inputs are too sparse for the example.

### Page 3 · Portfolio risk and diversification

- Let the user set an amount such as **₹5 lakh**, choose how much risk they are willing to take and select an unlisted stock to include in the scenario. Show how that position changes the portfolio and how spreading the amount across other investments affects concentration and risk.
- Include illustrative lower-risk and medium-risk choices, a metals exposure and a highly volatile exposure. The notes mention **RBI and HDFC** as examples to explore. Identify the specific underlying investment and its characteristics before assigning it to a risk band. Keep named instruments and weights flexible.
- Develop and run an explainable **Python risk and allocation algorithm**. Show the amount and allocation weight for each holding and the percentages in low, medium and high risk in a **pie chart**. Explain the risk assumptions and the effect of changing the amount, tolerance or mix. Account for the liquidity of the unlisted stock. Present the outputs as illustrative comparisons the user can explore.

## CEO goals across the prototype

- **Automate source-to-dashboard delivery.** Build a repeatable Python flow that gets data from a bounded source or retained capture, puts the inputs in a known location, maps and checks them, and writes dated or versioned JSON into the dashboard's data path. Have the pages read that output. Use labelled placeholders where data is missing, and exercise an offline rerun and a fallback when an input is unavailable.
- **Explore, implement and extend AI or agentic design.** Compare a few bounded possibilities, such as finding possible inventory or NPA disclosures in issuer documents, finding and summarizing dated company announcements and news, or using a sequence of tools to collect and check a missing field. Pick one and implement it as a runnable feature connected to a page or its pipeline. Show what actually ran, its source links and how the user can verify the result. Use a bounded local retrieval and evidence-review workflow if live model access is unavailable, and identify how a model could extend it. Keep financial calculations deterministic in Python. Give the founder a short list of additional options with their expected benefit and data or tooling needs.

## Source and design leads

- Draw on **Screener.in** for metric selection, financial tables and query-based screening. Examine **UnlistedZone** and **WWIPL** as named leads for unlisted data and as design references. Evaluate **Moneycontrol** for listed-company data and market context, including whether a suitable API or other access route exists. Treat the unofficial API question as a feasibility check and choose a working fallback based on access, coverage and reliability.
- The notes say “chattisgarh” in connection with expert write-ups. Use selected **Chittorgarh** analyst articles to learn how authors connect financial metrics, business drivers and risks. That identification follows the earlier research. [Expert-method note](../../../../docs/research/topics/expert-analysis-pipeline.md)
- Look at a relevant international site with both listed and unlisted data. Compare the metrics and presentation choices across the domestic and international examples. Capture the few lessons that influence what the prototype shows or how it works.
- Use the examples as design research and build a fresh visual identity. Decide which companies, peers, chart treatments, data providers, Python libraries and risk method will make the demo work. The prior implementation and its data are available for selective reuse after checking what each supports.

## Required deliverables

Deliver a runnable prototype and a Markdown report or playbook with these nine minimum sections in order. Connect each section to a specific method, result or interaction where it helps the reader follow the work.

1. **Problem Statement** — name the user, the decision they need to make and the information gap.
2. **Similar research already done in that area** — summarize the few studies or analytical precedents that shaped the work, and connect product references to concrete design decisions.
3. **Data Sources, Data Quality, and Data Information** — describe fields and coverage, evidence type, units, dates, quality checks, freshness and remaining gaps.
4. **Overall Approach to solve the problem** — explain the three-page user journey and how source inputs become dashboard outputs.
5. **Detailed Analytics Methodology(ies)** — document metrics, peer eligibility, screening semantics and the scenario risk and allocation logic, with formulas, assumptions and edge cases as appropriate.
6. **Using a schematic diagram, mention the Python libraries being used in different stages** — show ingestion, normalization, checks, analytics and delivery from input to UI. Label each stage with the actual Python standard-library modules or packages used and identify any separate presentation tools.
7. **Analysis results/Output** — show representative results from the executed pipeline and analytics. Include inputs, period or scenario, evidence and an interpretation.
8. **Client playbook/interactive dashboard** — give launch instructions and one guided walkthrough from the Page 1 home dashboard through the Page 2 comparison and screener to the Page 3 portfolio lab. Exercise the implemented AI or agentic feature in the walkthrough and give options for what to add next. Explain what the client can do with the outputs.
9. **Final Decision/strategy** — state a concrete next action for the demo case, such as shortlist for further diligence or pass on insufficient evidence, alongside the recommended product next step. Explain what would change each decision.
