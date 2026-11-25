# Native evidence and reproducibility

## V2.1 pre-IPO evidence, 2026-11-25

- [Issuer manifest and selected pages](../../data/captures/issuer/20261125-v21/manifest.json) records the IGX notice, Oravel draft, October addendum and annual exhibit with original-page mapping, and Lemon Tree's annual filing.
- [Free-research manifest](../../data/captures/free_ipo_research/20261125-v21/manifest.json) retains the three independent product pages reviewed. The [four-question audit](topics/v21-pre-ipo-cases.md) and [executed notebook](../../notebooks/02_pre_ipo_cases.ipynb) show what can be reproduced.
- [Liquid BeES primary evidence](sources/N26.md) and [method inputs](sources/N27.md) link to the allocation source, receipt and scenario work.

## Portal and expert-method evidence, 2026-11-12

- [Pinned architecture manifest](../architecture/BASELINE_MANIFEST.json): 16 native files from exact GitHub commit; [sync script](../../research/sync_design_baseline.py). Diagram builders were retained, not executed.
- [Free-source request directories](../../research/unlisted_sources_20261112/): immutable initial failures, native provider HTML, 404 body, issuer status/transcript PDFs and selected broker notes with SHA-256 manifests. See [executed command log and interpretation](topics/unlisted-free-data.md).
- [Offline reviewed-value adapter](../../archive/portal-exploration-20261123/research/prepare_unlisted_pilot.py), [30 observations](../../archive/portal-exploration-20261123/portal/data/observations.json), [Python projection](../../archive/portal-exploration-20261123/outputs/portal/research-snapshot.json), [browser results](../../archive/portal-exploration-20261123/outputs/portal/browser-check.json) and [software status](../BUILD_STATUS.md).
- Archive manifests record original paths, retained paths and verified hashes for the [November portal](../../archive/portal-exploration-20261123/manifest.json) and [October demo](../../archive/legacy-20261022/manifest.json).

The expert-note PDFs were read locally with `pypdf`; selected pages saved as text. `pdftoppm -f 1 -singlefile -scale-to 1400 -png` rendered the Canara NSDL cover and it was visually inspected. The stale first extracted issuer/date differs from the visible cover. This is extraction/identity evidence, not validation of the report's investment view.

The Markdown knowledge base is canonical. Native evidence remains in its original format so later agents can verify findings.

| Evidence | Location | Review scope |
| --- | --- | --- |
| Archived full research workbook | [Pass 3](../../outputs/ipo-ready-survey-20261022/IPO_Ready_Research_Survey_Pass3.xlsx) | Migrated; no further workbook authoring planned |
| Aether RHP and hash | [Manifest](../../research/aether_reconciliation/document_manifest.json) | Primary PDF; selected tables reviewed |
| Aether extraction and checks | [Evidence directory](../../research/aether_reconciliation/) | Text, page renders and research scripts |
| IPO Radar / ipo-ai snapshots | [Pinned manifest](../../research/github_audit_20261022/manifest.json) | Selected code only |
| Seven controlled audit examples | [Probe results](../../research/github_audit_20261022/probe_results.json) | Synthetic boundaries and arithmetic |
| XBRL repository snapshots and access outcomes | [Download manifest](../../research/xbrl_stage1_20261022/download_manifest.json) | Selected files, hashes and failed direct-download attempts |
| One-time migration | [Migration script](../../research/migrate_excel_to_md.py) | Reads XLSX XML; no Excel writes |

## Execution boundaries

Downloaded public repositories are untrusted reference content. Their full applications, scrapers and test suites were not executed. No third-party XBRL package was installed. Fixture XML was inspected using the Python standard library; this is not schema, dimensional or regulatory validation.

## XBRL stage 2A evidence

- [Native evidence directory](../../research/xbrl_stage2_20261022): official PDF, issuer HTML, hashes, request outcomes, extracted text and selected page renders.
- [Comparison script](../../research/xbrl_stage2_reconcile.py): 26 manual observations, unit conversion and differences; no XML parsing.
- [Acquisition script](../../research/xbrl_stage2_acquire.py): bounded discovery attempts; rerunning may change live evidence.
- [Interpretation and comparison table](topics/xbrl-stage-2.md).

## XBRL stage 2B evidence

- [Inspection script](../../research/xbrl_stage2b_inspect.py): 417 facts, 81 contexts, four units, 16 selected numeric comparisons and period checks.
- [Primary request script](../../research/xbrl_stage2b_acquire.py) and [outcomes](../../research/xbrl_stage2_20261022/primary_xml_manifest.json): NSE timeout and BSE 403.
- [Pinned tree](../../research/xbrl_stage2_20261022/alternative_repo_tree.json), [manifest](../../research/xbrl_stage2_20261022/alternative_filings_manifest.jsonl), [XML acquisition record](../../research/xbrl_stage2_20261022/infosys_copy_manifest.json), [full inventory](../../research/xbrl_stage2_20261022/infosys_inventory.json).
- [Investigation](topics/xbrl-stage-2b.md). Repository client reference was read only, not executed.

## US/global pre-IPO planning evidence, 2026-10-22

- [Acquisition script](../../research/us_scope_feasibility.py): eight exact public-source URLs, sequential requests, no API key, 12-second timeout and 0.6-second inter-request delay. Saves each run separately.
- [First run](../../research/us_scope_20261022/20261022T115822125560Z/manifest.json): eight DNS failures; no source bytes obtained.
- [Network-enabled retry](../../research/us_scope_20261022/20261022T115849017612Z/manifest.json): seven HTTP 200 responses and one form-PDF 403. Native HTML/JSON and the 403 error body have SHA-256 hashes. The error body is not the PDF.
- [Metadata inspection](../../research/us_scope_inspect.py) and [output](../../research/us_scope_20261022/20261022T115849017612Z/companyfacts_inventory.json): retained Reddit Company Facts response; no original S-1 accession; no financial-value checks.
- [Interpretation and initial plan](topics/pre-ipo-global-plan.md); [source records U01–U06](sources/INDEX.md). Form F-1 instructions were reviewed through web-extracted PDF text; their original PDF bytes were not acquired locally. Web review of Arm's historical F-1 identity was exploratory and is not a selected pilot or financial review.
