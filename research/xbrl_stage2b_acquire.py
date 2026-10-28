"""Bounded acquisition from exact links observed in a pinned public manifest."""
from pathlib import Path
from urllib.request import urlopen
import json,hashlib,concurrent.futures
root=Path('research/xbrl_stage2_20261022')
rows=[json.loads(l) for l in (root/'alternative_filings_manifest.jsonl').read_text().splitlines()]
selected=[r for r in rows if r['isin']=='INE009A01021' and r['filing_type']=='financial_results' and r.get('consolidated')=='Consolidated' and ('fourth-2023-24' in r.get('local_path','') or 'fourth-2024-25' in r.get('local_path',''))]
def fetch(r):
 url=r['xbrl_url'];name=url.rsplit('/',1)[1]
 try:
  with urlopen(url,timeout=18) as response: data=response.read()
  (root/name).write_bytes(data)
  return {'url':url,'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'manifest_hash_matches':hashlib.sha256(data).hexdigest()==r['sha256'],'retrieved_on':'2026-10-22','status':'downloaded'}
 except Exception as e:return {'url':url,'status':'failed','error':str(e),'retrieved_on':'2026-10-22'}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: result=list(pool.map(fetch,selected))
(root/'primary_xml_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
