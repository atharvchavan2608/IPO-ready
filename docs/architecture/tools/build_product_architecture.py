from product_diagram_engine import *
import shutil

pages=[]

s=Scene('01-target-product-architecture','IPO-Ready | Target product architecture','C4 container view: a financial intelligence platform for discovering, comparing, evaluating and monitoring companies.',1)
s.chip(48,183,'BLUE: application / worker',BLUE,PALE_BLUE)
s.chip(333,183,'TEAL: trusted data / serving',TEAL,PALE_TEAL)
s.chip(624,183,'GOLD: external dependency',GOLD,PALE_GOLD)
s.chip(923,183,'DASHED: optional extension',PURPLE,PALE_PURPLE)
s.rect(48,218,1190,875,'#FFFFFF',LINE,16,True)
s.text(68,229,'IPO-READY SYSTEM BOUNDARY',12,MUTED,True)
s.card(68,268,540,114,'Investor web app [React / TypeScript]','Screener; company research; peer comparisons; scenario views; saved shortlists and watchlists',BLUE,PALE_BLUE,16)
s.card(658,268,540,114,'Research operations console [Web app]','Exceptions; peer / model policy review; release control; freshness and coverage',BLUE,PALE_BLUE,16)
s.card(1290,268,362,144,'Identity provider [External system]','Sign-in and tokens. IPO-Ready enforces application roles and account permissions.',GOLD,PALE_GOLD,16)
s.card(68,448,1130,116,'Product API / application backend [Python / FastAPI]','Discover and screen companies | compare peers | evaluate models and scenarios | explain evidence | save criteria, shortlists and watchlists. Queries approved snapshots; validates commands; schedules research work.',BLUE,PALE_BLUE,17)
s.arrow([(338,382),(338,448)],color=BLUE,label='HTTPS / JSON',labelpos=(355,405))
s.arrow([(928,382),(928,448)],color=BLUE,label='HTTPS / JSON',labelpos=(946,405))
s.arrow([(1198,476),(1260,476),(1260,340),(1290,340)],color=GOLD)
s.text(1285,440,'identity checks',12,GOLD)
s.card(68,654,330,204,'Data processing workers [Python]','Acquire and version evidence; parse facts and narrative; normalize and reconcile; route exceptions; produce approved fact snapshots.',BLUE,PALE_BLUE,16)
s.card(430,654,300,204,'Durable task queue [Job store / queue]','Research and refresh jobs; retries / dead letters; idempotency keys; outbox dispatch.',TEAL,PALE_TEAL,16)
s.card(762,654,436,204,'Intelligence workers [Python]','Financial / factor models; peer matching; valuation scenarios; ranking policies; cited research packaging. Heavy analysis runs asynchronously.',BLUE,PALE_BLUE,17)
s.card(1290,600,362,204,'Disclosure + market systems [External]','Filing indexes; prospectus and peer disclosures; XML/XBRL/JSON financials; offer terms and dated market snapshots.',GOLD,PALE_GOLD,17)
s.card(1290,863,362,204,'LLM provider [Optional external]','Tool-bound retrieval and explanations. Numbers, ranking policies and publication authority stay in the platform.',PURPLE,PALE_PURPLE,17)
s.arrow([(580,564),(580,654)],color=BLUE,label='enqueue research jobs',labelpos=(599,610))
s.arrow([(430,756),(398,756)],color=BLUE)
s.arrow([(730,756),(762,756)],color=BLUE)
s.text(405,727,'jobs',11,BLUE);s.text(733,727,'jobs',11,BLUE)
s.arrow([(233,654),(233,607),(1250,607),(1250,702),(1290,702)],color=GOLD)
s.text(788,583,'acquire versioned source data',12,GOLD)
s.arrow([(1198,802),(1260,802),(1260,965),(1290,965)],color=PURPLE,dash=True)
s.text(1300,827,'optional grounded calls',12,PURPLE)
stores=[(68,'Application DB [PostgreSQL]','Accounts, saved criteria, watchlists, reviews, jobs and release state'),(357,'Research DB [PostgreSQL]','Point-in-time facts; features; peer sets; model registry; runs and lineage'),(646,'Evidence store [Object storage]','Immutable filings, parsed text, model artifacts and research snapshots'),(935,'Read models [PostgreSQL]','Published screener, company, comparison and scenario projections; optional cache')]
for x,t,b in stores:s.card(x,943,263,130,t,b,TEAL,PALE_TEAL,14)
s.arrow([(68,505),(55,505),(55,916),(199,916),(199,943)],color=TEAL)
s.arrow([(320,858),(320,895),(488,895),(488,943)],color=TEAL)
s.arrow([(360,858),(360,921),(777,921),(777,943)],color=TEAL)
s.arrow([(900,858),(900,881),(545,881),(545,943)],color=TEAL)
s.arrow([(1097,858),(1097,943)],color=TEAL)
s.arrow([(1198,525),(1220,525),(1220,915),(1148,915),(1148,943)],color=TEAL)
s.text(73,893,'SQL',12,TEAL);s.text(388,869,'facts',12,TEAL);s.text(666,894,'objects',12,TEAL)
s.text(960,888,'publish',12,TEAL);s.text(1098,597,'read snapshots',12,TEAL)
s.band(1090,'CROSS-CUTTING: ACCESS CONTROL, AUDIT, MODEL VERSIONS, OBSERVABILITY AND RECOVERY','Logical stores may share PostgreSQL initially. The backend is modular; data and intelligence workers can scale independently.',h=49)
# Replace band text to fit its compact height.
pages.append(s)

