import urllib.request,json
from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
shas={r['repo']:r['sha'] for r in manifest}
def fetch(repo,path):
 data=urllib.request.urlopen(f'https://raw.githubusercontent.com/{repo}/{shas[repo]}/{path}',timeout=40).read()
 dest=root/repo.split('/')[1]/path
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 return dest
p=fetch('gagandt/ipo-ai','data/out/ipos.csv')
df=pd.read_csv(p)
print('ipo-ai dataset:',df.shape)
print('Missing PAT and loss flag:',df.loc[df.pat_fy_latest_cr.isna(),['symbol','pat_fy_latest_cr','is_lossmaking']].head(8).to_dict('records'))
print('Missing PAT total:',int(df.pat_fy_latest_cr.isna().sum()))
print('Symbol duplicates:',int(df.symbol.duplicated().sum()))
q=fetch('rohanbeingsocial/ipo-radar','docs/data/ipos.json')
d=json.loads(q.read_text(encoding='utf-8'))
print('Radar JSON root:',type(d).__name__, list(d)[:12] if isinstance(d,dict) else len(d))
def walk(x):
 if isinstance(x,dict):
  if any(isinstance(v,str) and 'aether' in v.lower() for v in x.values()):
   print('Aether index row:',json.dumps(x)[:2500])
  for v in x.values():
   if isinstance(v,(dict,list)):walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(d)
