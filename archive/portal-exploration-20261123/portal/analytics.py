"""Deterministic Decimal arithmetic. Source review is separate from calculation validity."""
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

VERSION = 'financial-v0.1.0'
USABLE = {'reported', 'explicit_zero'}
STATES = USABLE | {'missing', 'nil', 'not_applicable', 'conflicting', 'unresolved'}

def number(value):
    if isinstance(value, bool) or value is None:
        raise ValueError('A finite numeric value is required')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('A finite numeric value is required') from None
    if not result.is_finite():
        raise ValueError('A finite numeric value is required')
    return result

def amount(fact):
    if fact['state'] not in USABLE:
        return None
    return number(fact['raw_value'].replace(',', ''))

def formatted(value):
    return str(value.quantize(Decimal('0.0001'))) if value is not None else None

def compatible(facts, same_period=True):
    keys = ['company_id', 'basis', 'raw_unit', 'currency']
    if same_period:
        keys += ['period_start', 'period_end']
    return all(all(f.get(k) == facts[0].get(k) for k in keys) for f in facts)

def result(metric, facts, formula, value=None, reason=None, unit='percent'):
    return {'id': metric, 'value': formatted(value), 'unit': unit,
            'state': 'unavailable' if value is None else 'available', 'reason': reason,
            'formula': formula, 'formula_version': VERSION,
            'operand_fact_ids': [f['id'] for f in facts],
            'period_end': facts[0]['period_end'], 'basis': facts[0]['basis'],
            'review_state': 'provisional_secondary'}

def ratio(metric, numerator, denominator, scale=Decimal(100), positive_numerator=False):
    facts = [numerator, denominator]
    formula = f'{numerator["metric_id"]} / {denominator["metric_id"]} * {scale}'
    unit = 'times' if scale == 1 else 'percent'
    if not compatible(facts):
        return result(metric, facts, formula, reason='Incompatible periods, units or reporting basis', unit=unit)
    n, d = amount(numerator), amount(denominator)
    if n is None or d is None:
        return result(metric, facts, formula, reason='Operand unavailable; missing states are preserved', unit=unit)
    if d <= 0 or (positive_numerator and n < 0):
        return result(metric, facts, formula, reason='Nonpositive denominator or ineligible numerator', unit=unit)
    return result(metric, facts, formula, n / d * scale, unit='times' if scale == 1 else 'percent')

def growth(current, previous):
    facts = [current, previous]
    formula = '(current operating revenue / previous operating revenue - 1) * 100'
    current_end, previous_end = date.fromisoformat(current['period_end']), date.fromisoformat(previous['period_end'])
    annual_pair = (current_end.month, current_end.day) == (previous_end.month, previous_end.day) and current_end.year - previous_end.year == 1
    if (not compatible(facts, False) or current['metric_id'] != previous['metric_id'] or not annual_pair
            or current['period_start'] != (previous_end + timedelta(days=1)).isoformat()
            or not 350 <= (current_end - date.fromisoformat(current['period_start'])).days <= 370
            or not 350 <= (previous_end - date.fromisoformat(previous['period_start'])).days <= 370):
        return result('operating_revenue_yoy', facts, formula, reason='Requires consecutive annual periods with matching definitions')
    n, d = amount(current), amount(previous)
    if n is None or d is None or n <= 0 or d <= 0:
        return result('operating_revenue_yoy', facts, formula, reason='Requires positive reported endpoints')
    return result('operating_revenue_yoy', facts, formula, (n / d - 1) * 100)

def cagr(first, last):
    facts = [last, first]
    formula = '(last / first) ** (1 / elapsed fiscal years) - 1'
    a, b = date.fromisoformat(first['period_end']), date.fromisoformat(last['period_end'])
    years = b.year - a.year
    n, d = amount(last), amount(first)
    if not compatible(facts, False) or first['metric_id'] != last['metric_id'] or years <= 0 or (a.month, a.day) != (b.month, b.day) or n is None or d is None or min(n, d) <= 0:
        return result('operating_revenue_cagr', facts, formula, reason='Requires matching positive fiscal endpoints')
    return result('operating_revenue_cagr', facts, formula, ((n / d) ** (Decimal(1) / years) - 1) * 100)

def income_residual(facts):
    ordered = [facts[k] for k in ['provider_total_income', 'operating_revenue', 'other_income']]
    formula = 'provider total income - operating revenue - other income'
    values = [amount(f) for f in ordered]
    if not compatible(ordered) or any(v is None for v in values):
        return result('income_residual', ordered, formula, reason='Income components unavailable or incompatible', unit='INR crore')
    return result('income_residual', ordered, formula, values[0] - values[1] - values[2], unit='INR crore')

def scenario(snapshot, command):
    expected = {'company_id', 'period_end', 'growth_pct', 'profit_pct'}
    if not isinstance(command, dict) or set(command) != expected:
        raise ValueError('Supply company_id, period_end, growth_pct and profit_pct only')
    if command['company_id'] != snapshot['company']['id']:
        raise ValueError('Unknown company')
    g, p = number(command['growth_pct']), number(command['profit_pct'])
    if not -30 <= g <= 30 or not 0 <= p <= 100:
        raise ValueError('Growth must be -30 to 30%; assumed profit percentage must be 0 to 100%')
    base = next((f for f in snapshot['observations'] if f['period_end'] == command['period_end'] and f['metric_id'] == 'operating_revenue'), None)
    if not base or amount(base) is None or amount(base) <= 0:
        raise ValueError('A positive reported base operating revenue is required')
    revenue = amount(base) * (1 + g / 100)
    return {'snapshot_id': snapshot['snapshot_id'], 'formula_version': VERSION,
            'inputs': {**command, 'growth_pct': str(g), 'profit_pct': str(p)},
            'base_fact_id': base['id'], 'hypothetical_operating_revenue': formatted(revenue),
            'hypothetical_continuing_profit': formatted(revenue * p / 100), 'unit': 'INR crore',
            'formula': 'base operating revenue * (1 + growth_pct / 100) * profit_pct / 100',
            'review_state': 'provisional_secondary', 'basis': base['basis'],
            'interpretation': 'One-year assumption sensitivity; not a forecast or valuation'}
