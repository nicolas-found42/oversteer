"""Convert original D3D left-handed world coordinates to Godot right-handed X-reflection.

The reflection changes geometry, triangle winding, instance bases and translations,
routes and road-contact arrays together. UVs and original decoded art stay intact.
"""
import json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];MARK='godot-rh-reflect-x'
for p in list((ROOT/'godot/assets/worlds').glob('*.glb'))+list((ROOT/'artifacts/juiced2-build/world-catalogs').glob('*.glb')):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);extras=d.setdefault('extras',{})
 if extras.get('coordinate_system')==MARK:continue
 binary=bytearray(raw[28+n:]);seen=set()
 for mesh in d['meshes']:
  for prim in mesh['primitives']:
   for field in ['POSITION','NORMAL']:
    a=prim['attributes'].get(field)
    if a is None or a in seen:continue
    seen.add(a);ac=d['accessors'][a];v=d['bufferViews'][ac['bufferView']];o=v.get('byteOffset',0)+ac.get('byteOffset',0);stride=v.get('byteStride',12)
    assert ac['componentType']==5126
    for i in range(ac['count']):x=struct.unpack_from('<f',binary,o+i*stride)[0];struct.pack_into('<f',binary,o+i*stride,-x)
    if 'min'in ac:ac['min'][0],ac['max'][0]=-ac['max'][0],-ac['min'][0]
   a=prim['indices']
   if a in seen:continue
   seen.add(a);ac=d['accessors'][a];v=d['bufferViews'][ac['bufferView']];o=v.get('byteOffset',0)+ac.get('byteOffset',0);kind={5125:'I',5123:'H'}[ac['componentType']];size=struct.calcsize(kind)
   for i in range(0,ac['count'],3):b,c=struct.unpack_from('<2'+kind,binary,o+(i+1)*size);struct.pack_into('<2'+kind,binary,o+(i+1)*size,c,b)
 for node in d.get('nodes',[]):
  if 'matrix'in node:
   m=node['matrix'];node['matrix']=[x*(-1 if (i%4==0) != (i//4==0) else 1)for i,x in enumerate(m)]
  if 'translation'in node:node['translation'][0]*=-1
 extras['coordinate_system']=MARK;extras['coordinate_conversion']='F=diag(-1,1,1,1); positions F*p, triangle winding reversed, instances F*M*F; native UV unchanged'
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary);print(p.name,flush=True)
for p in [ROOT/'data/juiced2/tracks.json',ROOT/'godot/assets/tracks.json',ROOT/'data/juiced2/content.json',ROOT/'godot/assets/game-content.json']:
 d=json.loads(p.read_text())
 for t in d.get('tracks',[]):
  source=t.setdefault('source',{})
  if source.get('coordinate_system')==MARK:continue
  t.setdefault('native_left_handed_points',t['points'])
  for key in ['points','surface_points']:
   if key in t:t[key]=[[-v[0],v[1],v[2]]for v in t[key]]
  if 'origin_source_units'in source:source['native_origin_source_units']=source['origin_source_units'];source['origin_source_units']=[-source['origin_source_units'][0],*source['origin_source_units'][1:]]
  source['coordinate_system']=MARK
 p.write_text(json.dumps(d,indent=2)+'\n')
