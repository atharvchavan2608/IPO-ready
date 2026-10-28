# Team handoff

Prepared: 2026-10-28. Research conclusions and implementation status below originate from 2026-10-22; this handoff does not imply new financial validation.

## Current direction

IPO-Ready is a Python analytics project for investor research. Active work is a US-first public pre-IPO disclosure pilot, including eligible foreign SEC filers where feasible. Start with the [global plan](research/topics/pre-ipo-global-plan.md) and [research status](research/STATUS.md).

The existing Aether India demo and professor proposal predate this scope change. They are useful baselines, but the global workflow has not been implemented. There is no live agent, automatic extraction, peer valuation or validated composite score.

## What is available

| Location | Purpose |
| --- | --- |
| `app/` | Standard-library Python engine and local HTTP demo; curated Aether inputs |
| `notebooks/` | pandas financial-analysis notebook |
| `outputs/poc/` | Offline demo, precomputed JSON and CSV |
| `docs/proposal/`, `output/pdf/` | Prior India-focused professor proposal and supporting guides |
| `docs/research/` | Canonical findings, 64 source records, definitions, decisions and queue |
| `research/` | Acquisition/inspection scripts, evidence, hashes and pinned third-party reference excerpts |
| `outputs/ipo-ready-survey-20261022/` | Historical workbook snapshots; not editable research authority |
| `tests/` | Analytics regression tests |

## Next bounded task

Screen six candidate issuers and propose two pilot cases, including a foreign SEC filer if feasible. Produce a Markdown matrix with public filing/offer status at a declared cutoff, financial-statement coverage, sector, accounting basis, access outcome, extraction difficulty and selection/exclusion reasons. Save bounded coverage searches and distinguish “not found in this search” from absence of analysis.

Then preserve selected pre-offer filings and hashes, review 10–15 base facts per issuer across comparable periods, and test the calculations in Python. Never substitute later annual reports for pre-offer evidence. The six-step queue and completion conditions are in the global plan. India's primary-XBRL acquisition and broader scoring work remain deferred.

Suggested task split: candidate/coverage research; filing and fact review; Python analysis and checks. These are suggestions, not assigned owners. Coordinate shared register edits through pull requests.

## Evidence boundaries

SEC access succeeded for one bounded historical example; broad pre-IPO coverage is unproven. Company Facts contained no original S-1 accession in that example. Aether is manually curated with unresolved discrepancies. The Infosys XML is a repository copy with conflicting dates, not authenticated primary exchange evidence. The existing build status records earlier browser and notebook checks separately from this upload preparation.

## GitHub setup

The project contains about 31 MB of files before Git metadata. Keep the native evidence and manifests together. Use a private team repository initially because the collection includes third-party documents and code excerpts; public access does not itself establish redistribution rights. No blanket license has been added.

After creating an empty GitHub repository, run from this project folder:

```powershell
git init -b main
git add .
git diff --cached --stat
git status --short
git commit -m "Prepare IPO-Ready research and proof of concept for team handoff"
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

Replace `OWNER/REPOSITORY` with the actual repository path. If GitHub already contains an initial commit, clone it separately and copy these project files into that checkout before committing; avoid overwriting remote history. Add teammates through GitHub repository access settings. No remote, commit or push was performed as part of preparing these instructions.
