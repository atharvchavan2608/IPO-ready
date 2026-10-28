"""Inspect an archived filing copy without fetching schemas or executing repo code.

This is bounded XML evidence inspection, not an XBRL-conformant processor.
Official PDF comparison values manually transcribed from physical page 13.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter,defaultdict
import xml.etree.ElementTree as E
import json,hashlib
root=Path('research/xbrl_stage2_20261022')
path=root/'infosys_fy24_repository_copy.xml'
data=path.read_bytes()
assert b'<!DOCTYPE' not in data and b'<!ENTITY' not in data
ns=dict(item for _,item in E.iterparse(path,events=['start-ns']))
x=E.fromstring(data)
X='{http://www.xbrl.org/2003/instance}';DI='{http://xbrl.org/2006/xbrldi}'
contexts={}
for c in x.findall(X+'context'):
 ident=c.find('.//'+X+'identifier');p=c.find(X+'period')
 contexts[c.get('id')]={'entity':ident.text,'scheme':ident.get('scheme'),'period':{e.tag.removeprefix(X):e.text for e in p},'dimensions':[dict(kind=e.tag.removeprefix(DI),attributes=e.attrib,xml=E.tostring(e,encoding='unicode')) for e in c.iter() if e.tag in (DI+'explicitMember',DI+'typedMember')]}
units={u.get('id'):E.tostring(u,encoding='unicode') for u in x.findall(X+'unit')}
facts=[dict(qname=e.tag,context_id=e.get('contextRef'),unit_id=e.get('unitRef'),decimals=e.get('decimals'),nil=e.get('{http://www.w3.org/2001/XMLSchema-instance}nil'),raw_text=''.join(e.itertext()),attributes=e.attrib) for e in x if e.get('contextRef')]
inventory={'sha256':hashlib.sha256(data).hexdigest(),'namespaces':ns,'schema_refs':[e.get('{http://www.w3.org/1999/xlink}href') for e in x.findall('{http://www.xbrl.org/2003/linkbase}schemaRef')],'contexts':contexts,'units':units,'facts':facts}
(root/'infosys_inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf8')
local=lambda f:f['qname'].split('}')[-1]
def one(concept,context):
 matches=[f for f in facts if local(f)==concept and f['context_id']==context]
 assert len(matches)==1,(concept,context,len(matches))
 return matches[0]
checks=[]
for cid,expected_start,values in [
 ('OneD','2024-01-01',{'RevenueFromOperations':'37923','OtherIncome':'2729','Income':'40652','Expenses':'30412','ProfitBeforeTax':'10240','ProfitLossForPeriod':'7975','ProfitOrLossAttributableToOwnersOfParent':'7969','DilutedEarningsLossPerShareFromContinuingOperations':'19.22'}),
 ('FourD','2023-04-01',{'RevenueFromOperations':'153670','OtherIncome':'4711','Income':'158381','Expenses':'122393','ProfitBeforeTax':'35988','ProfitLossForPeriod':'26248','ProfitOrLossAttributableToOwnersOfParent':'26233','DilutedEarningsLossPerShareFromContinuingOperations':'63.29'})]:
 for concept,pdf in values.items():
  f=one(concept,cid);divisor=Decimal(10_000_000) if f['unit_id']=='INR' else Decimal(1)
  number=Decimal(f['raw_text'])/divisor
  explicit_start=one('DateOfStartOfReportingPeriod',cid)['raw_text']
  checks.append({'concept_qname':f['qname'],'context_id':cid,'context_period':contexts[cid]['period'],'explicit_reporting_start':explicit_start,'expected_pdf_start':expected_start,'pdf_page':13,'pdf_value':pdf,'pdf_unit':'INR crore' if divisor!=1 else 'INR/share','xml_raw':f['raw_text'],'unit_ref':f['unit_id'],'decimals':f['decimals'],'normalized_xml':str(number),'number_matches':number==Decimal(pdf),'context_period_matches':contexts[cid]['period'].get('startDate')==expected_start})
(root/'infosys_comparison.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
groups=defaultdict(list)
for f in facts:
 c=contexts[f['context_id']]
 key=(f['qname'],json.dumps(c,sort_keys=True),f['unit_id'])
 groups[key].append(f)
conflicts=[{'concept_qname':k[0],'facts':v} for k,v in groups.items() if len({f['raw_text'] for f in v})>1]
(root/'infosys_same_aspect_conflicts.json').write_text(json.dumps(conflicts,indent=2),encoding='utf8')
summary={'facts':len(facts),'contexts':len(contexts),'units':len(units),'contexts_with_dimensions':sum(bool(c['dimensions']) for c in contexts.values()),'nil_facts':sum(f['nil'] in ('true','1') for f in facts),'comparison_rows':len(checks),'numeric_matches':sum(c['number_matches'] for c in checks),'period_matches':sum(c['context_period_matches'] for c in checks),'differing_value_groups_under_same_inspected_aspects':len(conflicts),'schema_refs':inventory['schema_refs']}
(root/'infosys_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
table=['| Concept (namespace `in-bse-fin`) | Context | Raw XML | Unit | Decimals | PDF p.13 | Numeric match | Context period match |','|---|---|---:|---|---|---:|---|---|']
for c in checks:table.append('| '+' | '.join(str(v) for v in [c['concept_qname'].split('}')[-1],c['context_id'],c['xml_raw'],c['unit_ref'],c['decimals'],c['pdf_value'],c['number_matches'],c['context_period_matches']])+' |')
(root/'infosys_comparison.md').write_text('\n'.join(table)+'\n',encoding='utf8')
print(json.dumps(summary,indent=2))
