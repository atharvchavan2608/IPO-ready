# ADR-002: Prefer structured observations where verified

- Status: proposed, not an implemented architecture.
- Date: 2026-10-22.
- Evidence: [X01](../sources/X01.md), [X02](../sources/X02.md), [X03](../sources/X03.md), [X06](../sources/X06.md), [X07](../sources/X07.md).

## Direction

For listed-company financials, investigate XBRL before building general PDF extraction. Use prospectuses and annual-report notes for restated pre-IPO statements, business context and disclosures that the structured feed does not cover. Reconcile overlapping facts across both routes.

## Conditions before adopting

- Obtain and validate a real raw instance, not just a rendered HTML view.
- Establish exact taxonomy/version and report basis.
- Preserve fact identity, contexts, units, precision and revisions.
- Match selected facts against the signed or published financial report.
- Measure coverage across a small issuer/year sample; then assess maintenance effort and access suitability.

## Why provisional

The current XBRL work is reconnaissance. We have not established historical coverage, primary XML availability for the pilot, complete taxonomy resolution or accuracy across sectors. Existing parser shortcuts require review before reuse.
