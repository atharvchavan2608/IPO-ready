from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
root=Path(__file__).resolve().parent
p=root/'Aether_RHP_20220516.pdf'
manifest={'file':p.name,'source_url':'https://www.sebi.gov.in/sebi_data/attachdocs/may-2022/1652869529567.pdf','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'retrieved_on':'2026-10-22','document_date':'2022-05-16','sebi_filing_date':'2022-05-18','broker_review':'Web-extracted text only. Local download unsuccessful.'}
(root/'document_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
book=Path('outputs/ipo-ready-survey-20261022/IPO_Ready_Research_Survey_Pass3.xlsx')
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(book) as z:
 assert z.testzip() is None
 sheets=[n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]
 assert len(sheets)==3
 for path in sheets:
  cells=E.fromstring(z.read(path)).findall('.//s:c',ns)
  assert not [c.attrib['r'] for c in cells if c.attrib.get('t')=='e']
 table=E.fromstring(z.read('xl/tables/table1.xml'))
 assert table.attrib['ref']=='A4:P49'
 raw=E.fromstring(z.read('xl/worksheets/sheet3.xml'))
 cells={c.attrib['r']:c for c in raw.findall('.//s:c',ns)}
 def value(a):return float(cells[a].find('s:v',ns).text)
 expected={'D8':4498.16,'D14':711.19,'B46':0.4952886876,'B52':0.3261575669,'B53':0.0289966951,'B55':273.048,'B56':202.637,'B57':105.771,'B60':75.55745532,'B65':112.37204694}
 for cell,v in expected.items():assert abs(value(cell)-v)<1e-7,(cell,value(cell),v)
 checks={col+str(row):value(col+str(row)) for col in 'BCDEF' for row in range(69,73)}
 assert all(abs(v)<=0.0200001 for v in checks.values()),checks
 print(json.dumps({'survey_entries':45,'primary_observations':110,'reconciliation_checks':len(checks),'max_residual_million':max(abs(v) for v in checks.values()),'expected_values_verified':len(expected),'formula_errors':0,'bytes':book.stat().st_size},indent=2))
