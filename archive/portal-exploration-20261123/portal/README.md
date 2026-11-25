# IPO-Ready research portal: milestone 1

Run from the project root with Python 3.10+; runtime uses only the standard library:

```powershell
python -m portal.main
```

Open http://127.0.0.1:8766. Stop with Ctrl+C. Use `--port 8767` to select another loopback port.

The active dataset is Indian Gas Exchange (pre-IPO candidate). NSE is a recent-IPO reference, not currently unlisted. Each has 15 secondary observations over FY24-FY26. Company status has separate dated evidence. Provider basis is unknown; issuer reconciliation remains the next task.

Interactive features: company/year selection, crore/million display conversion, financial trend and history, formula/source inspection, one-period assumption sensitivity calculated in Python, reference exclusions, coverage and JSON download. The source figures are real provider observations; the scenario is hypothetical. No scoring, price target, automatic recommendations or trained AI model.

Reproduce without a network call:

```powershell
python research/prepare_unlisted_pilot.py
python -m portal.snapshot
python -m unittest discover -s tests -v
python research/validate_markdown_research.py
```

The preparation script checks exact values in the retained HTML; it does not approve accounting definitions. Snapshot JSON is written under `outputs/portal/`. Browser QA additionally needs already installed Playwright and Chrome, plus the running server: `python scripts/check_portal.py`.

See [strategy](../docs/product/BUILD_STRATEGY.md), [current architecture](../docs/architecture/CURRENT_ARCHITECTURE.md) and [contracts](../docs/product/DATA_CONTRACTS.md). The superseded October app is [archived](../archive/legacy-20261022/README.md).
