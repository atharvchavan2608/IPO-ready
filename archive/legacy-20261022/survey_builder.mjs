import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const runtimeRequire=createRequire('C:/Users/chava/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {Workbook, SpreadsheetFile, FileBlob}=await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);

if(process.argv.includes('--pass3') || process.argv.includes('--pilot-preview')) {
  const book=await SpreadsheetFile.importXlsx(await FileBlob.load('outputs/ipo-ready-survey-20261022/IPO_Ready_Research_Survey_Pass2.xlsx'));
  const dest='outputs/ipo-ready-survey-20261022';
  if(process.argv.includes('--pilot-preview')) {
    console.log((await book.inspect({kind:'region',sheetId:'Findings',range:'A7:F11',maxChars:1200,tableMaxRows:2,tableMaxCols:3})).ndjson);
    const p=await book.render({sheetName:'Findings',range:'A1:F14',scale:1,format:'png'});
    await fs.writeFile(`${dest}/before_pass3.png`,new Uint8Array(await p.arrayBuffer()));
    process.exit(0);
  }
  const data=JSON.parse(await fs.readFile('research/aether_reconciliation/pilot_data.json','utf8'));
  const log=book.worksheets.getItem('Survey log');
  const findings=book.worksheets.getItem('Findings');
  log.tables.items[0].rows.add(null,data.survey.map(r=>[...r,new Date('2026-10-22T00:00:00Z')]));
  log.getRange('A44:P49').copyFrom(log.getRange('A35:P40'),'all');
  log.getRange('A44:P49').values=data.survey.map(r=>[...r,new Date('2026-10-22T00:00:00Z')]);
  log.getRange('A44:P49').format.rowHeight=105;
  log.getRange('P44:P49').setNumberFormat('dd mmm yyyy');
  findings.getRange('A2').values=[['IPO-Ready: research findings, pass 3']];
  findings.getRange('D4').values=[[45]];
  findings.getRange('F4').values=[['Pilot reconciliation']];
  findings.getRange('B7:F7').values=[['Build a verified financial dataset before automating reports. First pilot: 22 Aether metrics across five periods.','B01–B06; Aether pilot','Real disclosures confirm definition and period issues. Broker summaries are useful secondary checks, with unresolved differences preserved.','Repeat the same dictionary on a second issuer and review the comparison rules.','Pilot populated']];
  findings.getRange('B10:F10').values=[['Use dated offer inputs and explicitly tagged EPS. Aether weighted EPS is not FY21 EPS.','B05; Aether pilot','RHP peers use May 4 prices and FY21 earnings, with mixed statement bases. The broker TTM P/E bridge is reproducible approximately.','Find original price-band advertisement and reconcile the broker share-count references.','Partially reconciled']];
  findings.getRange('B11:F11').values=[['Preserve operating revenue, total income and issuer EBITDA definitions as separate fields.','B02–B04; Aether pilot','FY21 operating revenue 449.816 crore differs from total income 453.789 crore. EBITDA explicitly subtracts other income.','Apply definition checks to every issuer before comparing ratios.','Primary figures verified']];
  findings.getRange('B19:F19').values=[['Aether primary-document pilot','22 metrics, five periods and formula comparisons','B01–B06; Aether pilot','Selected primary tables reviewed. Broker text compared. Offer-price source and some broker denominators remain unresolved.','Partial: primary tables checked']];
  findings.getRange('B25').values=[['Pass 3 adds a primary-document pilot. Source figures, formulas, broker rounding and unresolved differences are separate. The broker PDF was reviewed as extracted web text.']];
  findings.getRange('B28').values=[['Next: verify price-band and share-count evidence, inspect the repeated-asset discrepancy, then repeat the field dictionary on another issuer. Core finance-paper deep reading remains pending.']];
  const s=book.worksheets.add('Aether pilot');
  base(s,'A1:L80');s.tabColor='#607D8B';
  s.getRange('A2').values=[['Aether: historical financial reconciliation']];
  s.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
  s.getRange('A4:L4').merge();s.getRange('A4').values=[['Retrospective reconstruction on 22 Oct 2026. RHP dated 16 May 2022. Figures retain their source units. EPS is per share.']];
  s.getRange('A5:L5').merge();s.getRange('A5').values=[['Period labels apply to flows; balance-sheet figures are as at each period end. PDF page is physical page; printed page follows the document footer.']];
  s.getRange('A4:L5').format.wrapText=true;s.getRange('A4:L5').format.rowHeight=28;
  s.getRange('A7:L7').values=[['Reported metric','9M Dec-2021','9M Dec-2020','FY Mar-2021','FY Mar-2020','FY Mar-2019','Source unit','PDF page','Printed page','Statement / measure basis','Definition / review note','Primary source URL']];header(s,'A7:L7');
  s.getRange('A8:L29').values=data.raw.map(r=>[...r,data.rhp_url]);
  s.getRange('A8:L29').format.wrapText=true;s.getRange('A8:L29').format.rowHeight=48;
  s.getRange('B8:F29').setNumberFormat('#,##0.00;(#,##0.00);"-"');
  s.getRange('B8:F29').format.font.color='#0000FF';
  s.getRange('H8:I29').setNumberFormat('0');
  for(let n=8;n<=29;n++)if(n%2===0)s.getRange(`A${n}:L${n}`).format.fill='#F0F4F8';
  const cols=[43,18,18,18,18,18,20,12,13,31,61,72];
  cols.forEach((w,i)=>s.getRangeByIndexes(0,i,78,1).format.columnWidth=w);
  s.freezePanes.freezeRows(7);s.freezePanes.freezeColumns(1);
  s.getRange('A31:L31').merge();s.getRange('A31').values=[['FY21 broker comparison. INR crore = INR million / 10. Broker data below is text-reviewed, not visually verified. Difference = broker minus primary calculation.']];s.getRange('A31:L31').format.wrapText=true;s.getRange('A31:L31').format.rowHeight=28;
  s.getRange('A33:H33').values=[['Comparable measure','RHP / derived','Broker reported','Difference','Unit','Broker page','Interpretation','Broker source URL']];header(s,'A33:H33');
  const comps=[
    ['Operating revenue','=D8/10',450,'INR crore',3,'Matches whole-crore rounding.'],
    ['PAT','=D14/10',71,'INR crore',3,'Matches whole-crore rounding.'],
    ['EBITDA excluding other income','=D15/10',112,'INR crore',3,'Matches whole-crore rounding.'],
    ['CFO','=D16/10',23,'INR crore',5,'Matches whole-crore rounding.'],
    ['Total equity','=D20/10',174,'INR crore',4,'Matches whole-crore rounding.'],
    ['Total assets, statement basis','=D21/10',386,'INR crore',4,'Different presentation: broker balance sheet uses net current assets. Do not equate its total with gross statement assets.'],
    ['Debt excluding leases','=D19/10',211,'INR crore',4,'Does not match rounding of borrowings alone.'],
    ['Borrowings plus lease liabilities','=(D19+D28+D29)/10',211,'INR crore',4,'Numerically consistent with broker total loans after rounding; treatment inferred, not confirmed.']
  ];
  comps.forEach((r,i)=>{const n=34+i;s.getRange(`A${n}:H${n}`).values=[[r[0],null,r[2],null,r[3],r[4],r[5],data.broker_url]];s.getRange(`B${n}`).formulas=[[r[1]]];s.getRange(`D${n}`).formulas=[['=C'+n+'-B'+n]];});
  s.getRange('A34:H41').format.wrapText=true;s.getRange('A34:H41').format.rowHeight=60;s.getRange('G34:G41').format.columnWidth=55;s.getRange('H34:H41').format.columnWidth=25;
  s.getRange('B34:D41').setNumberFormat('#,##0.000;(#,##0.000);0.000');s.getRange('C34:C41').format.font.color='#0000FF';
  s.getRange('D34:D41').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0.5,format:{fill:'#FDE8E8',font:{color:'#A61B1B'}}});
  s.getRange('D34:D41').conditionalFormats.add('cellIs',{operator:'lessThan',formula:-0.5,format:{fill:'#FDE8E8',font:{color:'#A61B1B'}}});
  s.getRange('A43:L43').merge();s.getRange('A43').values=[['Derived measures and valuation bridges. Broker-sourced price/share assumptions remain secondary inputs pending original offer-document verification.']];s.getRange('A43:L43').format.wrapText=true;s.getRange('A43:L43').format.rowHeight=28;
  s.getRange('A45:D45').values=[['Measure','Calculated / input','Unit','Definition or limitation']];header(s,'A45:D45');
  const metrics=[
    ['Operating revenue CAGR, FY19–21','=(D8/F8)^(1/2)-1','rate','Two elapsed fiscal years.'],
    ['PAT CAGR, FY19–21','=(D14/F14)^(1/2)-1','rate','Positive annual endpoints; no forecast implied.'],
    ['Operating revenue growth, 9M YoY','=B8/C8-1','rate','Like-for-like nine-month periods.'],
    ['EBITDA margin, FY21','=D15/D8','rate','Issuer EBITDA / operating revenue.'],
    ['PAT margin on total income, FY21','=D14/D10','rate','Issuer denominator convention.'],
    ['PAT margin on operating revenue, FY21','=D14/D8','rate','Alternative explicitly labelled denominator.'],
    ['CFO/PAT, FY21','=D16/D14','multiple','Cash flow after tax divided by PAT.'],
    ['CFO/PAT, 9M Dec-2021','=B16/B14','multiple','Interim ratio, not annualised.'],
    ['Debt/equity, FY21','=D19/D20','multiple','Borrowings excluding lease liabilities / equity.'],
    ['Issuer net debt, FY21','=(D22-D23)/10','INR crore','Issuer definition: total liabilities less cash/bank balances.'],
    ['Borrowings less cash/banks, FY21','=(D19-D23)/10','INR crore','Alternative bridge. Includes reported bank balances without assessing restrictions.'],
    ['TTM PAT to Dec-2021','=(D14+B14-C14)/10','INR crore','FY21 + 9M Dec-2021 - 9M Dec-2020.'],
    ['Illustrative post-offer shares',124482673,'shares','Broker p2. Secondary input; original price-band/offer share count not reconciled.'],
    ['Illustrative offer cap price',642,'INR/share','Broker p1. RHP leaves price band blank.'],
    ['TTM P/E on these offer shares','=B59*B58/(B57*10000000)','multiple','Approximately reproduces broker narrative 75.6x. Does not validate its recommendation.'],
    ['Restated FY21 EPS','=D27','INR/share','RHP annual EPS, adjusted historical weighted share basis.'],
    ['Reported three-year weighted EPS',5.51,'INR/share','RHP PDF p109, printed p106. Not current annual or TTM EPS.'],
    ['Price / weighted three-year EPS','=B59/B62','multiple','Illustration of denominator sensitivity, not an adopted valuation metric.'],
    ['FY21 PAT / post-offer shares','=D14*1000000/B58','INR/share','Illustrative annual PAT divided by broker post-offer shares.'],
    ['FY21 P/E on post-offer shares','=B59/B64','multiple','Differs from broker annual table 101.7x. Broker denominator still unresolved.']
  ];
  metrics.forEach((r,i)=>{const n=46+i;s.getRange(`A${n}:D${n}`).values=[[r[0],typeof r[1]==='number'?r[1]:null,r[2],r[3]]];if(typeof r[1]==='string')s.getRange(`B${n}`).formulas=[[r[1]]];else s.getRange(`B${n}`).format.font.color='#0000FF';s.getRange(`B${n}`).setNumberFormat(r[2]==='rate'?'0.00%':r[2]==='shares'?'#,##0':'0.000');s.getRange(`D${n}:F${n}`).merge();s.getRange(`D${n}:F${n}`).format.wrapText=true;});
  s.getRange('A46:L65').format.rowHeight=48;s.getRange('A46:A65').format.wrapText=true;
  s.getRange('A68:F68').values=[['Primary reconciliation residual (INR million)','9M Dec-2021','9M Dec-2020','FY21','FY20','FY19']];header(s,'A68:F68');
  const checks=[['Operating revenue + other - total',8,9,10],['EBITDA bridge residual'],['Borrowings components - debt'],['Equity + liabilities - assets']];
  for(let i=0;i<checks.length;i++){const n=69+i;s.getRange(`A${n}`).values=[[checks[i][0]]];for(const col of ['B','C','D','E','F']){const f=i===0?`=${col}8+${col}9-${col}10`:i===1?`=${col}11+${col}12+${col}13-${col}9-${col}15`:i===2?`=${col}17+${col}18-${col}19`:`=${col}20+${col}22-${col}21`;s.getRange(`${col}${n}`).formulas=[[f]];}}
  s.getRange('A69:F72').format.rowHeight=28;s.getRange('B69:F72').setNumberFormat('0.00;(0.00);0.00');
  s.getRange('B69:F72').conditionalFormats.addCustom('ABS(B69)>0.02',{fill:'#FDE8E8',font:{color:'#A61B1B'}});
  const notes=[
    'Residual tolerance: 0.02 million for source rounding. These checks test internal arithmetic, not whether the source financials are economically correct.',
    'Open discrepancy: Dec-2020 assets 4000.95 million on PDF p64 versus 4009.95 on p303. Statement value retained; cause and any corrigendum unverified.',
    'Peer basis: RHP PDF p111 uses FY21 EPS with NSE prices at 4 May 2022. Clean Science is standalone; the other four peers are consolidated.',
    'Broker EPS/capital references remain unresolved. Original price-band advertisement and exact post-offer share mechanics need checking before publishing a valuation.'
  ];
  notes.forEach((t,i)=>{const n=75+i;s.getRange(`A${n}:L${n}`).merge();s.getRange(`A${n}`).values=[[t]];s.getRange(`A${n}:L${n}`).format.wrapText=true;s.getRange(`A${n}:L${n}`).format.rowHeight=30;});
  book.recalculate();
  console.log((await book.inspect({kind:'region',sheetId:'Aether pilot',range:'A46:C65',maxChars:4000,tableMaxRows:20,tableMaxCols:3})).ndjson);
  const output=await SpreadsheetFile.exportXlsx(book);await output.save(`${dest}/IPO_Ready_Research_Survey_Pass3.xlsx`);
  for(const [sheetName,range,name] of [['Aether pilot','A7:G16','pilot_raw.png'],['Aether pilot','A45:F65','pilot_calculations.png'],['Findings','A1:F14','pass3_findings.png']]){const p=await book.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`${dest}/${name}`,new Uint8Array(await p.arrayBuffer()));}
  process.exit(0);
}

