# Candidate financial fact record

Status: proposed research specification. Not application code or a final database schema.

Evidence: [A01–A09](sources/INDEX.md), [Aether pilot](pilots/aether-ipo-2022.md), [X04](sources/X04.md), [X06](sources/X06.md), [X07](sources/X07.md).

## Identity and timing

| Field | Required meaning |
| --- | --- |
| Issuer identifier | ISIN/CIN/exchange code where available; source scheme retained |
| Document/filing ID | Immutable ID and SHA-256 of source bytes |
| Source type | RHP, annual report, result PDF, XBRL instance, genuine inline instance, or rendered HTML |
| Document date | Date stated in the document |
| Published/filed time | Exchange/regulator availability time; unknown if not established |
| Retrieved time | When we obtained the bytes |
| Revision relation | Original/revised filing link, preserved rather than overwritten |
| Assessment cutoff | Latest information time allowed for a historical analysis |

## Reported fact

| Field | Required meaning |
| --- | --- |
| Source concept | Full namespace URI plus local name for XBRL; exact label for PDF |
| Taxonomy | Family, version, schemaRef and resolved package hash; unresolved stays unresolved |
| Context | Original context ID plus decoded entity, period and every explicit/typed dimension |
| Statement basis | Standalone/consolidated and scope; never inferred from company alone |
| Period | Start/end for flows or instant for stocks; duration and fiscal labeling retained |
| Unit | Resolved measure or numerator/denominator, original unitRef |
| Raw value | Exact source lexical value, original label and nil marker |
| Numeric value | Decimal representation after valid transformations; no float-only authoritative storage |
| Accuracy | Source decimals/precision; distinct from presentation scale |
| Inline transformation | Format, sign, scale and continuation evidence where genuinely present |
| Location | Fact ID/XML locator or physical PDF page and table/cell region |
| State | Reported, missing, nil, explicit zero, not applicable, conflicting or unresolved |

## Normalized or derived value

Keep canonical metric ID, mapping version and rationale separate from the reported concept. Record unit conversion, formula, operand fact IDs, period alignment, adjustments, uncertainty and review state. An agent explanation must point to these records rather than perform hidden arithmetic.

## Duplicate identity

Compare full concept, entity, complete context aspects and unit within the appropriate filing/version. Original context IDs and prefixes are syntax, not sufficient semantic identity. Preserve duplicate candidates and their accuracy before deciding consistency. Never use last-value-wins to erase conflicts.

## Agent responsibilities

Discovery locates and records documents. Deterministic parsers expose facts and validation results. Mapping proposes a canonical interpretation with evidence. Calculations consume reviewed definitions. Narrative explains verified outputs and flags unknowns. Human review addresses ambiguous accounting, peer choices and material unresolved conclusions. These are logical responsibilities; no multi-agent framework has been chosen.
