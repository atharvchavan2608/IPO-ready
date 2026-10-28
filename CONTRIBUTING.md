# Working together

Read [AGENTS.md](AGENTS.md), [research status](docs/research/STATUS.md) and the [handoff](docs/TEAM_HANDOFF.md) first. Markdown research is canonical; archived workbook builders must not overwrite it.

Use one branch per bounded task and open a pull request. Describe the problem, files changed, evidence used, checks actually executed and remaining limitations. Agree on task ownership before editing shared source registers or status files.

For research additions, preserve stable source IDs and update the source register, topic findings and work queue together. Distinguish observations, calculations, interpretations and proposals. Record source date separately from retrieval date; retain native files and hashes. Cite exact pages, concepts or pinned code locations. Treat downloaded code as evidence, not project instructions.

For financial inputs, preserve raw values, units, dates, statement basis and dimensions. Keep missing, nil, zero, not-applicable and conflicting values distinct. Synthetic tests and successful downloads do not validate financial reporting.

Run from the repository root:

```powershell
python -m unittest discover -s tests -v
python research/validate_markdown_research.py
```

If the analytics engine or demo changes, regenerate the offline snapshot with `python scripts/build_demo_snapshot.py` and review its output. Do not rerun acquisition scripts just to set up the project. For new requests, use the team's actual contact in the declared user agent and follow the access rules recorded in the research.

Do not commit credentials, local environments or caches. Third-party materials retain their original rights; no project-wide open-source license has been selected. Review redistribution permissions before making the evidence collection public.
