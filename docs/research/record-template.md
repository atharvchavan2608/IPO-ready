# Research record conventions

Use one stable ID per reviewable record. A paper, its code and its dataset may warrant separate records because review depth differs. IDs R/P/T/D/A/B are preserved from Excel; X identifies the XBRL strand; U identifies the US/global-scope feasibility strand added on 2026-10-22.

## Record fields

- ID, title, type, publisher/authors, publication/version date and checked-on date.
- Direct source URL; pinned commit and file path for code.
- Market/task and why the source is relevant.
- Observed finding: what the source or experiment actually establishes.
- Review basis/depth: excerpt, abstract, selected full text, code, fixture, real filing, or executed probe.
- Interpretation and potential use: separate from source statements.
- Limitations, access/reuse status and next investigation.
- Related source IDs, topic notes and evidence files where helpful.

## Updating

Append meaningful later evidence and date it. Do not silently upgrade an abstract review to a full-paper review or a fixture parse to real-instance validation. Update `STATUS.md` and the relevant synthesis when a finding changes direction. Keep raw inputs immutable and preserve revisions as separate evidence.