s=Scene('02-product-system-context','Product scope | System context','C4 system context view: the product is defined by investor decisions and external dependencies, independent of any prototype.',2)
s.card(48,221,400,170,'Investor / research user [Person]','Find relevant companies; compare alternatives; understand financial quality, valuation and risks; save and monitor a shortlist.',BLUE,PALE_BLUE,17)
s.card(1252,221,400,170,'Research / operations team [Person]','Manage coverage; resolve exceptions; approve methodologies and releases; monitor quality and model behavior.',BLUE,PALE_BLUE,17)
s.card(650,221,400,137,'Identity platform [External system]','Authenticates investor and operations accounts.',GOLD,PALE_GOLD,16)
s.card(548,468,604,240,'IPO-READY [Software system]','Analytical company research and decision support. Combines trusted disclosures, comparable-company analysis, financial models and explainable ranking with evidence-linked research.',TEAL,PALE_TEAL,21)
s.arrow([(448,306),(503,306),(503,548),(548,548)],color=BLUE,label='discover, compare, evaluate',labelpos=(473,414))
s.arrow([(1252,306),(1197,306),(1197,548),(1152,548)],color=BLUE,label='review and operate',labelpos=(1199,414))
s.arrow([(850,468),(850,358)],color=GOLD,label='authenticate users',labelpos=(870,403))
s.card(48,827,500,208,'Financial disclosure / market systems [External]','Regulatory filing indexes, prospectus documents, company reports, structured peer financials, offer terms and dated prices. Jurisdiction adapters map these into one research model.',GOLD,PALE_GOLD,17)
s.card(1152,827,500,208,'AI language model [Optional external system]','Provides cited conversational explanation and text assistance through constrained tools. Financial calculations, ranking rules and publication authority stay in IPO-Ready.',PURPLE,PALE_PURPLE,17)
s.arrow([(548,642),(510,642),(510,783),(298,783),(298,827)],color=GOLD,label='acquire evidence and snapshots',labelpos=(48,751))
s.arrow([(1152,642),(1190,642),(1190,783),(1402,783),(1402,827)],color=PURPLE,dash=True,label='grounded explanation calls',labelpos=(1265,751))
s.band(1080,'PRODUCT OUTCOME','A user can explain why a company is shortlisted, how it compares, what could change the view, and which evidence supports that view.',h=58)
pages.append(s)

s=Scene('03-advisory-intelligence','How analysis becomes useful company advice','Logical component view of the intelligence domain: explicit models and selection policies connect data to investor decisions.',3)
journey=[('DISCOVER','Filter the investment universe'),('COMPARE','Select meaningful alternatives'),('EVALUATE','Assess quality, risk and price'),('SHORTLIST','Apply explicit selection criteria'),('MONITOR','Track meaningful changes')]
for i,(t,b) in enumerate(journey):
    x=48+i*327;s.card(x,218,296,119,t,b,TEAL,PALE_TEAL,15)
    if i<4:s.arrow([(x+296,278),(x+327,278)],color=TEAL)
