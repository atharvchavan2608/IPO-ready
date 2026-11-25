import json, pathlib, urllib.request, concurrent.futures

root=pathlib.Path('research/github_audit_20261022')
root.mkdir(parents=True,exist_ok=True)
repos={
 'rohanbeingsocial/ipo-radar': ['README.md','backend/app/pipeline/financial_extractor.py','backend/app/pipeline/valuation.py','backend/app/pipeline/scoring.py','backend/app/pipeline/forensic.py','backend/app/pipeline/pdf_processor.py','backend/app/pipeline/orchestrator.py','backend/app/models.py','backend/tests/test_pipeline.py','backend/tools/analyze_standalone.py','backend/requirements.txt'],
 'gagandt/ipo-ai':['README.md','src/build_dataset.py','src/cg_scrape.py','src/fetch_master.py','src/parse_nse.py','requirements.txt']
}
manifest=[]
def fetch(job):
 repo,sha,path=job
 url=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
 try:
  data=urllib.request.urlopen(url,timeout=40).read()
  dest=root/repo.split('/')[1]/path
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(data)
  return {'repo':repo,'sha':sha,'path':path,'url':f'https://github.com/{repo}/blob/{sha}/{path}','bytes':len(data)}
 except Exception as exc: return {'repo':repo,'sha':sha,'path':path,'error':str(exc)}
jobs=[]
for repo,paths in repos.items():
 tree=json.load(urllib.request.urlopen(f'https://api.github.com/repos/{repo}/git/trees/main?recursive=1',timeout=40))
 (root/(repo.split('/')[1]+'_tree.json')).write_text(json.dumps(tree,indent=2),encoding='utf-8')
 entries=[x['path'] for x in tree['tree']]
 license_files=[p for p in entries if pathlib.PurePosixPath(p).name.lower().startswith(('license','copying','notice'))]
 tests=[p for p in entries if 'test' in p.lower() and p.endswith(('.py','.json','.yml','.yaml'))]
 print(json.dumps({'repo':repo,'sha':tree['sha'],'license_files':license_files,'tests':tests,'python_files':[p for p in entries if p.endswith('.py')]}))
 jobs.extend((repo,tree['sha'],p) for p in paths+license_files)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 manifest=list(pool.map(fetch,jobs))
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'downloaded':sum('bytes'in r for r in manifest),'errors':[r for r in manifest if 'error'in r]}))
