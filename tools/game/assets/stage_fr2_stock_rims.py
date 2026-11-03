"""Split original static-wheel index triangles at measured rim/tire rings.

No vertex, UV, texture or triangle is created or discarded. Geometry inside the
source rim ring receives an exact separate material; tire/brake passes retain
their source materials. This is an authored geometry-role classification.
"""
import json,struct,sys,copy,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools.carmodels.assets import node_matrix
OUT=ROOT/'artifacts/juiced2-build/fr2-stock-rims';OUT.mkdir(exist_ok=True);path=ROOT/'data/juiced2/cars.json';catalog=json.loads(path.read_text());reports=[]
RINGS={'FOCUS_SVT':.209,'MUSTANG_68':.199,'LIGHTNING_SVT':.253,'F100_1956':.225}
for car in catalog['cars']:
 if car['code']not in RINGS:continue
 source=ROOT/'godot/assets/cars'/(car['code']+'.glb');raw=source.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=bytearray(raw[28+size:]);world={}
 if doc.get('extras',{}).get('oversteerStockRimSplit'):
  car['stock_rim_materials']=['stock_rim_'+car['code']];car['stock_rim_source']=doc['extras']['oversteerStockRimSplit'];reports.append(car['stock_rim_source']);(OUT/source.name).write_bytes(raw);continue
 def visit(index,parent):
  world[index]=parent@node_matrix(doc['nodes'][index])
  for child in doc['nodes'][index].get('children',[]):visit(child,world[index])
 for index in doc['scenes'][doc.get('scene',0)]['nodes']:visit(index,np.eye(4))
 def accessor(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];dtype=np.dtype({5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);count={'SCALAR':1,'VEC3':3}[a['type']]
  return np.ndarray((a['count'],count),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize*count),dtype.itemsize)).copy()
 def indices(data):
  while len(binary)%4:binary.append(0)
  vi=len(doc['bufferViews']);payload=np.asarray(data,dtype='<u4').tobytes();doc['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(payload),target=34963));binary.extend(payload);ai=len(doc['accessors']);doc['accessors'].append(dict(bufferView=vi,componentType=5125,count=len(data),type='SCALAR'));return ai
 material=copy.deepcopy(doc['materials'][0]);material['name']='stock_rim_'+car['code'];material.setdefault('extras',{})['oversteerRole']='Authored rim-only triangle classification at measured original static wheel rim ring';mi=len(doc['materials']);doc['materials'].append(material);parts=[];done=set()
 for ni,node in enumerate(doc['nodes']):
  if ni not in world or 'mesh'not in node or 'WHEEL_STATIC'not in node.get('extras',{}).get('sourceNames',[]):continue
  mesh_index=node['mesh']
  if mesh_index in done:continue
  done.add(mesh_index);mesh=doc['meshes'][mesh_index];new=[]
  for pi,primitive in enumerate(mesh['primitives']):
   assert primitive.get('mode',4)==4
   pos=accessor(primitive['attributes']['POSITION']);pos=pos@world[ni][:3,:3].T+world[ni][:3,3];center=min((np.array(s['center'])for s in car['wheel_sockets']),key=lambda c:np.linalg.norm(c-pos.mean(0)));radius=np.linalg.norm(pos[:,[1,2]]-center[[1,2]],axis=1);triangles=accessor(primitive['indices']).reshape(-1,3);rim=radius[triangles].max(1)<=RINGS[car['code']]+.003
   for subset,is_rim in [(triangles[~rim],False),(triangles[rim],True)]:
    if not len(subset):continue
    p=copy.deepcopy(primitive);p['indices']=indices(subset.reshape(-1));p['material']=mi if is_rim else primitive['material'];new.append(p)
   parts.append(dict(node=node['name'],mesh=mesh_index,source_primitive=pi,rim_triangles=int(rim.sum()),retained_other_triangles=int((~rim).sum()),total_source_triangles=len(triangles)))
  mesh['primitives']=new
 assert sum(p['rim_triangles']for p in parts)>0
 evidence=dict(code=car['code'],source_sha256=hashlib.sha256(raw).hexdigest(),measured_rim_ring_m=RINGS[car['code']],boundary_tolerance_m=.003,parts=parts,limits=['Authored geometry-role split using actual source rim/tire ring; not a recovered native customization channel.','Original brake/base wheel passes outside WHEEL_STATIC are unchanged.'])
 doc.setdefault('extras',{})['oversteerStockRimSplit']=evidence;doc['buffers'][0]['byteLength']=len(binary);j=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;(OUT/source.name).write_bytes(result);car['stock_rim_materials']=[material['name']];car['stock_rim_source']=evidence;reports.append(evidence)
 if '--publish'in sys.argv:source.write_bytes(result);car['prepared_sha256']=hashlib.sha256(result).hexdigest()
(OUT/'cars.json').write_text(json.dumps(catalog,indent=2)+'\n');(OUT/'report.json').write_text(json.dumps(reports,indent=2)+'\n')
if '--publish'in sys.argv:path.write_text(json.dumps(catalog,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(path.read_bytes())
print('Published'if'--publish'in sys.argv else'Staged','4 original FR2 rim index splits; every source triangle retained')
