"""Bounded public-link discovery; no authentication workaround or URL guessing."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
import hashlib,json,concurrent.futures

root=Path('research/xbrl_stage2_20261022');root.mkdir(parents=True,exist_ok=True)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   href=dict(attrs).get('href')
   if href:self.hrefs.append(href)
def fetch(job):
 name,url=job
 try:
  with urlopen(url,timeout=18) as r:data=r.read()
  (root/name).write_bytes(data)
  parser=Links();parser.feed(data.decode('utf8',errors='replace'))
  links=[urljoin(url,u) for u in parser.hrefs]
  interesting=[u for u in links if any(s in u.lower() for s in ['xbrl','.xml','2025','financial','quarterly'])]
  record={'url':url,'file':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'status':'downloaded','retrieved_on':'2026-10-22','links':interesting}
 except Exception as exc:record={'url':url,'file':name,'status':'failed','error':str(exc)}
 return record
jobs=[('kira_infosys_discovery.html','https://www.kirainvestors.com/research/infosys/'),('aether_rendered.html','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_127119_13112025150257_iXBRL_WEB.html'),('aether_investor_relations.html','https://aether.co.in/investor-relations/')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,jobs))
(root/'discovery_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
for r in records:
 out={k:v for k,v in r.items() if k!='links'}
 out['links']=r.get('links',[])[:45]
 print(json.dumps(out,ensure_ascii=True))