if(process.argv.includes('--audit-preview') || process.argv.includes('--pass2')) {
  const existing='outputs/ipo-ready-survey-20261021/IPO_Ready_Research_Survey_Pass1.xlsx';
  const book=await SpreadsheetFile.importXlsx(await FileBlob.load(existing));
  const dest='outputs/ipo-ready-survey-20261022';
  await fs.mkdir(dest,{recursive:true});
  console.log((await book.inspect({kind:'region',sheetId:'Survey log',range:'A27:P30',maxChars:1500,tableMaxCols:4,tableMaxRows:4})).ndjson);
  if(process.argv.includes('--audit-preview')) {
    const p=await book.render({sheetName:'Findings',range:'A1:F14',scale:1,format:'png'});
    await fs.writeFile(`${dest}/before.png`,new Uint8Array(await p.arrayBuffer()));
    process.exit(0);
  }
  const additions=JSON.parse(await fs.readFile('research/github_audit_20261022/audit_rows.json','utf8'));
  const log=book.worksheets.getItem('Survey log');
  const findings=book.worksheets.getItem('Findings');
  log.tables.items[0].rows.add(null, additions.map(r=>[...r,new Date('2026-10-22T00:00:00Z')]));
  log.getRange('A35:P43').copyFrom(log.getRange('A5:P13'),'all');
  log.getRange('A35:P43').values=additions.map(r=>[...r,new Date('2026-10-22T00:00:00Z')]);
  log.getRange('A35:P43').format.rowHeight=110;
  log.getRange('P35:P43').setNumberFormat('dd mmm yyyy');
  log.getRange('M5:M43').dataValidation={rule:{type:'list',values:['Selected full-text sections','Abstract reviewed','Abstract and repository overview','Abstract and dataset page','Resource index reviewed','Public page inspected','Vendor features page','Selected PDF sections','README reviewed','Repository overview','Official filing metadata','PDF identity and text checked','Search excerpt only','Official page inspected','Dataset preview','Dataset page reviewed','Code and controlled probes','Selected code inspected','Repository metadata checked','Published data inspected']}};
  const vals=log.getRange('A5:P34').values;
  for(let i=0;i<vals.length;i++) {
    if(vals[i][0]==='T04' || vals[i][0]==='T06') {
      const n=i+5;
      log.getRange(`H${n}`).values=[['Pass 1 README review extended by pinned code audit on 22 Oct 2026. See '+(vals[i][0]==='T04'?'A01–A04, A07–A08.':'A05–A06, A08–A09.')]];
      log.getRange(`L${n}`).values=[['Public repository. No LICENSE/COPYING/NOTICE file found in inspected pinned tree. Reuse terms unresolved.']];
      log.getRange(`M${n}`).values=[['Selected code inspected']];
      log.getRange(`N${n}`).values=[['Next: trace a real issuer through original disclosure and output. Full application not run.']];
      log.getRange(`P${n}`).values=[[new Date('2026-10-22T00:00:00Z')]];
    }
  }
  findings.getRange('A2').values=[['IPO-Ready: research findings, pass 2']];
  findings.getRange('B4').values=[[new Date('2026-10-22T00:00:00Z')]];
  findings.getRange('D4').values=[[39]];
  findings.getRange('F4').values=[['Code audit']];
  findings.getRange('B7:F7').values=[['Pilot a financial-research report with verified definitions and per-value evidence. Keep the schema reusable for listed companies.','A01, A05–A07, A09','The audit found specific definition, missingness and provenance issues worth addressing. This is an engineering hypothesis, not proven market demand.','Create a small manually verified dataset before building extraction or an agent.','Proposed']];
  findings.getRange('B8:F8').values=[['Explore financial reconciliation, reliable unknown states and historical reproducibility as measurable improvements.','A01–A09','Close tools already exist. Controlled probes expose testable requirements beyond a feature checklist.','Compare the same real RHP across tools and measure extraction and evidence accuracy.','Needs real-document validation']];
  findings.getRange('B9:F9').values=[['Show ratios and data coverage first. Evaluate any composite score separately.','A02, A09, R01','Coverage-based confidence is not measured accuracy. Missing PAT must not imply a known non-loss-making state.','Specify nullable flags and minimum data requirements for each metric.','Proposed']];
  findings.getRange('B10:F10').values=[['Require compatible EPS periods, share counts and peer dates before interpreting offer P/E.','A03, R02–R03, M01','A computed P/E can be mathematically correct yet use an unsuitable earnings definition.','Audit one EPS table and distinguish annual, TTM and weighted EPS.','Needs real-document validation']];
  findings.getRange('B11:F11').values=[['Distinguish operating revenue from total income. Derive debt only from known components or mark it partial.','A01, A05–A06','Examples: incomplete debt becomes a numeric total, and total income is reused as revenue.','Draft the metric dictionary and reconciliation rules.','Next action']];
  findings.getRange('B13:F13').values=[['Use actual elapsed fiscal years and preserve evidence per year and metric.','A01, A06–A07','FY23 100 to FY25 121 gives 10% annual growth. Counting observations can produce 21%.','Record period end, original unit, statement basis and source page per observation.','Proposed']];
  findings.getRange('B20:F20').values=[['Code review of two closest GitHub projects','9 detailed audit records and 7 controlled examples','A01–A09, T04, T06','Static audit and focused probes complete. Full pipelines and original-RHP reconciliation remain untested.','Partial: code inspected']];
  findings.getRange('B25').values=[['Pass 2 adds selected code review, seven controlled examples and a published-data check. Full applications and repository test suites were not run.']];
  findings.getRange('B28').values=[['Next: primary-document reconciliation and finance-paper deep reading. Existing gaps in Indian empirical validation, accounting definitions, historical price access and user demand remain open.']];
  findings.getRange('A7:F14').format.rowHeight=78;
  book.recalculate();
  const result=await SpreadsheetFile.exportXlsx(book);
  await result.save(`${dest}/IPO_Ready_Research_Survey_Pass2.xlsx`);
  for(const [name,range,file] of [['Findings','A1:F14','findings_preview.png'],['Survey log','F35:K37','audit_preview.png']]) {
    const p=await book.render({sheetName:name,range,scale:1,format:'png'});
    await fs.writeFile(`${dest}/${file}`,new Uint8Array(await p.arrayBuffer()));
  }
  console.log((await book.inspect({kind:'region',sheetId:'Survey log',range:'A35:C43',maxChars:1800,tableMaxRows:9,tableMaxCols:3})).ndjson);
  process.exit(0);
}

