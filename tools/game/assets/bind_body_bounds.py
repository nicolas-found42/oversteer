"""Bind measured donor body underside height, preserving original wheel contacts."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/body-bounds';OUT.mkdir(exist_ok=True);rows=json.loads((ROOT/'artifacts/juiced2-build/body-geometry-audit.json').read_text())['cars'];by={r['code']:r for r in rows};assert len(by)==30
for row in rows:assert hashlib.sha256((ROOT/'godot'/row['model_path'][6:]).read_bytes()).hexdigest()==row['sha256'],row['code']
cars=json.loads((ROOT/'data/juiced2/cars.json').read_text());content=json.loads((ROOT/'data/juiced2/content.json').read_text())
for car in cars['cars']:
 row=by[car['code']];car.setdefault('handling',{})['body_min_y']=row['body_bounds']['min'][1];car['body_collision_proxy']=dict(kind='donor_rendered_body_bounds_adaptation',bounds=row['body_bounds'],prepared_sha256=row['sha256'],exclusions='Exact wheel/tire socket descendants, source wheel meshes, helmet and shadow roles; full part evidence in body-geometry-audit.json')
for car in content['cars']:
 row=by[car['id']];car.setdefault('handling',{})['body_min_y']=row['body_bounds']['min'][1];car['body_collision_proxy']=next(c['body_collision_proxy']for c in cars['cars']if c['code']==car['id'])
a=json.dumps(cars,indent=2,allow_nan=False)+'\n';b=json.dumps(content,separators=(',',':'),allow_nan=False)+'\n';(OUT/'cars.json').write_text(a);(OUT/'game-content.json').write_text(b)
if '--publish'in sys.argv:
 for path in ['data/juiced2/cars.json','godot/assets/cars.json']:(ROOT/path).write_text(a)
 for path in ['data/juiced2/content.json','godot/assets/game-content.json']:(ROOT/path).write_text(b)
print('Published'if'--publish'in sys.argv else'Staged','30measured donor body underside heights; wheel geometry/contact data unchanged')
