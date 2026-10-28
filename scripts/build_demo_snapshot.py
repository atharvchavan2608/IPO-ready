"""Package actual Python report outputs into a self-contained offline demonstration."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from engine import build_report, PERIODS
reports={p[0]:build_report(p[0]) for p in PERIODS}
payload=json.dumps(reports,allow_nan=False).replace('</','<\\/')
template=(ROOT/'app/index.html').read_text(encoding='utf8')
html=template.replace('<script>','<script type="application/json" id="snapshot">'+payload+'</script><script>',1)
html=html.replace('Current demo: curated evidence','Offline demonstration: precomputed Python reports; regenerate with scripts/build_demo_snapshot.py. Current demo: curated evidence')
out=ROOT/'outputs/poc';out.mkdir(parents=True,exist_ok=True)
(out/'IPO_Ready_Demo.html').write_text(html,encoding='utf8')
(out/'all_reports.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
print(out/'IPO_Ready_Demo.html')
