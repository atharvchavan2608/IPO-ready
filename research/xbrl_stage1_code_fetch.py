from pathlib import Path
import json,urllib.request,hashlib
root=Path('research/xbrl_stage1_20261022')
records=json.loads((root/'download_manifest.json').read_text())
repos={
 'ShantanuAnant/nse-xbrl':['src/nse_xbrl/xbrl.py','src/nse_xbrl/models.py','src/nse_xbrl/tags.py','tests/fixtures/sample_filing.xml','tests/test_xbrl.py'],
 'dhananjaym182/india-xbrl-filings':['src/india_xbrl/reader.py','src/india_xbrl/taxonomy.py','tests/fixtures/in-capmkt/sample_integrated_2025.xml','vendor/taxonomies/in-capmkt-finance/META-INF/taxonomyPackage.xml','vendor/taxonomies/in-capmkt-finance/IntegratedFinance_IndAS/in-capmkt-ent-2025-01-31.xsd']
}
for repo,paths in repos.items():
 name=repo.split('/')[1];tree=json.loads((root/f'{name}_tree.json').read_text());sha=tree['sha']
 for path in paths:
  url=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
  try:
   with urllib.request.urlopen(url,timeout=25) as response:data=response.read()
   dest=root/name/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
   records.append({'url':url,'file':f'{name}/{path}','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'status':'downloaded','retrieved_on':'2026-10-22'})
  except Exception as exc:print('Failed',url,str(exc))
(root/'download_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print('Source files downloaded; no third-party package installed or executed.')
