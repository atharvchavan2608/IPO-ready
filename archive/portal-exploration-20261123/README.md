# November portal exploration

Archived on 23 November 2026 for the fresh prototype build. The [manifest](manifest.json) records original paths and SHA-256 hashes for 17 files.

| Material | Reference |
| --- | --- |
| Python analytics, local server and original web design | [Original portal](portal/) |
| Provisional IGX and NSE observations | [Observation JSON](portal/data/observations.json) |
| Offline source preparation and original checks | [Preparation script](research/prepare_unlisted_pilot.py) · [Python tests](tests/test_portal.py) · [Browser check](scripts/check_portal.py) |
| Saved demo views and results | [Desktop](outputs/portal/dashboard-desktop.png) · [Mobile](outputs/portal/dashboard-mobile.png) · [Prepared snapshot](outputs/portal/research-snapshot.json) · [Browser results](outputs/portal/browser-check.json) |
| Research backing and design context | [Native captures](../../research/unlisted_sources_20261112/) · [Build record](../../docs/BUILD_STATUS.md) · [Historical architecture](../../docs/architecture/CURRENT_ARCHITECTURE.md) · [Historical strategy](../../docs/product/BUILD_STRATEGY.md) · [Historical contracts](../../docs/product/DATA_CONTRACTS.md) |

The original files retain their historical paths and contents inside this archive. To reproduce the server or tests, copy the archived layout to an isolated scratch folder and add the repository's native captures at `research/unlisted_sources_20261112/` within that folder. Run commands from that scratch folder so the original relative evidence paths resolve. The stored data consists of provisional secondary observations with an unspecified reporting basis.