// Observed source statements and proposed project uses are separate columns.
const rows = [
['R01','Paper','Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers','Joseph D. Piotroski. Journal of Accounting Research 38, supplement, 1–41.',2000,'US high book-to-market firms, 1976–1996','Nine binary signals cover profitability, leverage/liquidity and operating efficiency. F-score sums these signals.','Read abstract and financial-signal methodology, PDF pp. 7–10.','Simple accounting rules offer an explainable baseline.','Test original F-score alongside separate ratio trends. Publish every component and missing input.','Original population differs from Indian IPO issuers. An IPO share issue can affect the equity-issuance signal. Score is not a calibrated distress probability.','Open paper PDF hosted by Ivey.','Selected full-text sections','Read precise denominator and equity-issuance definitions before implementation.','https://www.ivey.uwo.ca/media/3775523/value_investing_the_use_of_historical_financial_statement_information.pdf'],
['R02','Paper','Are IPOs Really Underpriced?','Amiyatosh K. Purnanandam and Bhaskaran Swaminathan. Review of Financial Studies 17(3), 811–848. DOI 10.1093/rfs/hhg055.',2004,'Over 2,000 US IPOs, 1980–1997','Publisher abstract reports offer-price overvaluation of 14%–50%, depending on peer matching, despite positive first-day returns.','Compare offer valuation with industry peer multiples. Abstract reviewed.','Listing gains and relative fundamental valuation answer different questions.','Separate valuation range from listing-return outcome. Vary peer matching and show the sensitivity.','US historical evidence is not a result about Indian IPOs. Estimates depend on peer criteria. Full methods not reviewed.','Abstract open. Publisher full text may require access.','Abstract reviewed','Read full method with R03 and reproduce alternative matching rules on a small Indian sample.','https://academic.oup.com/rfs/article-abstract/17/3/811/1612977'],
['R03','Paper','Are IPOs really overpriced?','Steven X. Zheng. Journal of Empirical Finance 14(3), 287–309. DOI 10.1016/j.jempfin.2006.06.001.',2007,'IPO comparable-valuation methodology','Publisher search excerpt challenges earlier overpricing conclusions using a modified valuation method.','Publisher excerpt only. Direct publisher page returned 403.','Competing findings make model specification a research question.','Compare more than one peer-selection and aggregation rule before declaring an IPO expensive.','Full paper not reviewed. Do not treat this as a settled rebuttal or transfer its findings directly to India.','Publisher page blocked in this browser. Locate an author manuscript or library copy.','Search excerpt only','Obtain full text and document exactly which corrections change the earlier findings.','https://www.sciencedirect.com/science/article/abs/pii/S0927539806000387'],
['R04','Paper','FinQA: A Dataset of Numerical Reasoning over Financial Data','Zhiyu Chen et al. EMNLP 2021. arXiv:2109.00122.',2021,'Financial reports and numerical question answering','Expert-written questions include gold reasoning programs for explainability. Paper describes gaps between models and experts.','Abstract and linked repository overview reviewed.','A correct answer needs a defensible computation path.','Store operands, source locations, formula and result. Build local questions for margins, growth and cash conversion.','Not an Indian IPO dataset. Benchmark results do not establish performance on Indian prospectuses.','Open paper and public code/data repository. Dataset terms need separate review.','Abstract and repository overview','Read dataset schema and adapt 10–20 question patterns to manually verified prospectus facts.','https://arxiv.org/abs/2109.00122'],
['R05','Paper','TAT-QA: A Question Answering Benchmark on a Hybrid of Tabular and Textual Content in Finance','Fengbin Zhu et al. ACL 2021. arXiv:2105.07624.',2021,'Financial reports combining tables and narrative','TAGOP selects relevant table cells and text spans, then applies symbolic operations.','Abstract reviewed.','Table cells alone may omit units, footnotes and definitions.','Preserve table headers, adjacent notes, period, currency unit and consolidation basis during extraction.','Benchmark data and models are not validated for Indian offer documents. Full experimental method not reviewed.','Open paper. Follow paper links for dataset and terms.','Abstract reviewed','Inspect examples involving units, signs and table-to-text reasoning.','https://arxiv.org/abs/2105.07624'],
['R06','Paper','FinanceBench: A New Benchmark for Financial Question Answering','Pranab Islam et al. arXiv:2311.11944.',2023,'Open-book QA over publicly traded companies','Describes 10,231 questions with answers and evidence. Evaluates 16 model configurations on 150 cases.','Abstract reviewed. Public dataset link followed.','Evidence retrieval and correct answering need separate evaluation.','Measure answer accuracy and evidence correctness on a local gold set. Include unanswerable questions.','2023 model performance is historical. The public sample is not the entire question collection. Indian document accuracy remains untested.','Open paper and public sample. Check dataset card before reuse.','Abstract and dataset page','Read scoring protocol and design a small Indian IPO evaluation set.','https://arxiv.org/abs/2311.11944'],
['R07','Paper','FinRobot: AI Agent for Equity Research and Valuation with Large Language Models','Tianyu Zhou, Pinqiao Wang, Yilin Wu and Hongyang Yang. arXiv:2411.08804.',2024,'Automated equity research and valuation','Presents an agent-based equity-research approach with quantitative analysis and valuation.','Abstract reviewed. Repository logged separately as T01.','Existing financial agent work is a useful architecture reference.','Study how research tasks, numerical tools and report generation are coordinated.','Preprint and project claims are not independent validation. India-specific data and accounting require adaptation.','Open preprint.','Abstract reviewed','Read architecture and evaluation sections before deciding whether orchestration adds value.','https://arxiv.org/abs/2411.08804'],
['M01','Learning resource','Damodaran valuation materials','Aswath Damodaran, NYU Stern.',null,'DCF, relative valuation and option valuation','Teaching page links multiple definitions, sector datasets, spreadsheets and worked valuation examples.','Topic index and relative-valuation resource list reviewed.','Choose a valuation method consistent with the financial measure and business.','Define P/E and EV/EBITDA consistently. Explain peer ranges and assumptions before adding DCF.','Teaching material is not Indian IPO calibration. Current sector averages cannot substitute for historical as-of-date peers.','Public educational materials. Check individual dataset dates and reuse terms.','Resource index reviewed','Read Anatomy of a Multiple and P/E or EV/EBITDA notes relevant to chosen sector.','https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valuation/val.htm'],
['P01','Product','Screener company page: Aether Industries','Screener.in',null,'Indian listed-company fundamental research','Page exposes statements, ratios, peer comparison, documents, export control and machine-generated pros/cons.','Public Aether page inspected. Standalone/consolidated selector visible.','Useful benchmark for navigation and compact financial presentation.','Keep comparable-period ratio tables, explicit statement basis and source-document access.','Dynamic peers table did not load in text view. Export and AI not tested. These are current listed-company data, not a pre-IPO snapshot.','Public page. Some functions require login or payment. No licensed API established.','Public page inspected','Compare the page with a historical prospectus and record definition differences.','https://www.screener.in/company/AETHER/'],
['P02','Product','Trendlyne IPO Dashboard','Trendlyne',null,'Indian mainboard and SME IPO tracking','Shows upcoming/open IPOs and distinguishes listing-open, listing-close and later return summaries.','Public dashboard inspected.','Outcome horizons must be named explicitly.','Use separate IPO lifecycle states and separately defined outcome dates.','Dashboard is a product reference, not a verified API or an independently checked dataset. Paid workflow not tested.','Public dashboard. Check terms before collecting or redistributing data.','Public page inspected','Record required IPO fields and compare with original exchange or issuer documents.','https://next.trendlyne.com/ipo/dashboard/'],
['P03','Product','Tijori Finance research features','Tijori Finance',null,'Indian business and sector research','Advertises revenue mix, operational metrics, competitor comparisons and historical/source-link features in paid plans.','Vendor features page reviewed. Paid features not tested.','Business comparability needs more context than a sector label.','Use product mix, end markets, scale and operating model in a human-reviewed peer-selection checklist.','Feature claims do not establish coverage or quality. No licensed data feed established.','Free and paid tiers. Reuse rights need review.','Vendor features page','Walk through one accessible specialty-chemicals example and note source coverage.','https://www.tijorifinance.com/in/features/'],
['P04','Report example','Aether Industries IPO research report','Angel One',2022,'Indian specialty-chemicals IPO','Seven-page report combines business description, financial tables, risks and a post-issue TTM P/E discussion.','PDF text inspected, especially opening valuation discussion and financial tables.','Professional IPO notes offer a practical report structure and denominator choices to inspect.','Compare historical annual versus TTM earnings, share-count treatment and risks with prospectus evidence.','Broker opinion is not ground truth. Do not inherit its recommendation or valuation conclusion. Report not independently recalculated.','Public broker PDF. Copyright retained by publisher.','Selected PDF sections','Recalculate one ratio against the original offer document and explain any mismatch.','https://www.angelone.in/get-co-pdf/Aether%20Industries%20Research%20Report.pdf'],
['T01','Open-source project','FinRobot repository','AI4Finance Foundation',null,'Financial analysis and agent orchestration','README describes end-to-end financial agent workflows. Repository identifies Apache-2.0 license.','README and repository overview reviewed. No installation or execution.','Study existing tool boundaries before designing an agent.','Borrow workflow concepts for data gathering, deterministic calculations and report assembly.','Dependencies, external data services, model cost and India support not evaluated. License does not grant rights to external data.','Public Apache-2.0 code. Verify pinned version and dependencies before reuse.','README reviewed','Inspect the equity-research example and create a dependency/cost inventory.','https://github.com/AI4Finance-Foundation/FinRobot'],
['T02','Open-source project','Docling','Docling project',null,'Document parsing, layout, tables and OCR','README describes PDF layout, reading order and table-structure parsing. Code is MIT licensed with separate model licenses.','README capabilities and license note reviewed. No parser run.','Document structure is worth preserving alongside extracted text.','Benchmark table extraction on the same manually labelled prospectus pages as a simpler parser.','Capabilities are vendor/project claims until tested. OCR and table accuracy on Indian disclosures unknown.','MIT code. Model licenses require separate checks.','README reviewed','Test 3 difficult pages: multi-year table, footnotes and poor text encoding.','https://github.com/docling-project/docling'],
['T03','Open-source project','FinQA code and data','FinQA authors',2021,'Reproducible financial numerical QA benchmark','Author-linked repository provides data and code for the EMNLP paper.','Repository landing page reviewed. No code execution.','Reasoning programs can guide a transparent calculation trace.','Inspect example question, evidence and operation schema for local evaluation design.','Repository maintenance and licenses for code versus underlying reports need review. Not an Indian dataset.','Public repository. Terms not fully reviewed.','Repository overview','Check LICENSE and one sample record before reuse.','https://github.com/czyssrs/FinQA'],
['D01','Primary data source','Aether Industries final prospectus','SEBI filing / Aether Industries',2022,'Indian IPO, filed May 31, 2022','SEBI page identifies a final offer document filed with ROC and links a PDF.','Filing metadata and linked viewer verified. Financial tables not extracted.','Document type and filing date belong in the data manifest.','Candidate first pilot issuer for a reproducible historical assessment.','Final prospectus timing may follow the offer period. Select the actual disclosure available at the intended assessment date.','Public filing. No bulk-download permission or API assumed.','Official filing metadata','Find pre-offer RHP as well. Extract dates, document hash, periods, units and source pages.','https://www.sebi.gov.in/filings/public-issues/may-2022/aether-industries-limited-prospectus_59353.html'],
['D02','Primary data source','Fine Organic Industries red herring prospectus','Issuer RHP hosted by Kotak',2018,'Indian IPO RHP dated June 11, 2018','Accessible 530-page issuer document. Browser text extraction has visibly garbled characters on the opening page.','PDF opening text and document identity checked. Not a full financial review.','Public PDF availability does not guarantee clean machine-readable text.','Useful second extraction test with character-encoding issues.','Host path/crawl date is not publication date. Verify dates and financial tables visually before labelling.','Public PDF on bank host. Confirm canonical issuer/SEBI copy and reuse terms.','PDF identity and text checked','Inspect financial statements, units and basis-for-price pages visually.','https://www.kotak.com/content/dam/Kotak/files/asba-ipo-offers/fine-organics.pdf'],
['D03','Primary data candidate','Clean Science and Technology prospectus candidate','SEBI search result',2021,'Search result identifies prospectus dated July 12, 2021','A SEBI result points to this PDF, but direct opening failed. URL path uses April 2023.','Search excerpt only. Document contents unverified.','Publication date must come from the document and filing metadata, not the URL folder.','Keep as a candidate third issuer, pending canonical-document verification.','Do not treat the financial data or document version as verified. A later hosted copy can contaminate historical reconstruction.','Candidate public PDF. Direct fetch failed.','Search excerpt only','Locate canonical filing page and visually confirm cover, date and document version.','https://www.sebi.gov.in/sebi_data/attachdocs/apr-2023/1681818551996.pdf'],
['D04','Primary data source','NSE corporate financial results','National Stock Exchange of India',null,'Indian listed issuers including potential peers','Official page exposes financial-result filing search.','Public page and results-search interface reviewed. No dataset downloaded.','Exchange filings can anchor peer and post-listing financials.','Store announcement dates and distinguish standalone, consolidated, annual and quarterly results.','Page access is not a stable bulk API. Historical revisions and consistent fields need checking.','Public browsing. Bulk access and redistribution terms not established.','Official page inspected','Manually retrieve one peer filing and inspect dates, units and available structured attachments.','https://www.nseindia.com/companies-listing/corporate-filings-financial-results'],
['D05','Primary data source','NSE XBRL filing information','National Stock Exchange of India',null,'Structured listed-company compliance filings','Official search excerpt describes tagged, standardized XBRL compliance filing and financial-results taxonomy resources.','Official search excerpt reviewed. Taxonomy and sample filings not downloaded.','Structured filings may reduce some PDF extraction work.','Investigate XBRL as an alternative input for listed peers and later outcomes.','Taxonomy consistency and historical coverage untested. This does not establish structured IPO prospectus availability.','Public information page. Filing access and terms require verification.','Search excerpt only','Inspect one real financial-result XBRL and map 10 required fields.','https://www.nseindia.in/static/companies-listing/xbrl-information'],
['D06','Community dataset','indian_ipo_prospectus_data','Hugging Face user scholarly360',null,'Indian IPO prospectus discovery','Dataset viewer shows titles and SEBI prospectus URLs, including Aether.','Dataset landing page and viewer preview inspected.','A community index can speed document discovery.','Use candidate URLs to locate and validate original regulatory filings.','Not verified clean financials. Completeness, version dates and license unresolved. No license text found in viewed page.','Public preview. Do not assume unrestricted dataset reuse.','Dataset preview','Review files, provenance and license. Validate a random sample against SEBI.','https://huggingface.co/datasets/scholarly360/indian_ipo_prospectus_data'],
['D07','Evaluation dataset','FinanceBench public dataset','Patronus AI / FinanceBench authors',2023,'Public financial QA evaluation cases','Author-linked Hugging Face dataset provides the publicly released FinanceBench cases.','Landing page reviewed. No dataset downloaded.','A small evidence-labelled test set can reveal failures before adding features.','Use its evaluation pattern for an Indian IPO gold set, separately sourced and manually checked.','Do not confuse public release with the full 10,231-question collection. License and input-report rights need review.','Public dataset page. Review card and license before reuse.','Dataset page reviewed','Inspect answer/evidence fields and define separate arithmetic and citation checks.','https://huggingface.co/datasets/PatronusAI/financebench']
];
rows.push(
['T04','GitHub similar project','IPO Radar / RHP Analyst','rohanbeingsocial',null,'Very close Indian IPO research workflow','README describes RHP extraction, peer valuation, risk flags, deterministic scoring with page traces and automated refresh.','README pipeline, quickstart and stated limits reviewed. Not executed.','Many proposed IPO-Ready features already have a public implementation claiming similar behavior.','Inspect backend/tools/analyze_standalone.py, extraction modules and tests. Compare one real RHP output with manual truth.','README claims unverified. Demo can be synthetic. Forecast validity, survivor bias, missing-data handling and data rights need audit.','Public repository. License not verified. Do not assume permission to copy code or redistribute data.','README reviewed','Highest-priority code walkthrough: trace one financial value from PDF to report and inspect score rules.','https://github.com/rohanbeingsocial/ipo-radar'],
['T05','GitHub similar project','Indian IPO Quant Research','amansingh2116',null,'Listing returns, subscription, GMP and ML screening','README describes chronological validation, deduplication, bootstrap checks and separation of current fundamentals from at-IPO inputs.','README workflow, data-source and limitations sections reviewed. Not executed.','Feature availability before the application deadline differs from availability before listing.','Study notebooks and report-generation script for chronological validation and leakage audits.','Research conclusions and reported performance not reproduced. Current fundamentals cannot serve as historical IPO features.','Public repository. License and upstream data rights not verified.','README reviewed','Inspect timestamp assumptions, train/test split and treatment of final GMP/subscription data.','https://github.com/amansingh2116/ipo_analysis'],
['T06','GitHub similar project','ipo-ai','gagandt',null,'Indian IPO dataset and comparables explorer','README documents issue filtering, company-name verification, cached raw data, offer financials and configurable historical comparables.','README schema, pipeline and known limits reviewed. Not executed.','Issuer identity, repeat offers and mixed public-issue feeds can silently corrupt a dataset.','Study src/fetch_master.py, src/cg_scrape.py and src/build_dataset.py. Borrow validation ideas and raw-cache structure.','Reported coverage and financial values unverified. Historical IPO analogues are different from listed operating-company valuation peers.','Public repository. License and upstream reuse rights unresolved.','README reviewed','Inspect a rejected name match and manually verify one completed row against its RHP.','https://github.com/gagandt/ipo-ai'],
['T07','GitHub similar project','Nifty100 Analytics','ramya831',null,'Alternative general company-financial dashboard scope','README describes Python ETL, SQLite, ratio analysis, peer comparison, Streamlit, FastAPI and tests.','README features, directory structure and analytics list reviewed. Not executed.','Useful architecture reference if the project expands to listed-company financial health.','Inspect src/etl, src/analytics, src/dq and tests. Start with a smaller slice than the advertised platform.','Feature completion and formula correctness not independently checked. Data provenance and license unresolved.','Public repository. License not verified.','README reviewed','Trace one ratio and its data-quality checks. Assess what can be omitted from a student MVP.','https://github.com/ramya831/Nifty100_Analytics'],
['P05','Product','IPO4U','IPO4U',null,'Direct Indian DRHP/RHP analysis product','Landing page advertises PDF upload, financial snapshot, risk score, promoter analysis and structured verdict.','Public landing page inspected. No upload or generated report tested.','Direct product overlap extends beyond conventional financial dashboards.','Benchmark document-to-report flow, source citations, missing inputs and export behavior.','Accuracy, timing and usage claims are marketing statements, not tested results. Page citations not established in this review.','Public website with free/paid plans. No API or redistribution rights established.','Vendor features page','Test an allowed sample or public report and compare against manually verified figures.','https://ipo4u.com/'],
['P06','Product','CMDA Hub IPO Analysis','CMDA Hub',null,'Direct prospectus-linked Indian IPO research','Public page states that analyses cover offer structure, restated financials, KPIs, risks and litigation with source-page references.','Public listing and stated feature scope inspected. Individual claims not checked against PDFs.','Source-page references are already claimed by a comparable product.','Compare evidence navigation and disclosure coverage before choosing a differentiation claim.','No extraction accuracy, completeness or model evaluation verified. Public access is not a reuse license.','Public listing. Account or access requirements for deeper workflows not tested.','Public page inspected','Open one complete report and check 5 financial values and their cited pages.','https://cmdahub.com/ipo'],
['R08','Paper','Experimenting with Multi-modal Information to Predict Success of Indian IPOs','Sohom Ghosh, Arnab Maji, N Harsha Vardhan and Sudip Kumar Naskar. arXiv:2412.16174.',2024,'Indian IPO listing-day outcomes','Studies prospectus content, macro conditions and GMP. Targets listing-day direction and underpricing at open, high and close.','Abstract reviewed. Author-linked code repository followed.','Directly relevant Indian evidence, but listing-day success differs from long-term financial strength.','Read target definitions, dataset construction and temporal feature availability. Compare to R02 and T05.','Preprint findings not independently reproduced. Full methodology and sample coverage not yet reviewed.','Open preprint with code and dataset links. Check individual licenses.','Abstract reviewed','Deep-read experiments and audit whether each input was available at prediction time.','https://arxiv.org/abs/2412.16174'],
['T08','GitHub research code','Indian_IPO','sohomghosh and paper collaborators',2024,'Code linked by Indian multimodal IPO paper','Repository is linked directly from R08 as the study code.','Repository identity and paper link verified. No notebooks or execution inspected.','Provides a route from a relevant paper to reproducible experiments.','Inspect notebook workflow, datasets and splits when deep-reading R08.','Reproducibility, environment setup, licenses and leakage not assessed.','Public repository. Code and dataset terms not yet checked.','Repository overview','Read README and inspect one experiment alongside the paper.','https://github.com/sohomghosh/Indian_IPO']
);
const wb=Workbook.create();
const findings=wb.worksheets.add('Findings');
const log=wb.worksheets.add('Survey log');
const out='outputs/ipo-ready-survey-20261021';
await fs.mkdir(out,{recursive:true});

