# Proposal and Python proof-of-concept status

Updated: 2026-10-22. Latest user direction returns active work to initial planning and opens scope to foreign pre-IPO companies, prioritising free APIs. See [current plan](research/topics/pre-ipo-global-plan.md). Python analytics remains the academic core; product design is later work. The existing India-focused proposal, PDF and demo below are prior artifacts and have not been revised to the new scope.

## Ready to review

- [Recreated two-page proposal](proposal/IPO_Ready_Project_Proposal.md) and [PDF](../output/pdf/IPO_Ready_Project_Proposal.pdf). The prior extended text is retained as [working notes](proposal/IPO_Ready_Extended_Working_Notes.md).
- [Discussion and demo guide](proposal/Presentation_Guide.md).
- [Reference guide](proposal/Reference_Guide.md): how the eight proposal references inform the financial method, dashboard and document-processing design.
- [Self-contained offline demo](../outputs/poc/IPO_Ready_Demo.html): open directly in a browser; no server or API key required. Reports are precomputed by the Python engine, not calculated by Python inside the browser.
- [Python app instructions](../app/README.md) and [pandas notebook](../notebooks/01_financial_analysis.ipynb).
- [Annual profile CSV](../outputs/poc/aether_annual_profile.csv) and [all report outputs](../outputs/poc/all_reports.json).

## Implemented and verified

- Original engine uses the curated Aether historical pilot: 22 metrics and five periods. Period selection, monetary conversion, ratio calculation, four reconciliation checks, known review flags and a template explanation.
- Five Python regression tests pass, including all five periods, missing/zero denominators and CAGR elapsed-year handling.
- All notebook code cells executed successfully and produced the CSV. Notebook is saved with clean outputs for classroom execution.
- Offline browser smoke test passed with Chrome/Playwright: initial report, interim-period switch and 0.029x cash ratio, JSON download, no JavaScript errors and no page-level horizontal overflow at 390px. Downloaded JSON independently checked for period and ratio.
- Desktop/mobile screenshots inspected. The revised two-page proposal was rendered and both pages visually inspected. A numbered references section with publication details and links appears at the end, with matching in-text citations. AI assistance is a brief optional extension; Python analysis drives the proposal's milestones and evaluation.

## Important implementation limits

No live model or autonomous decisions, automatic extraction, peer valuation or overall score. Known issues are supplied from prior research; the app does not claim to discover them autonomously. The source pilot remains manually transcribed and not fully adjudicated.

The Python HTTP server starts, but this environment's localhost browser connection timed out. HTTP/browser end-to-end behaviour has not been verified. The tested offline bundle avoids that dependency for today's demonstration. Use `python scripts/build_demo_snapshot.py` to regenerate it from current Python calculations.

## Previous proposed build milestone — deferred

Confirm the course rubric, then prepare a second issuer with the same schema and pandas analysis. Gate: reproducible two-issuer output with a reviewed reference set and meaningful calculation tests. Next add bounded model-selected tool calls with genuine execution logs, failure handling and cost controls. Keep the existing deterministic baseline for comparison.

Investor audience is confirmed by the user and includes small individual investors through broker analysts. Other scope choices in the proposal are team-reviewable recommendations, not claims that the team already approved them.
