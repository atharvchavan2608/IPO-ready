"""Controlled edge-case probes. No full app, live data, or repository entry point runs.
Only named pure functions are compiled from the pinned public source snapshots.
"""
import ast
import json
import re
from pathlib import Path
from statistics import median
import pandas as pd

root=Path(__file__).resolve().parent

def selected(path,names,env=None):
    tree=ast.parse((root/path).read_text(encoding='utf-8'))
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes}==set(names)
    module=ast.Module(body=nodes,type_ignores=[])
    scope={} if env is None else env
    exec(compile(module,str(path),'exec'),scope)
    return scope

fin=selected(Path('ipo-radar/backend/app/pipeline/financial_extractor.py'),['_derive_metrics','get_metric','cagr'])
val=selected(Path('ipo-radar/backend/app/pipeline/valuation.py'),['valuation_call'],{'median':median})
builder=selected(Path('ipo-ai/src/build_dataset.py'),['first_full_year'],{'re':re})
out=[]

gap={'series':{'FY25':{'revenue':121},'FY23':{'revenue':100}},'fiscal_order':['FY25','FY23']}
actual=fin['cagr'](gap,'revenue')
assert round(actual,8)==0.21
out.append({'case':'Nonconsecutive fiscal years','input':'FY23 revenue 100, FY25 revenue 121','observed_cagr':actual,'calendar_year_cagr':0.10,'interpretation':'Function uses the number of retained observations minus one, not elapsed fiscal years.'})

series={'FY25':{'borrowings_lt':100}}
fin['_derive_metrics'](series)
assert series['FY25']['total_debt']==100
out.append({'case':'Only long-term debt extracted','input':'Long-term debt 100, short-term debt unknown','observed_total_debt':100,'interpretation':'Missing debt component is treated as zero during derivation.'})

series={'FY25':{'total_income':120}}
fin['_derive_metrics'](series)
assert series['FY25']['revenue']==120
out.append({'case':'Other income not extracted','input':'Total income 120, other income unknown','observed_revenue':120,'interpretation':'Other income defaults to zero in revenue derivation.'})

result=val['valuation_call'](None,[{'pe':10},{'pe':12}],{},price_high=100,issuer_eps=5)
assert result['issuer_pe']==20
out.append({'case':'EPS fallback','input':'Offer price 100, supplied EPS 5, peer P/Es 10 and 12','observed_issuer_pe':result['issuer_pe'],'observed_call':result['call'],'interpretation':'The function accepts EPS without identifying whether it is current annual, TTM or multi-year weighted EPS.'})

periods=['31 Mar 2023','31 Mar 2025','31 Dec 2025']
actual=builder['first_full_year'](periods)
assert actual==(0,1)
out.append({'case':'Unsorted financial period columns','input':periods,'selected_indices':actual,'interpretation':'The first two March year-ends are used in input order rather than sorted by date.'})

missing=pd.Series([float('nan'),-5.0,5.0])
actual=(missing<0).tolist()
assert actual==[False,True,False]
out.append({'case':'Unknown PAT in loss flag expression','input':['missing',-5,5],'observed_is_lossmaking':actual,'interpretation':'The comparison used in build_dataset.py maps a missing numeric PAT to False. Keep an explicit unknown state.'})

pre,post=100,125
out.append({'case':'Two dilution definitions','input':'Pre-issue shares 100, post-issue shares 125','repo_equity_dilution_pct':(post/pre-1)*100,'old_holder_ownership_dilution_pct':(1-pre/post)*100,'interpretation':'The repository metric measures share-count expansion. It differs from the reduction in an unchanged shareholder stake.'})

(root/'probe_results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
