# IPO-Ready financial intelligence platform

## Target product architecture - 29 October 2026

Active development follows the [fintech product architecture](docs/architecture/IPO_Ready_Design_Framework.md), [seven-view diagram PDF](docs/architecture/IPO_Ready_Architecture_Design.pdf), and [implementation backlog](docs/architecture/IMPLEMENTATION_BACKLOG.md). Discover, compare, evaluate, shortlist and monitor companies. The earlier mockup is a reference fixture, not a design constraint. Components and analytical policies remain proposed, not implemented or validated.

## Historical research workspace

Research for a Python programming-analytics project with a possible longer-term financial-research application. Scope expanded on 2026-10-22 to foreign pre-IPO companies, prioritising free APIs. Active work is [initial planning with a US-first source pilot](docs/research/topics/pre-ipo-global-plan.md); product design follows later. The Indian IPO pilot is retained as prior work.

Start with [the research entry point](docs/research/README.md), then [current status and next work](docs/research/STATUS.md).

Teammates: read the [team handoff and next task](docs/TEAM_HANDOFF.md) and [contribution guide](CONTRIBUTING.md). The handoff includes repository setup commands and the boundaries between current research and the earlier demo.

## Run the existing demo

Python 3.10+ is required. The app and regression tests use the standard library; no API keys or package installation are needed.

```powershell
python app/main.py
```

Open <http://127.0.0.1:8765>. Alternatively, open [the offline demo](outputs/poc/IPO_Ready_Demo.html) directly in a browser. It displays precomputed Python results. The optional notebook requires pandas and a Jupyter-compatible environment; rebuilding the proposal PDF requires reportlab. Historical research and browser scripts have separate dependencies and are not required to run the app.

```powershell
python -m unittest discover -s tests -v
python research/validate_markdown_research.py
```

The research check validates archive migration, local research links and fixture inventory; it does not validate financial reporting. See [build status](docs/BUILD_STATUS.md) for prior verification and limitations.

The canonical research is plain Markdown under `docs/research/`. Historical Excel workbooks under `outputs/` are preserved snapshots. Native documents, pinned public source code and small research probes under `research/` support the evidence trail.

Earlier user-authorized work produced an [India-focused proposal](docs/proposal/IPO_Ready_Project_Proposal.md) and [local Python proof of concept](app/README.md). These predate the scope change. Python analytics is the academic core. Live agent routing remains unimplemented.
