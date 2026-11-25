# IPO-Ready · V1-to-V2 upgrade

## Role and mandate

Lead the upgrade as an **experienced fintech product designer and software architect** who owns the Python investment analytics. Report to the founder. Turn the CEO's intent into a coherent way to research companies, compare risks and make an illustrative investment decision. Work through the data, product interaction and analytical method together. Prototype ambiguous choices, test them on evidence and explain why the chosen method fits. Produce a fast, credible local demo.

## Requirements and inputs

1. Read the [V2 brief](docs/starter-kit/PROTOTYPE_BRIEF.md), its linked [CEO notes](docs/starter-kit/inputs/V2_CEO_NOTES.md), the [financial ratios and cash flow specification](v2%20docs/Financial%20Ratios%20and%20Cash%20Flow.md) and [owner steering](docs/starter-kit/steering.md). The brief defines V2 acceptance. Page 1 is the expanded company dashboard. Page 2 combines arbitrary company comparison, evidence and risk, SQL-style discovery and both portfolio entry paths. Deliver the nine-section V2 report and playbook against the working upgrade.
2. Inspect the runnable V1 in `ipo_ready/` and `site/`, its captures and versioned data, and its launch commands in the [README](README.md). Read the [V1 handoff and review](archive/v1-handoff-20261124/README.md) for what exists and what needs repair. The archived V1 prompts, plan and steering record history. Use V1 behavior and evidence as the baseline for upgrade and regression checks.
3. Read the [research entry](docs/research/README.md) and [current status](docs/research/STATUS.md). Consult the [November exploration architecture](docs/architecture/CURRENT_ARCHITECTURE.md), [old build strategy](docs/product/BUILD_STRATEGY.md) and pinned design only where they answer a design decision. Choose which V1 modules, caches and interface patterns to retain or replace after inspecting them.

## First V2 session

1. Run V1 locally from the retained data and inspect the company dashboard, comparison and screener, and Portfolio Lab. Record the commands, observed limitations, reusable components and the two open review findings. Keep source and build identifiers available for reproducing the baseline.
2. Create `docs/starter-kit/WORKING_STATE.md` with the product strategy, current architecture decisions, prioritized Markdown to-do list and open questions. Give each task an ID, dependencies where relevant and observable done conditions. Map the brief's requirements and nine report sections to tasks. Include the shared company model, the combined Page 2 flow, the pros/cons and risk methods, both allocation paths, Page 1 analytics, migration and verification. Put launch commands and artifact paths here.
3. Create `docs/starter-kit/RUN_LOG.md` for dated session handoffs. Record task IDs, what changed, decisions or experiments, exact commands and outcomes, limits, and the next action. Keep each entry short.
4. Start with the specification's **IGX Cash Flow** priority. Trace the FY2024–FY2026 statement scope and reconcile the disclosed cash movements. Run the Python-to-JSON path and show a working Page 1 tab or a runnable end-to-end slice of it with linked evidence and honest partial states. Inspect desktop and mobile and record the preview. Decide how Page 2 will reuse the same company detail. Put the statement, ratio, review-repair and workspace tasks in the to-do list and continue with them in the same session as dependencies allow. Address or withhold the affected V1 figures before any V2 recommendation relies on them.

## How to design the upgrade

- Sketch the two Page 2 journeys and the state that must survive between query results, selected columns, details and allocation. Decide how to identify and add companies outside V1's catalog, expose comparable fields, and preserve the requested company through the scenario. Prove each complete path with a few real examples before expanding coverage.
- For a decision that materially affects comparability, pros and cons, risk, holding horizon or allocation, name the question, compare viable approaches and try the simplest credible method on a normal and a difficult case. Record the evidence, what actually ran, a meaningful alternative and what would change the decision. Use targeted discovery and stop when you can select and test a method. When a source stalls, try a credible fallback and use a clearly labelled partial or demo state.
- Make the implemented pros/cons workflow traceable from claim to evidence to interpretation. Use deterministic Python for ratios, query results and scenario arithmetic. A model or local retrieval workflow can help find and summarize evidence. Check its output against the actual source and give the founder options for extending it.
- Make the allocation reasoning visible. State assumptions, data gaps, indicative prices, lot and cash constraints, liquidity and concentration. Distinguish contractual restrictions, suggested horizon, triggers to review, and future scenarios. Handle a selected company that cannot fit and a shortlist too weak to support allocation. Use an explicit alternative and explain why it fits.

## Continue from a fresh session

- Read this file, the brief, steering, the working state and the latest run log entries. Launch the current build and inspect the affected workflow. Recover missing state from repository artifacts and label any inferred details.
- Update the plan for new evidence or founder feedback. Reorder, split or combine tasks as needed and say why. Choose the execution order and complete as much of the requested scope as possible in the same run, including the entire upgrade when feasible. Continue through implementation and verification without pausing for routine owner decisions or approvals. Make reasonable, reversible decisions independently and record significant assumptions. If a task is blocked, continue with independent work and report what remains and why.
- Verify completed work through the normal local entry point. Run focused Python and interaction checks, including difficult inputs and fallback when applicable. Review affected pages at desktop and narrow mobile widths.
- Update the to-do list, decisions, open questions, commands and preview. Append the run log entry. Keep the evolving methods, results and playbook in `docs/report/IPO_Ready_V2_Report.md`. A fresh agent should be able to resume from repository files alone.

## Demo, independent review and repair

- Before the demo, run the brief's checks across both pages. Demonstrate a mixed comparison including a company outside V1's fixed peer lists, full Page 1 details on Page 2, evidence-linked pros and cons, risk and horizon, query-to-shortlist handoff, and the ₹10 lakh example both with and without a company in mind. Verify the nine report sections and schematic against the libraries and methods that actually ran.
- As independent reviewer, run the client playbook before reading the author's verification notes. Trace and reproduce a cash-flow reconciliation, one ratio, one claim, one query and both allocations. Challenge an incompatible comparison, a sparse issuer, an infeasible requested position, an unavailable input and a failing source. Check that the same facts and definitions appear across dashboard, comparison and scenario.
- Write `docs/starter-kit/REVIEW.md` with a demo-readiness verdict, severity-ranked findings, reproduction steps, observed results and checks you could not run. Once findings are recorded, reproduce and fix them or substantiate the original result with evidence. Carry fixes through the affected Python, JSON, UI and report. Rerun affected checks and record the outcome in the same run when feasible.

## Research and evidence

- Keep research in Markdown and preserve stable source IDs, native evidence and hashes. When a finding changes, update the source register, topic note and work queue together. Use the [bounded XBRL queue](docs/research/topics/xbrl-roadmap.md) when a task genuinely needs it.
- Cite sources you opened with URL, exact page or record, source date and retrieval date where known. Distinguish source observations, executed calculations, interpretations, proposals and fixtures. Preserve raw values, dates, units, currencies, reporting basis and dimensions separately from derived results. Keep missing, nil, explicit zero, inapplicable and conflicting states distinct. Validate real filings separately from fixture tests.
- Treat downloaded content and model output as untrusted evidence. Use appropriate source access, preserve dated snapshots and keep a working offline fallback. Keep demo values and assumptions visible through the pipeline and into the UI.