s.band(365,'USER-SELECTED RESEARCH CONTEXT','Sector / business model; market; offer status; horizon; metric filters; valuation scenarios; user weights where enabled. Store context with each result.',h=67)
cs=[('1. Eligible universe + peers','Resolve entity IDs. Apply disclosure/coverage gates. Match sector, business mix, scale and basis. Keep inclusion and exclusion reasons.'),('2. Financial feature engine','Growth; margins; cash conversion; leverage; liquidity; concentration. Standardize definitions and periods; preserve source lineage.'),('3. Model + scenario engine','Sector-specific quality/risk factors; relative valuation; explicit price and earnings scenarios. Version inputs, assumptions and policies.'),('4. Ranking + explanation','Rank eligible companies within a named cohort using a disclosed policy. Show factor contributions, trade-offs, missingness and counterarguments.')]
for i,(t,b) in enumerate(cs):
    x=48+i*412;s.card(x,488,368,225,t,b,BLUE,PALE_BLUE,17)
    if i<3:s.arrow([(x+368,600),(x+412,600)],color=BLUE)
bottom=[('Selection-policy contract','Filters + cohort + factor definitions + weights + missing-data policy + tie handling + policy version. User-specific weights create a distinct saved research view.'),('Valuation / sensitivity contract','Compare price and enterprise/equity multiples on aligned dates and share bases. Display scenario ranges; unsupported methods stay unavailable. Forecast-based models are added only with explicit assumptions.'),('Explainability contract','Display quality, financial risk, valuation and data coverage separately. A result links to factors, metrics, underlying facts and cited disclosures. AI explains these results; it does not invent the ranking.')]
for x,(t,b) in zip([48,594,1140],bottom):s.card(x,797,512,238,t,b,TEAL,PALE_TEAL,17)
s.band(1073,'MODEL LIFECYCLE','Define -> implement -> test on reviewed reference cases -> evaluate stability and coverage -> approve version -> monitor -> revise or roll back.',h=65)
pages.append(s)

s=Scene('04-data-model-lifecycle','Research production | Data and model lifecycle','Asynchronous processing turns the listed data into reusable intelligence; user browsing reads prepared research products.',4)
sources=[('Filing indexes / metadata','Issuer IDs, forms, accessions, dates and amendment links'),('Prospectus / issuer reports','Statements, business, risks, offer structure and narrative'),('Peer financial disclosures','Annual/interim facts; XML/XBRL/JSON contexts; notes and accounting basis'),('Offer terms / market data','Dated price bands, prices, shares, dilution and corporate actions')]
for i,(t,b) in enumerate(sources):
    x=48+i*412;s.card(x,222,368,135,t,b,GOLD,PALE_GOLD,15)
    s.line([(x+184,357),(x+184,397)],GOLD,1.5)
s.line([(232,397),(1468,397)],GOLD,1.5)
s.arrow([(232,397),(232,459)],color=GOLD,label='adapters or controlled upload',labelpos=(250,417))
stages=[('Acquire + preserve','Source version, public time, retrieval time, checksums and original bytes'),('Extract + map','Tables / facts / text; source anchors; concepts, periods, dimensions and units'),('Normalize + reconcile','Canonical financial definitions; basis checks; conflicts and missing states'),('Quality gates + review','Automated acceptance rules; material ambiguity to analyst queue; decisions audited'),('Approve fact snapshot','Eligible versioned data; coverage manifest; exclusions; source and mapping versions')]
for i,(t,b) in enumerate(stages):
    x=48+i*327;s.card(x,459,296,180,t,b,BLUE if i<3 else TEAL,PALE_BLUE if i<3 else PALE_TEAL,15)
    if i<4:s.arrow([(x+296,549),(x+327,549)],color=TEAL)
s.card(48,733,500,198,'Financial / feature jobs','Compute deterministic metrics and comparable features. Use matched reporting periods. Store formula versions and operand fact IDs.',BLUE,PALE_BLUE,17)
s.card(600,733,500,198,'Models + research evaluation','Approve peer sets; execute factor/ranking policies and valuation scenarios; test outputs and drift in input coverage / distributions.',BLUE,PALE_BLUE,17)
s.card(1152,733,500,198,'Publish research package','Atomically release company, screener, comparison, scenario and evidence projections under one research snapshot ID.',TEAL,PALE_TEAL,17)
s.arrow([(1504,639),(1504,683),(298,683),(298,733)],color=TEAL,label='approved snapshot -> computation',labelpos=(674,658))
s.arrow([(548,832),(600,832)],color=BLUE)
s.arrow([(1100,832),(1152,832)],color=TEAL)
s.band(975,'EXCEPTIONS DO NOT DISAPPEAR','Failed retrieval / extraction -> bounded retry or repair. Conflicting / ambiguous facts -> review. Incomplete metrics -> explicit unavailable states.',accent=GOLD,fill=PALE_GOLD,h=63)
s.band(1062,'REFRESH LOOP','New filing, price refresh, correction or policy change -> identify dependencies -> recompute affected research -> release successor snapshot -> refresh watchlists.',h=72)
pages.append(s)

