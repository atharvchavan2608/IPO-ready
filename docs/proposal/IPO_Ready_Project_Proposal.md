# IPO-Ready

> Scope update, 2026-10-22: this is the earlier India-focused proposal. The user has since opened foreign-company scope and requested initial planning around free data APIs. Use the [current planning note](../research/topics/pre-ipo-global-plan.md) for active scope. The existing PDF remains the earlier version; a revised proposal follows source and analytical feasibility work.

## Evidence-Based IPO Research

Programming Analytics Lab Project

Team members: Abdul, Ankit, Atharv, Kabeer, Sailaja, Utkarsh.

### Project idea and relevance

IPO-Ready is a proposed analytical application that helps investors examine the financial performance of Indian companies approaching an initial public offering. It will organise financial disclosures, calculate comparable indicators and present findings with links to the original evidence. The intended users range from individual investors investing small amounts to analysts working with brokers and investment firms.

IPO prospectuses and financial reports contain extensive information that can be difficult for investors to interpret and compare. Bringing this information into a common analytical framework can make financial research more accessible and systematic. The project will apply Python programming and financial analytics to transform company disclosures into useful comparisons and visual insights.

### Aim and proposed output

The aim is to develop a Python-based system that supports investors in understanding an IPO issuer's financial performance and comparing it with relevant companies.

The objectives are to organise financial data, analyse growth and financial strength, compare companies using relevant indicators, and communicate the results through visualisations and concise reports. The application will provide accessible explanations for individual investors and detailed financial information for analysts.

### Project scope and data sources

The project will focus on selected Indian IPO issuers and relevant listed companies. Publicly available prospectuses [8], annual reports, financial statements and stock-exchange disclosures will provide the data. The analysis will examine financial performance across reporting periods and compare companies within relevant industries. A web-based dashboard will present the results, supported by a reproducible Python notebook and analytical modules.

### Analytical approach

- Data collection and preparation: gather financial disclosures, extract relevant figures using document-processing tools such as Docling [7], and use pandas to structure and combine the data.
- Financial analysis: calculate revenue growth, CAGR, profit margins, leverage and cash-flow indicators to examine company performance and financial position.
- Peer comparison and valuation: compare companies using business characteristics and financial indicators, and develop valuation comparisons using relevant market multiples.
- Visualisation and interpretation: create trend charts, comparison tables and explanatory summaries, with references to the underlying financial information.

### Foundations of the project idea

Piotroski [1] informs the focus on accounting-based financial strength. IPO research [2] and Damodaran's valuation resources [3] guide peer comparisons and market multiples. FinQA [4] and TAT-QA [5] motivate traceable calculations and interpretation of tables alongside explanatory text. Screener [6] provides a practical reference for organising company financials, ratios, comparisons and source documents in an investor-facing dashboard.

---

## Implementation and Expected Outcomes

### Implementation plan and deliverables

The project will follow four development stages:

1. Data preparation: select companies and sources, define variables and structure the dataset.
2. Analytical development: implement calculations, exploratory analysis and company comparisons.
3. Application development: create the dashboard, visualisations and downloadable reports.
4. Testing and presentation: validate outputs, assess usability and document the project.

### Tools and technologies

Python, pandas and NumPy will support data processing; matplotlib or Plotly will support visualisation. A lightweight web framework will present the dashboard. AI-assisted features may support document search and explanatory summaries.

### Evaluation

Evaluation will examine data accuracy, calculation correctness, comparison consistency and presentation clarity. Selected outputs will be checked against original disclosures and manual calculations. Investor feedback will assess usability and understanding.

### Expected outcomes

Deliverables include a structured dataset, reusable Python modules, a reproducible notebook, an interactive dashboard and company reports, demonstrating programming analytics applied to financial decision support.

### References

[1] Piotroski, J. D. (2000). Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers. Journal of Accounting Research, 38 (Supplement), 1-41. https://doi.org/10.2307/2672906

[2] Purnanandam, A. K., & Swaminathan, B. (2004). Are IPOs Really Underpriced? Review of Financial Studies, 17(3), 811-848. https://doi.org/10.1093/rfs/hhg055

[3] Damodaran, A. (n.d.). Valuation: Supporting Materials and Relative Valuation Resources. NYU Stern School of Business. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valuation/val.htm

[4] Chen, Z., et al. (2021). FinQA: A Dataset of Numerical Reasoning over Financial Data. Proceedings of EMNLP 2021, 3697-3711. https://aclanthology.org/2021.emnlp-main.300/

[5] Zhu, F., et al. (2021). TAT-QA: A Question Answering Benchmark on a Hybrid of Tabular and Textual Content in Finance. Proceedings of ACL-IJCNLP 2021, 3277-3287. https://aclanthology.org/2021.acl-long.254/

[6] Screener.in. (n.d.). Aether Industries Ltd: Company Financials, Ratios and Documents. https://www.screener.in/company/AETHER/

[7] Docling Project. (n.d.). Docling: Document Conversion and Structured Extraction [Software repository]. GitHub. https://github.com/docling-project/docling

[8] Aether Industries Limited. (2022). Red Herring Prospectus, 16 May 2022. Securities and Exchange Board of India. https://www.sebi.gov.in/sebi_data/attachdocs/may-2022/1652869529567.pdf
