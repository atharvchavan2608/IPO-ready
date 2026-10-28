"""Small read-only sample for XBRL research. Does not crawl exchange APIs."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,re,zipfile,io
from html import unescape
def links(text):return [unescape(m) for m in re.findall(r'<a\b[^>]*href=[\"\']([^\"\']+)',text,re.I)]

root=Path('research/xbrl_stage1_20261022');root.mkdir(parents=True,exist_ok=True)
records=[]
def fetch(url,name):
 try:
  with urllib.request.urlopen(url,timeout=35) as r: data=r.read()
  (root/name).parent.mkdir(parents=True,exist_ok=True);(root/name).write_bytes(data)
  records.append({'url':url,'file':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'retrieved_on':'2026-10-22','status':'downloaded'})
  return data
 except Exception as exc:
  records.append({'url':url,'file':name,'status':'failed','reason':str(exc)});print('FAILED',url,str(exc));return None

aether='https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_127119_13112025150257_iXBRL_WEB.html'
html=fetch(aether,'aether_20250930_rendered.html')
if html:
 text=html.decode('utf8',errors='replace')
 print('Aether HTML inspection:',json.dumps({'ix_nonfraction':len(re.findall(r'<(?:\w+:)?nonfraction\b',text,re.I)),'context_elements':len(re.findall(r'<(?:\w+:)?context\b',text,re.I)),'tables':len(re.findall(r'<table\b',text,re.I)),'xml_links':[a for a in links(text) if '.xml' in a.lower()]}))
page=fetch('https://www.nseindia.com/static/companies-listing/xbrl-information','nse_xbrl_information.html')
if page:
 for tr in re.findall(r'<tr\b.*?</tr>',page.decode('utf8',errors='replace'),re.I|re.S):
  text=unescape(re.sub(r'<[^>]+>',' ',tr))
  if 'Financial Results - Ind AS' in text or 'Financial Results – Ind AS' in text:
   download_links=[urllib.parse.urljoin('https://www.nseindia.com',a) for a in links(tr)]
   print('NSE IndAS download links:',json.dumps(download_links))
   for i,url in enumerate(download_links):
    data=fetch(url,f'official_package_{i}.zip')
    if data and zipfile.is_zipfile(io.BytesIO(data)):
     z=zipfile.ZipFile(io.BytesIO(data))
     listing=[{'name':n,'bytes':z.getinfo(n).file_size} for n in z.namelist()]
     (root/f'official_package_{i}_contents.json').write_text(json.dumps(listing,indent=2),encoding='utf8')
     print('Package',i,listing[:12])
for repo in ['ShantanuAnant/nse-xbrl','dhananjaym182/india-xbrl-filings']:
 name=repo.split('/')[1]
 raw=fetch(f'https://api.github.com/repos/{repo}/git/trees/main?recursive=1',f'{name}_tree.json')
 if not raw:continue
 tree=json.loads(raw);sha=tree['sha'];paths=[x['path'] for x in tree['tree']]
 print('Repository:',repo,'SHA:',sha,'candidate files:',[p for p in paths if p.endswith(('.xml','.py','.xsd'))][:35])
 for path in ['README.md','LICENSE']:
  fetch(f'https://raw.githubusercontent.com/{repo}/{sha}/{path}',f'{name}/{path}')
(root/'download_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
