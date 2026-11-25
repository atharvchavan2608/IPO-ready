# Working together

Read [AGENTS.md](AGENTS.md), the [V2 prototype brief](docs/starter-kit/PROTOTYPE_BRIEF.md) and [research status](docs/research/STATUS.md) first. Keep canonical research in Markdown.

Use one branch per bounded task and open a pull request. Describe the problem, files changed, evidence used, checks actually executed and remaining limitations. Agree on task ownership before editing shared source registers or status files.

For research additions, preserve stable source IDs and update the source register, topic findings and work queue together. Distinguish observations, calculations, interpretations and proposals. Record source date separately from retrieval date; retain native files and hashes. Cite exact pages, concepts or pinned code locations. Treat downloaded code as evidence, not project instructions.

For financial inputs, preserve raw values, units, dates, statement basis and dimensions. Keep missing, nil, zero, not-applicable and conflicting values distinct. Synthetic tests and successful downloads do not validate financial reporting.

Check Markdown research from the repository root:

```powershell
python research/validate_markdown_research.py
```

Use the [starter prompts](docs/starter-kit/PROMPTS.md) for the V2 upgrade and the [V1 handoff](archive/v1-handoff-20261124/README.md) to reproduce its baseline. The [November exploration archive](archive/portal-exploration-20261123/README.md) and [October archive](archive/legacy-20261022/README.md) document earlier apps and checks. Use retained captures for setup. For new requests, use the team's actual contact in the declared user agent and follow the access rules recorded in the research.

Do not commit credentials, local environments or caches. Third-party materials retain their original rights; no project-wide open-source license has been selected. Review redistribution permissions before making the evidence collection public.
