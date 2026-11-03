"""Extract three accepted donor rim meshes, retaining textures/materials."""
import sys,json,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools.carmodels.assets import decode_scene
def unpack(b):
 n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[20+n:]
def pack(d,tail):
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 return struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail
out=ROOT/'godot/assets/wheels';out.mkdir(parents=True,exist_ok=True)
rows=[]
for style,code in [('sport','GT4_HOND0018'),('mesh','GT4_BMW_0010'),('deep-dish','GT4_MAZD0012'),('shared-tire','GT4_HOND0018')]:
 b=(ROOT/'godot/assets/cars'/f'{code}.glb').read_bytes();d,tail=unpack(b)
 idx=next(i for i,n in enumerate(d['nodes']) if n.get('name')==('tire_front_right'if style=='shared-tire'else'wheel_front_right'))
 d['nodes'][idx].pop('translation',None);d['nodes'][idx].pop('scale',None)
 d['scenes']=[{'name':style,'nodes':[idx]}];d['scene']=0
 raw=pack(d,tail);parts=decode_scene(raw);p=np.concatenate([x['positions'] for x in parts]);lo=p.min(0);hi=p.max(0);centre=(lo+hi)/2;radius=max(hi[1]-lo[1],hi[2]-lo[2])/2
 root={'name':'TireRoot'if style=='shared-tire'else'RimRoot','children':[idx],'scale':[1/radius]*3,'translation':(-centre/radius).tolist()};d['scenes'][0]['nodes']=[len(d['nodes'])];d['nodes'].append(root)
 (out/f'{style}.glb').write_bytes(pack(d,tail));rows.append(dict(id=style,model_path=f'res://assets/wheels/{style}.glb',source_car=code,axle='X',outer_radius=1,classification='reconstructed style label; actual accepted donor rim geometry'))
(ROOT/'data/juiced2/wheels.json').write_text(json.dumps(rows,indent=2))
