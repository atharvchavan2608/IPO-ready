"""Check migration completeness, local links and fixture inventory; no financial-model validation."""
from pathlib import Path
import re,zipfile,xml.etree.ElementTree as E,json
root=Path('.').resolve();docs=root/'docs/research'
source_files=sorted((docs/'sources').glob('*.md'))
ids=[p.stem for p in source_files if p.stem!='INDEX']
assert len(ids)==64 and len(set(ids))==64
register=(docs/'sources/INDEX.md').read_text(encoding='utf8')
for i in ids:assert f'[{i}]({i}.md)' in register,i
broken=[]
for path in [root/'README.md']+list(docs.rglob('*.md')):
 for url in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf8')):
  if re.match(r'^[a-zA-Z]+://',url) or url.startswith('#'):continue
  target=url.split('#')[0]
  if not (path.parent/target).resolve().exists():broken.append((str(path),url))
assert not broken,broken
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
book=root/'outputs/ipo-ready-survey-20261022/IPO_Ready_Research_Survey_Pass3.xlsx'
with zipfile.ZipFile(book) as z:
 ss=[]
 for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns):ss.append(''.join(t.text or '' for t in si.findall('.//s:t',ns)))
 cells={}
 for c in E.fromstring(z.read('xl/worksheets/sheet2.xml')).findall('.//s:c',ns):
  v=c.find('s:v',ns);value=v.text if v is not None else ''
  if c.get('t')=='s':value=ss[int(value)]
  if c.get('t')=='d':value=value[:10]
  cells[c.get('r')]=value
 field_checks=0
 for row in range(5,50):
  record=(docs/'sources'/f'{cells[f"A{row}"]}.md').read_text(encoding='utf8')
  for col in 'ABCDEFGHIJKLMNOP':
   value=cells.get(f'{col}{row}','')
   if value:
    assert value in record,(row,col,value)
    field_checks+=1
 xns={'x':'http://www.xbrl.org/2003/instance'}
 fixtures=[]
 for path in [root/'research/xbrl_stage1_20261022/nse-xbrl/tests/fixtures/sample_filing.xml',root/'research/xbrl_stage1_20261022/india-xbrl-filings/tests/fixtures/in-capmkt/sample_integrated_2025.xml']:
  x=E.fromstring(path.read_bytes());fixtures.append({'file':str(path.relative_to(root)),'contexts':[c.get('id') for c in x.findall('x:context',xns)],'units':len(x.findall('x:unit',xns)),'facts':sum(bool(el.get('contextRef')) for el in x)})
print(json.dumps({'source_records':len(ids),'migrated_nonempty_cell_checks':field_checks,'broken_local_links':len(broken),'fixture_inventory':fixtures},indent=2))
