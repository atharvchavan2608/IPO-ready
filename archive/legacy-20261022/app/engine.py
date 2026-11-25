"""Evidence-backed historical analysis. Deterministic orchestration, no LLM calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'research/aether_reconciliation/pilot_data.json'
PERIODS = [
    ('9M Dec-2021', '2021-04-01', '2021-12-31', 'interim'),
    ('9M Dec-2020', '2020-04-01', '2020-12-31', 'interim'),
    ('FY21', '2020-04-01', '2021-03-31', 'annual'),
    ('FY20', '2019-04-01', '2020-03-31', 'annual'),
    ('FY19', '2018-04-01', '2019-03-31', 'annual'),
]

def ratio(a, b):
    return None if a is None or b in (None, 0) else a / b

def cagr(start, end, years):
    if start is None or end is None or start <= 0 or end <= 0 or years <= 0:
        return None
    return (end / start) ** (1 / years) - 1

def build_report(period='FY21'):
    names = [p[0] for p in PERIODS]
    if period not in names:
        raise ValueError('Unknown reporting period')
    i = names.index(period)
    raw = DATA.read_bytes()
    data = json.loads(raw)
    trace = []
    def record(tool, reason, outcome):
        trace.append({'step': len(trace)+1, 'tool': tool, 'reason': reason, 'outcome': outcome})
    record('load_curated_evidence', 'Use the previously transcribed RHP pilot; do not invent missing inputs.', '22 metrics across five dated periods loaded. No automated PDF extraction in this prototype.')
    facts=[]
    for row in data['raw']:
        facts.append({'metric':row[0], 'value':row[i+1], 'raw_unit':row[6], 'pdf_page':row[7], 'printed_page':row[8], 'basis':row[9], 'note':row[10], 'url':data['rhp_url']+'#page='+str(row[7]), 'period_start':PERIODS[i][1], 'period_end':PERIODS[i][2]})
    values={f['metric']:f['value'] for f in facts}
    record('select_period', 'Annual and interim observations must remain distinct.', f'{period}: {PERIODS[i][1]} to {PERIODS[i][2]}; no interim annualisation.')
    checks=[]
    for label, residual in [
        ('Revenue + other income = total income', values['Revenue from operations']+values['Other income']-values['Total income']),
        ('EBITDA definition bridge', values['Profit before tax']+values['Finance costs']+values['Depreciation and amortisation']-values['Other income']-values['EBITDA excluding other income']),
        ('Borrowings components = disclosed debt',values['Non-current borrowings']+values['Current borrowings']-values['Debt as disclosed']),
        ('Equity + liabilities = assets', values['Total equity']+values['Total liabilities']-values['Total assets'])]:
        checks.append({'check':label,'residual_million':round(residual,8),'tolerance_million':0.02,'passed':abs(residual)<=0.02000001})
    record('reconcile_arithmetic', 'Check internal arithmetic before explaining the figures.', f"{sum(c['passed'] for c in checks)}/4 checks within INR 0.02 million. These checks do not establish financial health.")
    derived={
        'ebitda_margin':ratio(values['EBITDA excluding other income'],values['Revenue from operations']),
        'pat_margin':ratio(values['Profit after tax'],values['Revenue from operations']),
        'cfo_pat':ratio(values['Net cash from operating activities'],values['Profit after tax']),
        'debt_equity':ratio(values['Debt as disclosed'],values['Total equity']),
    }
    flags=[{'title':'Conflicting repeated assets figure','detail':'9M Dec-2020 assets: INR 4,000.95 million on PDF p.64 versus 4,009.95 million on p.303. Statement value retained for display; cause unresolved.','pages':[64,303]},
           {'title':'Valuation inputs require review','detail':'Original price-band advertisement and post-offer share basis remain unresolved. No fair-value range or investment recommendation is generated.','pages':[109,111]},
           {'title':'Peer accounting bases differ','detail':'The RHP peer table mixes standalone and consolidated figures. Automated peer selection and normalized peer valuation are future work.','pages':[111]}]
    if derived['cfo_pat'] is not None and derived['cfo_pat'] < 1:
        flags.insert(0,{'title':'Operating cash trails accounting profit','detail':f"CFO/PAT is {derived['cfo_pat']:.3f}x for {period}. This invites working-capital investigation; it does not establish fraud or future distress.",'pages':[66,67]})
    record('route_review_items','Preserve known conflicts and label provisional definitions.',f'{len(flags)} research/review items retained; no automatic approval.')
    summary=f"For {period}, operating revenue is INR {values['Revenue from operations']/10:,.2f} crore and PAT is INR {values['Profit after tax']/10:,.2f} crore. EBITDA margin is {derived['ebitda_margin']:.1%}; operating cash flow is {derived['cfo_pat']:.3f} times PAT. Read cash conversion alongside profit growth and review the underlying accounting definitions."
    record('compose_template_summary','Every number comes from evidence or deterministic calculations.', 'Template explanation generated. No model inference, predictive score or autonomous agent execution.')
    annual=[]
    for j in [4,3,2]:
        annual.append({'period':PERIODS[j][0],**{r[0]:r[j+1]/10 for r in data['raw'] if r[0] in ['Revenue from operations','Profit after tax','Net cash from operating activities']}})
    return {'issuer':'Aether Industries','period':period,'period_kind':PERIODS[i][3],'retrospective':True,'source_document_date':'2022-05-16','historical_evidence_cutoff':'2022-05-18','reconstructed_at':datetime.now(timezone.utc).isoformat(),'engine_version':'0.1.0','input_sha256':hashlib.sha256(raw).hexdigest(),'source_status':'Hand-transcribed research pilot; not a fully adjudicated benchmark','facts':facts,'derived':derived,'checks':checks,'flags':flags,'summary':summary,'annual_trend_crore':annual,'revenue_cagr_fy19_fy21':cagr(2011.8,4498.16,2),'trace':trace,'mode':'deterministic workflow prototype'}