s=Scene('05-point-in-time-research','Research state | Evidence, versions and consistency','Point-in-time data and frozen model inputs make a shortlist or comparison explainable and reproducible after the data changes.',5)
cs=[('DocumentVersion','Source identity; immutable hash; publication / retrieval time; supersedes relation'),('FactVersion','Raw + canonical value; metric; period / basis; evidence anchor; review / mapping version'),('MetricFeatureSet','Snapshot of derived metrics; formula versions; operand fact IDs; coverage states'),('ResearchRun','Fact / feature manifests; peer set; policy / model version; scenarios; code and run state'),('ResearchSnapshot','Approved outputs; cohort and assumptions; evidence; publication / expiry timestamps')]
for i,(t,b) in enumerate(cs):
    x=48+i*327;s.card(x,240,296,216,t,b,TEAL,PALE_TEAL,16)
    if i<4:s.arrow([(x+296,348),(x+327,348)],color=TEAL)
s.card(48,533,774,220,'Run manifest | the reproducibility contract','Pin source and fact versions; analysis cutoff; financial periods; market-data as-of times; currency/basis rules; peer membership; factor definitions and weights; model/scenario versions; code version; reviewer and release decision.',BLUE,PALE_BLUE,18)
s.card(872,533,780,220,'Serving contract | one coherent research version','All screener, company, comparison and explanation responses identify the research snapshot, coverage and relevant market-data time. Build projections before switching the published pointer. Cache keys include snapshot and query/criteria IDs.',BLUE,PALE_BLUE,18)
s.text(48,809,'RELIABLE CHANGE PROPAGATION',16,TEAL,True)
events=[('Commit change + outbox','One database transaction'),('Dispatch work event','Retry-safe event ID'),('Rebuild affected outputs','Idempotent worker / projector'),('Release + invalidate','Versioned pointer + cache event')]
for i,(t,b) in enumerate(events):
    x=48+i*412;s.card(x,847,368,126,t,b,TEAL,PALE_TEAL,15)
    if i<3:s.arrow([(x+368,910),(x+412,910)],color=TEAL)
s.band(1015,'TEMPORAL RULE','Source-publication time controls eligibility; retrieval time records when the platform learned it. Historical reconstruction is labelled. Later amendments do not rewrite older research.',h=67)
s.text(48,1108,'History, audit records and outbox events are retained; full event sourcing is not required for this design.',14,MUTED)
pages.append(s)

s=Scene('06-deployment-operating-model','Startup deployment | Reliability and growth','Deployment view: a practical launch topology, with scale boundaries chosen for actual workload rather than the prototype code.',6)
s.card(48,222,480,145,'Public edge + web delivery','HTTPS, CDN/static frontend delivery, request limits, web protection and authenticated sessions.',BLUE,PALE_BLUE,17)
s.card(584,222,480,145,'Private application runtime','Modular Python API; separate data and intelligence worker processes; scheduler/outbox dispatcher.',BLUE,PALE_BLUE,17)
s.card(1120,222,532,145,'Managed data services','PostgreSQL schemas; durable jobs/queue; private object storage. Secrets and service identities scoped by role.',TEAL,PALE_TEAL,17)
s.arrow([(528,296),(584,296)],color=BLUE,label='API',labelpos=(541,267))
s.arrow([(1064,296),(1120,296)],color=TEAL,label='private',labelpos=(1068,267))
s.rect(48,438,1604,279,BG,LINE,13)
s.text(68,458,'OPERATING CONTROLS APPLY TO EVERY DOMAIN',15,TEAL,True)
controls=[('Access + data separation','Investor / analyst / admin roles; account-scoped saved research; common financial evidence kept separate from private user data.'),('Observability + freshness','Trace API request -> job -> research run; monitor lag, parser failures, coverage changes, model shifts and serving errors.'),('Recovery + controlled release','Database point-in-time recovery; evidence/artifact backups; restore drills; CI checks; staging; versioned model promotion and rollback.')]
for x,(t,b) in zip([68,603,1138],controls):s.card(x,504,494,188,t,b,TEAL,PALE_TEAL,16)
s.text(48,763,'LAUNCH NOW',17,TEAL,True)
s.text(872,763,'SCALE WHEN MEASUREMENTS JUSTIFY IT',17,BLUE,True)
s.card(48,803,774,245,'Small, deliberate deployment','One modular backend; independently runnable workers; PostgreSQL facts/features/read projections; object storage; durable job table or managed queue. PostgreSQL full-text search first. AI is a replaceable provider adapter.',TEAL,PALE_TEAL,18)
s.card(872,803,780,245,'Preserve the same domain contracts','Add worker replicas for backlog; dedicated cache/read replicas for query pressure; a search service for retrieval load; an analytical warehouse for large cohort scans. Extract a service only for measured isolation, scaling or ownership needs.',BLUE,PALE_BLUE,18)
s.text(48,1090,'Proposed targets to validate: fast reads from published projections; explicit freshness labels; no duplicate publications; graceful use of the last valid snapshot.',14,MUTED)
s.text(48,1115,'Heavy extraction, model execution and optional AI inference remain off the synchronous browsing path.',14,TEAL,True)
pages.append(s)

