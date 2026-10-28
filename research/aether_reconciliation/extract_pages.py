from pathlib import Path
from pypdf import PdfReader
root=Path(__file__).resolve().parent
for file in root.glob('*.pdf'):
 reader=PdfReader(file)
 pages=[p.extract_text() or '' for p in reader.pages]
 (root/(file.stem+'.txt')).write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)),encoding='utf8')
 print(file.name,'pages',len(pages))
 if file.name.startswith('Aether'):
  for i,t in enumerate(pages):
   if any(s in t.lower() for s in ['restated statement of profit','summary of restated','weighted average','comparison with listed industry peers']):
    print('candidate',i+1,t[:160].replace('\n',' '))