function base(sheet,range){
  sheet.showGridLines=false;
  sheet.getRange(range).format.font={name:'Arial',size:10,color:'#243247'};
  sheet.getRange(range).format.verticalAlignment='top';
}
function header(sheet,range){sheet.getRange(range).format={fill:'#243B53',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:32,verticalAlignment:'center',horizontalAlignment:'center'};}

base(findings,'A1:F35');
findings.tabColor='#243B53';
findings.getRange('A2').values=[['IPO-Ready: research findings, pass 1']];
findings.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
findings.getRange('A4:F4').values=[['Reviewed on',new Date('2026-10-21T00:00:00Z'),'Survey records',rows.length,'Stage','Discovery']];
findings.getRange('B4').setNumberFormat('dd mmm yyyy');
findings.getRange('A6:F6').values=[['Decision area','Working conclusion','Evidence IDs','Why it matters','Next investigation','State']];
header(findings,'A6:F6');
const decisions=[
['Project direction','Pilot an evidence-linked financial research report for one Indian IPO. Keep the underlying financial schema reusable for listed companies.','P01–P04, R04–R07','Ratio displays and company research already exist. Auditability and measured extraction quality are a defensible learning objective.','Choose a pilot and map the evidence needed for one complete report.','Proposed'],
['Differentiation','Close alternatives already claim RHP extraction, source-page traces, scoring and valuation. Choose an improvement that can be measured.','T04, T06, P05, P06','Evidence links alone are not a supported novelty claim. Extraction accuracy, historical reproducibility or sector-specific analysis may offer room to improve.','Compare one shared RHP across the closest tools. Interview 3 potential users.','Needs validation'],
['Financial strength','Begin with transparent ratio trends and a separately explained rule-based baseline.','R01','F-score provides a concrete reference but is not an Indian IPO distress probability. Missing data must stay missing.','Read original definitions and assess whether each signal fits an IPO issuer.','Proposed'],
['Valuation','Show a peer-based range and sensitivity to peer selection. Keep listing return a separate outcome.','R02, R03, M01','Published findings differ with method. One multiple or one peer set should not create false precision.','Read both IPO valuation papers fully and draft inclusion/exclusion rules.','Needs deeper reading'],
['Data feasibility','Verify one company and a few peers manually before scaling extraction.','D01–D06','Filing metadata, document dates, units and statement basis require explicit reconciliation.','Confirm canonical pre-offer RHP and extract a small labelled table.','Next action'],
['AI evaluation','Evaluate fact extraction, evidence retrieval and arithmetic separately. Add narrative generation after numerical checks.','R04–R06, D07','A plausible answer can contain the wrong source, period or calculation.','Create 20–30 manually answered questions, including missing/ambiguous cases.','Proposed'],
['Historical evaluation','Label reports created now from old documents as retrospective reconstructions.','D01, D03, D04','Assessment date, disclosure availability and later revisions affect what could have been known.','Define as-of date, document version, peer-price date and separate later outcomes.','Proposed'],
['Scope boundary','Defer revenue forecasts and calibrated distress probabilities until targets, labelled data and validation are defined.','R01, R04–R06','Three example issuers can support a pilot, not supervised-model validation across IPOs.','Define a measurable target before collecting a larger chronological cohort.','Deferred']
];
findings.getRange('A7:F14').values=decisions;
findings.getRange('A7:F14').format.wrapText=true;
findings.getRange('A7:F14').format.rowHeight=70;
findings.getRange('A17:F17').values=[['Sequence','Next survey pass','Concrete output','Evidence to inspect','Completion criterion','State']];
header(findings,'A17:F17');
findings.getRange('A18:F22').values=[
[1,'Deep-read core finance literature','Method comparison for F-score and IPO peer valuation','R01, R02, R03, M01','Definitions and competing assumptions recorded from full texts.','Pending'],
[2,'Audit pilot documents','Field dictionary and document manifest','D01–D05, P04','Canonical pre-offer document and 15–20 fields verified with source pages.','Pending'],
[3,'Audit closest GitHub projects and products','Feature matrix plus code/data review','T04–T08, P05–P06, P01–P03','Trace one real issuer from source to output. Record licenses, tests and unverified claims.','Pending'],
[4,'Evaluate extraction methods','Manually labelled table and error taxonomy','T02, R04, R05','Same pages tested for headers, units, signs, periods and footnotes.','Pending'],
[5,'Set evaluation protocol','Gold questions and chronological validation plan','R06, D07','Answer, arithmetic, evidence and as-of-date checks specified.','Pending']
];
findings.getRange('A18:F22').format.wrapText=true;
findings.getRange('A18:F22').format.rowHeight=60;
findings.getRange('A25').values=[['How to use this log']];
findings.getRange('A25').format.font.bold=true;
findings.getRange('B25:F28').values=[
['This is a first-pass discovery survey. Abstract, excerpt and selected-section reviews are explicitly identified. No product account, parser or agent was run.',null,null,null,null],
['Source observations are in column G of Survey log. Learnings and proposed uses are interpretations, not claims made by the source.',null,null,null,null],
['Filter the survey by type or review depth. Update the review depth and next step as the team reads or tests each source. A blank year means no publication year was established.',null,null,null,null],
['Coverage gaps: Indian empirical validation, Altman/Ohlson/Beneish model suitability, accounting definitions, historical pricing access, legal/data-reuse terms and user demand. These remain open.',null,null,null,null]
];
for(let r=25;r<=28;r++){findings.getRange(`B${r}:F${r}`).merge();findings.getRange(`B${r}:F${r}`).format.wrapText=true;findings.getRange(`B${r}:F${r}`).format.rowHeight=44;}
const fw=[22,49,22,49,48,22]; fw.forEach((w,i)=>findings.getRangeByIndexes(0,i,28,1).format.columnWidth=w);

