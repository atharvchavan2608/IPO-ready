# Professor discussion guide

## A short opening

Our project, IPO-Ready, begins as a Python programming analytics project. We analyse public Indian IPO disclosures to help investors understand financial trends and identify questions for further research. Python structures the data, calculates indicators, checks consistency and produces visualisations. An agent-assisted layer will coordinate those tools and investigate missing or conflicting evidence. The differentiating hypothesis is that investors benefit from explanations they can trace back to source documents; we still need to test that with users.

## Three-minute demonstration

1. Open the local app. Explain that Aether is a retrospective historical case, not a current IPO recommendation.
2. Select FY21. Show operating revenue, EBITDA margin, CFO/PAT and debt/equity. Explain that profits and cash can move differently.
3. Change to 9M Dec-2021 and run analysis. CFO/PAT changes to about 0.029x. The interim period is not annualised or inserted into the annual chart.
4. Open a source page from the analyst table. Show raw units and an original accounting definition.
5. Show the repeated-assets conflict and pending valuation inputs. The system retains uncertainty rather than concealing it in an overall score.
6. Expand the workflow trace. State explicitly that today's steps are deterministic Python, with live agent-selected tools planned for a later milestone.
7. Download JSON and show the pandas notebook if the professor asks about programming work.

## Questions likely to arise

- **Is this mostly a website?** No. The assessed core is the Python preparation and analysis pipeline, calculations, reproducible notebook and evaluation. The site is its demonstration interface.
- **Why use an agent?** To decide which evidence and analytical tool to request next, investigate discrepancies and prepare a cited explanation. Python remains responsible for calculations.
- **Does it recommend buying an IPO?** The first submission provides financial research and conditional comparisons. No validated return prediction or personalized investment recommendation is claimed.
- **What has actually been built?** A single-issuer curated-data prototype, period-aware calculations, checks, visualisation, evidence drill-down, review flags and exports. Automated extraction, live model routing and peer valuation are not yet implemented.
- **How is it evaluated?** A reviewed observation set, calculation regressions, source-citation checks, a separate extraction test case and bounded agent tasks compared with the deterministic baseline.
- **Why such a small sample?** It allows the team to demonstrate a complete, auditable pipeline within a course. It cannot support general predictive claims.

## Decisions to confirm with the professor

Course deadline and team size; required Python topics; whether AI/API use is permitted; whether a notebook is mandatory; expected dataset size; and whether the rubric prefers statistical modelling over a primarily descriptive, comparative analytics project. Adjust the proposed six-week sequence and stretch features accordingly.
