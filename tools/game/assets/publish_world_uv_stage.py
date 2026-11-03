"""Publish an already reviewed exact-UV stage after validating every source SHA."""
import json,struct,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];STAGE=ROOT/'artifacts/juiced2-build/world-uv';TARGET=ROOT/'godot/assets/worlds';report=json.loads((STAGE/'report.json').read_text());jobs=[]
for row in report:
 source=TARGET/row['path'];staged=STAGE/row['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['source_glb_sha256'],row['path'];raw=staged.read_bytes();magic,version,length=struct.unpack_from('<4sII',raw);assert(magic,version,length)==(b'glTF',2,len(raw));size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size],parse_constant=lambda s:(_ for _ in()).throw(ValueError(s)));assert doc['extras']['nativeVertexDeclarations']['sha256']==row['vdl_sha256'];jobs.append((source,staged,hashlib.sha256(raw).hexdigest()))
for source,staged,_ in jobs:shutil.copyfile(staged,source)
shutil.copyfile(STAGE/'render-contract.json',TARGET/'render-contract.json');(STAGE/'published.json').write_text(json.dumps(dict(worlds=[dict(path=str(source.relative_to(ROOT)),sha256=sha)for source,_,sha in jobs],contract_sha256=hashlib.sha256((TARGET/'render-contract.json').read_bytes()).hexdigest()),indent=2)+'\n');print('Published',len(jobs),'reviewed exact-UV worlds and layered render contract')
