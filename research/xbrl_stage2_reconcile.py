"""Recompute manually observed PDF versus web-rendered filing comparisons.

Not an XML parser or validation test. PDF values visually checked on numbered
physical pages; NSE values transcribed from primary web-tool text on 2026-10-22.
"""
from pathlib import Path
from decimal import Decimal as D
import json

root=Path('research/xbrl_stage2_20261022')
# label, PDF physical page, period, PDF INR million, NSE INR lakh, interpretation
rows=[
 ('Revenue from operations',20,'quarter','2247.20','22472.00','same label'),
 ('Other income',20,'quarter','96.67','966.70','same label'),
 ('Total income',20,'quarter','2343.87','23438.70','same label'),
 ('Finance costs',20,'quarter','18.10','181.00','same label'),
 ('Depreciation and amortisation',20,'quarter','152.71','1527.10','same label'),
 ('Profit before tax',20,'quarter','615.04','6150.40','same label'),
 ('PAT',20,'quarter','435.72','4357.20','same label'),
 ('Revenue from operations',20,'half-year','4390.54','43905.40','same label'),
 ('PAT',20,'half-year','837.15','8371.50','same label'),
 ('Total assets',24,'instant','27499.04','274990.40','same label'),
 ('Cash and cash equivalents, balance sheet',24,'instant','33.40','334.00','same label'),
 ('Current borrowings',26,'instant','1479.18','14791.80','same label'),
 ('Operating cash flow',28,'half-year','1306.13','13061.30','same label'),
 ('Investing cash flow',28,'half-year','-3461.00','-34610.00','same label'),
 ('Financing cash flow',28,'half-year','331.34','3313.40','same label'),
 ('Cash flow closing balance',28,'instant','561.72','5617.20','same label; broader than balance-sheet cash'),
 ('Quarter total expenses',20,'quarter','1702.41','17020.40','numeric conflict'),
 ('Quarter other expenses',20,'quarter','300.15','3001.40','numeric conflict'),
 ('Half-year tax expense',20,'half-year','309.38','3093.90','numeric conflict'),
 ('Capital work in progress',24,'instant','5290.27','57374.00','numeric/classification conflict'),
 ('Intangible assets',24,'instant','8.27','16913.60','numeric/classification conflict'),
 ('Non-current lease liabilities / NSE non-current borrowings',24,'instant','143.96','1439.60','equal number; different label'),
 ('Deferred tax liabilities / NSE other non-current liabilities',24,'instant','583.35','5833.40','different label and number'),
 ('Cash generated from operations',28,'half-year','1530.97','15681.40','numeric/classification conflict'),
 ('PPE purchases, signed / NSE purchase amount unsigned',28,'half-year','-1003.78','5566.50','sign convention and amount differ'),
 ('Investment income / NSE dividends received',28,'half-year','37.17','371.70','equal number; label not established equivalent'),
]
records=[]
for label,page,period,pdf,nse,note in rows:
 converted=D(pdf)*10;delta=D(nse)-converted
 records.append(dict(label=label,pdf_page=page,period=period,pdf_raw_million=pdf,nse_raw_lakh=nse,pdf_converted_lakh=str(converted),nse_minus_pdf_lakh=str(delta),interpretation=note))
(root/'reconciliation.json').write_text(json.dumps(records,indent=2),encoding='utf8')
table=['| Observation | PDF page | Period | PDF million | NSE lakh | NSE minus PDF, lakh | Review |','|---|---:|---|---:|---:|---:|---|']
for r in records:table.append('| '+ ' | '.join(str(r[k]) for k in ['label','pdf_page','period','pdf_raw_million','nse_raw_lakh','nse_minus_pdf_lakh','interpretation'])+' |')
(root/'comparison-table.md').write_text('\n'.join(table)+'\n',encoding='utf8')
print(json.dumps({'observations':len(records),'same_label_exact_matches':sum(r['interpretation'].startswith('same label') and D(r['nse_minus_pdf_lakh'])==0 for r in records),'important_limit':'manual transcription; no raw XML acquired'},indent=2))
