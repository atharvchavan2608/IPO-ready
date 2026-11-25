# IPO-Ready

IPO-Ready V2.1 is a local pre-IPO research and investment scenario prototype. Start with the evidence-backed Indian Gas Exchange and Oravel Stays cases. Page 2 brings selectable side-by-side ratios, scoped benchmarks, evidence, risk, querying and portfolio scenarios together.

## V2 walkthrough and handoff

1. Open this repository in a fresh coding session and paste [Kickoff](docs/starter-kit/PROMPTS.md#1-kickoff).
2. The agent reads [AGENTS.md](AGENTS.md) and the [V2 brief](docs/starter-kit/PROTOTYPE_BRIEF.md), runs the V1 baseline, creates the V2 task list and run log, and works through the requested scope, starting with IGX cash flow.
3. Record feedback in [V2 steering](docs/starter-kit/steering.md). The [starter prompts](docs/starter-kit/PROMPTS.md) support resuming work or requesting review and repair separately.

The [working state](docs/starter-kit/WORKING_STATE.md) tracks the V2 tasks. The [run log](docs/starter-kit/RUN_LOG.md) records executed checks, and the [V2 report and playbook](docs/report/IPO_Ready_V2_Report.md) covers both investment journeys.

## Run the local prototype

```bash
python -m pip install -r requirements.txt
python -X utf8 -m ipo_ready.server --port 8785
```

Open `http://127.0.0.1:8785/` and select IGX or OYO in **Pre-IPO · verified filings**. Open a source-backed research answer or **Cash Flow**, **Choose charts** or **Choose ratios**. **Compare this company** carries the issuer and period to Page 2. From there, add a reviewed benchmark, choose shared ratios or calculate the ₹10 lakh scenario. Historical returns are visible alongside the model cases. Old `/portfolio.html` links open the allocation section, and `/portfolio.html?legacy=1` serves the original Lab. On Windows, `view-local.bat` selects a free port and opens the preview. [Two-issuer notebook](notebooks/02_pre_ipo_cases.ipynb)

The GitHub checkout includes the built demo and source receipts. Start the server directly to use the published snapshot. The original provider and issuer downloads are kept in the local research workspace. Run `python -m ipo_ready.pipeline --offline` only after the matching local captures are available. Some research links point to those local files and their receipts identify the original sources. The [V1 handoff archive](archive/v1-handoff-20261124/README.md) links the historical data build, report, review and screenshots.

For the desktop demo, open **Compare & invest** and add companies using **Find a company or sector** or **Look up on NSE**. The workspace supports up to eight side-by-side columns and scrolls horizontally when needed. The retained catalogue includes BSE, CDSL and Astral. Set `IPO_READY_LOOKUP_OFFLINE=1` before launching the server to use retained inputs throughout. [Lookup sources and coverage](docs/research/topics/company-lookup.md)

## Reusable project material

- V2 ratios, cash-flow details and acceptance cases. [Financial ratios and cash flow](v2%20docs/Financial%20Ratios%20and%20Cash%20Flow.md)
- Earlier November exploration with portal source, web design, data, screenshots and checks. [Archive](archive/portal-exploration-20261123/README.md)
- Prior architecture and strategy. [Architecture record](docs/architecture/CURRENT_ARCHITECTURE.md) · [Staged plan](docs/product/BUILD_STRATEGY.md) · [Pinned design package](docs/architecture/BASELINE_MANIFEST.json)
- Canonical Markdown research and its native evidence. [Research entry](docs/research/README.md) · [Status](docs/research/STATUS.md) · [Evidence index](docs/research/evidence.md)
- Earlier Aether app, notebook, demo and survey builders. [October archive](archive/legacy-20261022/README.md)
