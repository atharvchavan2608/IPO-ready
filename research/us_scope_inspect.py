"""Read retained API responses; do not infer pre-IPO coverage from HTTP success."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

root = Path(sys.argv[1])
facts_path = root / "reddit_companyfacts.json"
payload = json.loads(facts_path.read_bytes())
forms = Counter()
accessions = set()
observations = 0
for concepts in payload["facts"].values():
    for concept in concepts.values():
        for entries in concept.get("units", {}).values():
            for entry in entries:
                observations += 1
                forms[entry.get("form", "<missing>")] += 1
                if entry.get("accn"):
                    accessions.add(entry["accn"])
result = {
    "input": facts_path.name,
    "input_sha256": hashlib.sha256(facts_path.read_bytes()).hexdigest(),
    "observations": observations,
    "observations_by_form": dict(sorted(forms.items())),
    "first_s1_accession": "0001628280-24-006294",
    "first_s1_accession_present": "0001628280-24-006294" in accessions,
    "limit": "Metadata inventory only. No values, periods, accounting definitions or original statements reconciled."
}
(root / "companyfacts_inventory.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
