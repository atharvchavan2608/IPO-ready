"""Validate observation contracts and prepare coherent local read projections."""
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from . import analytics as calc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'portal/data/observations.json'

def validate(data):
    seen = set()
    for fact in data['observations']:
        if fact['id'] in seen: raise ValueError('Duplicate observation ID')
        seen.add(fact['id'])
        if fact['state'] not in calc.STATES: raise ValueError('Unknown observation state')
        if fact['state'] in calc.USABLE:
            value = calc.amount(fact)
            if (value == 0) != (fact['state'] == 'explicit_zero'):
                raise ValueError('Explicit zero must have its own state')
        elif fact['raw_value'] is not None:
            raise ValueError('Non-numeric observation state must preserve null and separate conflict evidence')
        path = (ROOT / fact['evidence_path']).resolve()
        if not path.is_relative_to(ROOT) or sha256(path.read_bytes()).hexdigest() != fact['evidence_sha256']:
            raise ValueError('Evidence path/hash mismatch')
    return data

def build(reference=False):
    raw = DATA.read_bytes()
    data = validate(json.loads(raw))
    reference_data = data.pop('reference_dataset')
    if reference:
        data = {**data, **reference_data}
        validate(data)
    code = Path(calc.__file__).read_bytes() + Path(__file__).read_bytes()
    snapshot_id = 'research-' + sha256(raw + code + str(reference).encode()).hexdigest()[:16]
    ends = sorted({f['period_end'] for f in data['observations']})
    periods, previous = [], None
    for end in ends:
        facts = {f['metric_id']: f for f in data['observations'] if f['period_end'] == end}
        revenue, profit, cfo = (facts[k] for k in ['operating_revenue', 'continuing_profit', 'cfo'])
        metrics = [calc.ratio('continuing_profit_to_revenue', profit, revenue),
                   calc.ratio('cash_conversion', cfo, profit, Decimal(1)), calc.income_residual(facts)]
        if previous: metrics.append(calc.growth(revenue, previous))
        periods.append({'period_end': end, 'label': 'FY' + end[2:4], 'fact_ids': [f['id'] for f in facts.values()], 'metrics': metrics})
        previous = revenue
    first, last = [next(f for f in data['observations'] if f['period_end'] == end and f['metric_id'] == 'operating_revenue') for end in [ends[0], ends[-1]]]
    return {**data, 'snapshot_id': snapshot_id, 'calculation_version': calc.VERSION,
            'input_sha256': sha256(raw).hexdigest(), 'code_sha256': sha256(code).hexdigest(),
            'built_at': datetime.now(timezone.utc).isoformat(), 'historical_reconstruction': True,
            'public_availability_date': None, 'periods': periods, 'summary_metrics': [calc.cagr(first, last)],
            'coverage': {'issuer_count': 1, 'annual_periods': len(ends), 'observations': len(data['observations']),
                         'primary_reviewed': 0, 'basis': 'unspecified', 'valuation_state': 'unavailable', 'ranking_state': 'unavailable'}}

if __name__ == '__main__':
    output = ROOT / 'outputs/portal'
    output.mkdir(parents=True, exist_ok=True)
    snapshot = build()
    (output / 'research-snapshot.json').write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'snapshot_id': snapshot['snapshot_id'], 'coverage': snapshot['coverage']}))
