from pathlib import Path
import urllib.request,json,hashlib
root=Path(__file__).resolve().parent
docs=[('Aether_RHP_20220516.pdf','https://www.sebi.gov.in/sebi_data/attachdocs/may-2022/1652869529567.pdf'),('Angel_Aether_20220523.pdf','https://www.angelone.in/get-co-pdf/Aether%20Industries%20Research%20Report.pdf')]
manifest=[]
for name,url in docs:
 path=root/name
 if path.exists():
  data=path.read_bytes()
 else:
  with urllib.request.urlopen(url,timeout=45) as response:
   chunks=[]
   while True:
    chunk=response.read(65536)
    if not chunk:break
    chunks.append(chunk)
   data=b''.join(chunks)
 assert data[:4]==b'%PDF'
 (root/name).write_bytes(data)
 manifest.append({'file':name,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'retrieved_on':'2026-10-22'})
(root/'document_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(manifest,indent=2))