base(log,`A1:P${rows.length+5}`);
log.getRange('A2').values=[['Research and comparable-work survey']];
log.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
const heads=['ID','Type','Title / product','Authors / publisher / citation','Year','Market / task','Observed finding','Review basis / method','Learning (interpretation)','Potential project use','Limitations / transfer risks','Access / reuse','Review depth','Next step','Source URL','Checked on'];
log.getRange('A4:P4').values=[heads];
const data=rows.map(r=>[...r.slice(0,14),r[14],new Date('2026-10-21T00:00:00Z')]);
log.getRange(`A5:P${data.length+4}`).values=data;
const table=log.tables.add(`A4:P${data.length+4}`,true,'SurveyRecords');
table.showFilterButton=true;
header(log,'A4:P4');
log.getRange(`A5:P${data.length+4}`).format.wrapText=true;
log.getRange(`A5:P${data.length+4}`).format.rowHeight=88;
log.getRange(`E5:E${data.length+4}`).setNumberFormat('0');
log.getRange(`P5:P${data.length+4}`).setNumberFormat('dd mmm yyyy');
log.getRange(`O5:O${data.length+4}`).format.font.color='#1665A7';
const widths=[9,22,43,42,9,35,51,37,42,50,56,43,28,48,62,17];
widths.forEach((w,i)=>log.getRangeByIndexes(0,i,data.length+5,1).format.columnWidth=w);
log.freezePanes.freezeRows(4);log.freezePanes.freezeColumns(3);
for(let r=5;r<=data.length+4;r++)if(r%2===1)log.getRange(`A${r}:P${r}`).format.fill='#F0F4F8';
log.getRange(`M5:M${data.length+4}`).dataValidation={rule:{type:'list',values:['Selected full-text sections','Abstract reviewed','Abstract and repository overview','Abstract and dataset page','Resource index reviewed','Public page inspected','Vendor features page','Selected PDF sections','README reviewed','Repository overview','Official filing metadata','PDF identity and text checked','Search excerpt only','Official page inspected','Dataset preview','Dataset page reviewed']}};
for (const r of ['A7:F14','A18:F22']) findings.getRange(r).format.borders={insideHorizontal:{style:'thin',color:'#DEE5EC'}};
wb.recalculate();
console.log((await wb.inspect({kind:'sheet,table',maxChars:1600,tableMaxRows:2,tableMaxCols:3})).ndjson);
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(`${out}/IPO_Ready_Research_Survey_Pass1.xlsx`);
// A compact range keeps the overview review readable without shrinking text.
const preview=await wb.render({sheetName:'Findings',range:'A1:F14',scale:1,format:'png'});
await fs.writeFile(`${out}/findings_preview.png`,new Uint8Array(await preview.arrayBuffer()));
const detail=await wb.render({sheetName:'Survey log',range:'F4:K6',scale:1,format:'png'});
await fs.writeFile(`${out}/survey_preview.png`,new Uint8Array(await detail.arrayBuffer()));
console.log(JSON.stringify({records:rows.length,output:`${out}/IPO_Ready_Research_Survey_Pass1.xlsx`}));