s=Scene('07-design-decisions-roadmap','Architecture decisions | Product delivery roadmap','The startup product is the design target. Repository mockups and attached reports supply context and examples, not architectural constraints.',7)
phases=[('1 / FOUNDATION','Define the intelligence contract','Company / offering identities; metric and factor policies; peer rules; evidence schema; representative reference cases.'),('2 / CORE PRODUCT','Ship discovery and comparison','Screener, company pages, peer comparison, explicit selection criteria, valuation scenarios, evidence and saved shortlists.'),('3 / AUTOMATION','Make research repeatable','Reliable acquisition / extraction; exception queue; model approval; published snapshot refresh; watchlist changes; cited assistant.'),('4 / EXPANSION','Grow coverage and capacity','Additional sectors / jurisdictions; evaluate new models; scale workers and read services using observed demand.')]
for i,(tag,t,b) in enumerate(phases):
    x=48+i*412;s.card(x,220,368,245,t,b,BLUE if i<3 else TEAL,PALE_BLUE if i<3 else PALE_TEAL,17,tag)
    if i<3:s.arrow([(x+368,343),(x+412,343)],color=TEAL)
s.text(48,508,'KEY ARCHITECTURE DECISIONS',17,TEAL,True)
rows=[('Decision','Why it belongs in this product'),('C4 context + container + separate logical views','Keep users, runtime units, domain models and deployment concerns explicit.'),('Modular backend + asynchronous workers','Support domain separation and independent compute scaling without a service fleet.'),('Published read projections + immutable snapshots','Fast discovery/comparison; users see one coherent research version with freshness.'),('Versioned peer / factor / valuation policies','Selection and analytical advice can be explained, tested and revised.'),('Point-in-time facts + operand lineage','Reproduce research and prevent later disclosures from leaking into an earlier view.'),('Outbox + idempotent processing','Make source/model changes and downstream refresh recoverable under retries.')]
y=546
for i,(a,b) in enumerate(rows):
    rh=40 if i==0 else 53
    for x,w,t in [(48,600,a),(648,1004,b)]:
        s.rect(x,y,w,rh,TEAL if i==0 else (BG if i%2 else '#FFFFFF'),LINE,0)
        s.para(x+13,y+10,t,w-26,14,'#FFFFFF' if i==0 else INK,i==0,19)
    y+=rh
s.text(48,944,'ARCHITECTURE REFERENCES  /  PRIMARY GUIDANCE',14,TEAL,True)
s.text(48,975,'C4: c4model.com/diagrams/system-context and /container  |  Microsoft: Azure Architecture Center /patterns/cqrs',13,MUTED)
s.text(48,1000,'AWS Prescriptive Guidance: cloud-design-patterns/transactional-outbox.html  |  Accessed 29 Oct 2026',13,MUTED)
s.band(1045,'DELIVERY PRINCIPLE','Validate financial logic, ranking stability, evidence accuracy and user understanding before expanding analytical claims or product scope.',h=71)
pages.append(s)

# Stable output names replace the earlier proposal files and retain their identity.
pdfpath=OUT/'IPO_Ready_Architecture_Design.pdf'
c=canvas.Canvas(str(pdfpath));c.setTitle('IPO-Ready | Target Fintech Product Architecture');c.setAuthor('IPO-Ready project team')
for i,p in enumerate(pages):
    pdf_page(c,p,(1683.78,1190.55) if i==0 else (1190.55,841.89))
    (OUT/(p.name+'.svg')).write_text(svg(p))
c.save()
(OUT/'IPO_Ready_Editable_Diagrams.drawio').write_text(drawio(pages))
(ROOT/'tmp/product-scenes.json').write_text(json.dumps([{'name':p.name,'items':p.items,'boxes':p.boxes} for p in pages]))
print(json.dumps({'pages':len(pages),'file':str(pdfpath),'objects':[len(p.items) for p in pages]}))
