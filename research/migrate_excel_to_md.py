"""One-time migration of the final Excel research snapshot. No spreadsheet writes."""
from pathlib import Path
from datetime import datetime,timedelta
import zipfile,xml.etree.ElementTree as E,hashlib,re

book=Path('outputs/ipo-ready-survey-20261022/IPO_Ready_Research_Survey_Pass3.xlsx')
dest=Path('docs/research')
assert not (dest/'sources/INDEX.md').exists(),'Migration already completed. Edit canonical Markdown directly.'
(dest/'sources').mkdir(parents=True,exist_ok=True)
(dest/'pilots').mkdir(exist_ok=True)
(dest/'decisions').mkdir(exist_ok=True)
(dest/'topics').mkdir(exist_ok=True)
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def md(v):return str(v if v is not None else '').replace('|','\\|').replace('\n',' ')
def table(headers,rows):return '\n'.join(['| '+' | '.join(map(md,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(md,r))+' |' for r in rows])+'\n'
def write(name,text):
 p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n',encoding='utf8')

with zipfile.ZipFile(book) as z:
 strings=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  for s in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns):strings.append(''.join(x.text or '' for x in s.findall('.//s:t',ns)))
 def sheet(n):
  cells={};formulas={}
  for c in E.fromstring(z.read(f'xl/worksheets/sheet{n}.xml')).findall('.//s:c',ns):
   address=c.attrib['r'];v=c.find('s:v',ns);t=c.attrib.get('t');value=v.text if v is not None else ''
   if t=='s':value=strings[int(value)]
   elif t=='inlineStr':value=''.join(x.text or '' for x in c.findall('.//s:t',ns))
   elif t=='d':value=value[:10]
   elif value and t not in ('str','e'):
    value=float(value);value=int(value) if value.is_integer() else value
   cells[address]=value
   f=c.find('s:f',ns)
   if f is not None:formulas[address]='='+f.text
  return cells,formulas
 findings,_=sheet(1);survey,_=sheet(2);pilot,formulas=sheet(3)
 records=[]
 fields=[('D','Authors / publisher / citation'),('E','Publication year'),('F','Market / task'),('G','Observed finding'),('H','Review basis / method'),('I','Learning / interpretation'),('J','Potential project use'),('K','Limitations / transfer risks'),('L','Access / reuse'),('M','Review depth'),('N','Next investigation')]
 for row in range(5,50):
  record_id=survey[f'A{row}'];title=survey[f'C{row}'];typ=survey[f'B{row}'];url=survey[f'O{row}'];checked=survey[f'P{row}']
  if isinstance(checked,(int,float)):checked=(datetime(1899,12,30)+timedelta(days=checked)).strftime('%Y-%m-%d')
  text=f'# {record_id}: {title}\n\n- ID: {record_id}\n- Type: {typ}\n- Checked on: {checked}\n- Source: [{title}]({url})\n- Migrated from: Survey log!A{row}:P{row}\n'
  for col,label in fields:
   value=survey.get(f'{col}{row}','')
   if col=='E' and not value:value='Not established'
   text+=f'\n## {label}\n\n{value}\n'
  write(f'sources/{record_id}.md',text)
  records.append([f'[{record_id}]({record_id}.md)',typ,title,survey[f'M{row}'],checked])
 assert len(records)==45
 write('sources/INDEX.md','# Source and audit register\n\nOriginal 45 records migrated without dropping fields. An audit record can reference the same underlying source as another record. Count records separately from unique sources.\n\n'+table(['ID','Type','Title','Review depth','Checked'],records))
 decisionrows=[[findings.get(f'{c}{r}','') for c in 'ABCDEF'] for r in range(7,15)]
 queue=[[findings.get(f'{c}{r}','') for c in 'ABCDEF'] for r in range(18,23)]
 write('findings.md','# Research findings\n\nAs of 2026-10-22. These are working conclusions, not frozen product requirements. Source IDs resolve through [the register](sources/INDEX.md).\n\n'+table(['Area','Working conclusion','Evidence','Reason','Next investigation','State'],decisionrows)+'\n## Prior queue at migration\n\n'+table(['Sequence','Research pass','Output','Evidence','Completion criterion','State'],queue)+'\n## Migration notes\n\n'+'\n\n'.join(str(findings.get(f'B{r}','')) for r in range(25,29)))
 raw=[[pilot.get(f'{c}{r}','') for c in 'ABCDEFGHIJKL'] for r in range(8,30)]
 metrics=[]
 for r in range(46,66):
  metrics.append([pilot.get(f'A{r}',''),pilot.get(f'B{r}',''),pilot.get(f'C{r}',''),f'`{formulas[f"B{r}"]}`' if f'B{r}' in formulas else 'Source input',pilot.get(f'D{r}','')])
 comps=[]
 for r in range(34,42):comps.append([pilot.get(f'{c}{r}','') for c in 'ABCDEFGH'])
 checks=[]
 for r in range(69,73):checks.append([pilot[f'A{r}']]+[pilot.get(f'{c}{r}','') for c in 'BCDEF'])
 write('pilots/aether-ipo-2022.md','# Aether: retrospective IPO financial reconciliation\n\n- Assessment reconstructed on: 2026-10-22\n- RHP document date: 2022-05-16\n- SEBI filing date: 2022-05-18\n- Original evidence: [document manifest](../../../research/aether_reconciliation/document_manifest.json) and [RHP PDF](../../../research/aether_reconciliation/Aether_RHP_20220516.pdf)\n- Historical availability: original price-band advertisement and exact post-offer share mechanics remain unresolved.\n- Broker evidence: extracted web text only; local broker download and visual verification did not complete.\n- Status: hand-transcribed pilot, not a fully adjudicated benchmark.\n\n## Reported observations\n\n110 numeric observations. Monetary amounts retain INR million; EPS retains INR per share. Balance-sheet amounts are as at the period end. PDF page means physical page; printed page means footer numbering.\n\n'+table(['Metric','9M Dec-2021','9M Dec-2020','FY Mar-2021','FY Mar-2020','FY Mar-2019','Unit','PDF page','Printed page','Basis','Review note','URL'],raw)+'\n## Broker comparisons\n\nDifference is broker minus primary calculation. The loan/lease bridge is an inference; the asset presentation is not like-for-like.\n\n'+table(['Measure','RHP / derived','Broker','Difference','Unit','Broker page','Interpretation','URL'],comps)+'\n## Derived measures\n\nFormula strings below preserve the archived workbook coordinates for audit. They are not executable Markdown formulas. The raw observations and definitions above are the ongoing canonical facts.\n\n'+table(['Measure','Cached result','Unit','Archived workbook formula','Definition / limitation'],metrics)+'\n## Reconciliation residuals\n\nINR million. Absolute tolerance 0.02. All 20 residuals pass within source rounding; this checks arithmetic, not economic correctness.\n\n'+table(['Check','9M Dec-2021','9M Dec-2020','FY21','FY20','FY19'],checks)+'\n## Open review items\n\n'+'\n\n'.join(str(pilot.get(f'A{r}','')) for r in range(75,79)))

sha=hashlib.sha256(book.read_bytes()).hexdigest()
write('migration.md',f'''# Excel-to-Markdown migration

- Completed: 2026-10-22
- Source snapshot: [{book.name}](../../{book.as_posix()})
- Source SHA-256: `{sha}`
- Migrated: 45 survey records, all 16 columns, eight findings, five queue items, existing usage notes, 110 primary pilot observations, eight broker comparisons, 20 derived/input measures and 20 reconciliation residuals.
- IDs are unchanged. Repeated underlying URLs were not collapsed because paper, code and published-data reviews have different evidence scope.
- Publication years and review dates were preserved. Blank years are explicitly not established.
- Formulas and cached results are preserved as audit references. Markdown does not recalculate them.
- The workbook and its builder are historical snapshots. Future research edits belong in Markdown. Do not rerun old builders over canonical notes.
- Native PDF/XML/HTML, downloaded third-party source snapshots and small reproducibility scripts remain in `research/` as evidence, not as the canonical research narrative.

The stage-1 XBRL research is added after this migration and was not part of the Excel source.
''')
print('Migrated 45 records and all pilot sections to',dest)
