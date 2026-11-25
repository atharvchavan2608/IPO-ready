"""Fetch the user's pinned architecture package without switching/merging branches."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

COMMIT='5b71ab3e0fea6dff294519fc2f6560aad5a059aa'
FILES=['README.md','IMPLEMENTATION_BACKLOG.md','IPO_Ready_Design_Framework.md',
       'IPO_Ready_Mermaid_Diagrams.md','IPO_Ready_Eraser_Description.md',
       'IPO_Ready_Architecture_Design.pdf','IPO_Ready_Editable_Diagrams.drawio',
       '01-target-product-architecture.svg','02-product-system-context.svg',
       '03-advisory-intelligence.svg','04-data-model-lifecycle.svg',
       '05-point-in-time-research.svg','06-deployment-operating-model.svg',
       '07-design-decisions-roadmap.svg','tools/build_product_architecture.py',
       'tools/product_diagram_engine.py']

def main():
    root=Path(__file__).resolve().parents[1]
    target=root/'docs/architecture'
    rows=[]
    for name in FILES:
        url=f'https://raw.githubusercontent.com/atharvchavan2608/IPO-ready/{COMMIT}/docs/architecture/{name}'
        with urlopen(Request(url,headers={'User-Agent':'IPO-Ready-bounded-design-sync/0.1'}),timeout=12) as response:
            body=response.read(1_000_001)
            if len(body)>1_000_000: raise ValueError('Architecture file exceeds 1 MB capture limit')
        path=target/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(body)
        rows.append({'path':name,'source_url':url,'commit':COMMIT,'retrieved_at':datetime.now(timezone.utc).isoformat(),'bytes':len(body),'sha256':sha256(body).hexdigest()})
    (target/'BASELINE_MANIFEST.json').write_text(json.dumps({'source_date':'2026-10-29','commit':COMMIT,'files':rows},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'commit':COMMIT,'files_retained':len(rows),'directory':str(target)}))

if __name__=='__main__': main()
