"""Bind atlas-repeat decal coordinates only to source-proven negative-V materials."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/decal-repeat';OUT.mkdir(exist_ok=True);audit=json.loads((ROOT/'artifacts/juiced2-build/body-geometry-audit.json').read_text())['cars'];catalog=json.loads((ROOT/'data/juiced2/cars.json').read_text());reports=[]
for row in audit:
 if row['code']not in ['F100_1956','MUSTANG_68']:continue
 assert hashlib.sha256((ROOT/'godot'/row['model_path'][6:]).read_bytes()).hexdigest()==row['sha256']
 grouped={}
 for entry in row['paint_uv']:grouped.setdefault(entry['material'],[]).append(entry)
 car=next(c for c in catalog['cars']if c['code']==row['code'])
 for material in car['paint_materials']:
  proof=grouped.get(material['name'],[])
  if not proof:continue
  assert all(p['triangles_entirely_nonpositive_v']==p['triangles']and p['source_sampler']==dict(wrapS=10497,wrapT=10497)for p in proof)
  material['decal_repeat_uv']=True;material['decal_repeat_source']='Actual paint-target UVs entirely V<=0; explicit original glTF sampler wrapS/T=10497(REPEAT); normalize decal UVs to the same base atlas domain.';reports.append(dict(code=row['code'],material=material['name'],triangles=sum(p['triangles']for p in proof),source_sha256=row['sha256']))
payload=json.dumps(catalog,indent=2,allow_nan=False)+'\n';(OUT/'cars.json').write_text(payload);(OUT/'verification.json').write_text(json.dumps(reports,indent=2)+'\n')
if '--publish'in sys.argv:
 for path in ['data/juiced2/cars.json','godot/assets/cars.json']:(ROOT/path).write_text(payload)
print('Published'if'--publish'in sys.argv else'Staged',len(reports),'source-proven repeating paint atlas material bindings')
