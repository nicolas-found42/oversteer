"""Initialize car runtime definitions; native career builders supply events later."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];cars=json.loads((ROOT/'data/juiced2/cars.json').read_text())['cars'];definitions=[]
for i,c in enumerate(cars):
 kits=c.get('kits',[]);definitions.append(dict(id=c['code'],name=c['name'],model_path=c['model_path'],length_m=c['length_m'],width_m=c['width_m'],price=15000+i*4500,league=min(9,i//3),body_kits=[k['id']for k in kits if k['kind']=='body'],interior_kits=[k['id']for k in kits if k['kind']=='interior']))
content=dict(cars=definitions,tracks=[],events=[],leagues=[])
(ROOT/'data/juiced2/content.json').write_text(json.dumps(content,indent=2)+'\n');(ROOT/'godot/assets/game-content.json').write_text(json.dumps(content,separators=(',',':'))+'\n');print('Initialized30car definitions; run native career/league/sponsor builders before launching')
