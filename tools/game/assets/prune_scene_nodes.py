"""Keep only selected GLB scene nodes; duplicate shared node instances per path."""
import json,struct,hashlib,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
for p in list((ROOT/'godot/assets/cars').glob('*.glb'))+list((ROOT/'godot/assets/wheels').glob('*.glb')):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);tail=b[20+n:];old=d['nodes'];nodes=[]
 def clone(i,ancestors):
  assert i not in ancestors,'cycle'
  node=copy.deepcopy(old[i]);idx=len(nodes);nodes.append(node)
  if 'children'in node:node['children']=[clone(j,ancestors|{i}) for j in node['children']]
  return idx
 d['scenes'][0]['nodes']=[clone(i,set()) for i in d['scenes'][0]['nodes']];d['nodes']=nodes
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail;p.write_bytes(result)
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text())
for c in doc['cars']:c['prepared_sha256']=hashlib.sha256((ROOT/'godot/assets/cars'/f"{c['code']}.glb").read_bytes()).hexdigest()
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes());print('Pruned selected scene node graphs for30cars3rims')
