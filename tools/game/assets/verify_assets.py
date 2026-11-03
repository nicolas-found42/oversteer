"""Validate prepared scenes, variants, dimensions and native route continuity."""
import sys,json,struct,hashlib,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools.carmodels.assets import decode_scene
cars=json.loads((ROOT/'data/juiced2/cars.json').read_text())['cars'];checks=[]
for c in cars:
 b=(ROOT/'godot/assets/cars'/f"{c['code']}.glb").read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);assert hashlib.sha256(b).hexdigest()==c['prepared_sha256'];assert len(d['scenes'])==1
 p=np.concatenate([x['positions'] for x in decode_scene(b)]);span=p.max(0)-p.min(0);assert abs(span[2]-c['length_m'])<.0001;assert abs(p.min(0)[1])<.0001
 for v in c['factory_variants']:
  for m in v['mappings']:assert m['material']<len(d['materials']) and m['primitive']<len(d['meshes'][m['mesh']]['primitives'])
 for m in c['paint_materials']:assert d['materials'][m['index']]['name']==m['name']
 checks.append(dict(code=c['code'],length_verified_m=float(span[2]),ground_height=float(p.min(0)[1]),factory_variants=len(c['factory_variants']),triangles=sum(len(p['indices']) for p in decode_scene(b))))
tracks=json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks']
for t in tracks:
 assert len(t['points'])>=3;assert all(math.isfinite(v) for p in t['points'] for v in p)
 assert max(math.dist(t['points'][i],t['points'][(i+1)%len(t['points'])]) for i in range(len(t['points'])))<30
(ROOT/'artifacts/juiced2-build/asset-verification.json').write_text(json.dumps(dict(cars=checks,native_routes_verified=len(tracks),native_route_samples=sum(len(t['points']) for t in tracks),limits=['Structural/native-coordinate verification; runtime import/render/material appearance and matched reference captures are separate.']),indent=2)+'\n')
print('PASS',len(cars),'scene/dimension/hash/variant checks;',len(tracks),'native closed route continuity checks')
