"""Measure prepared body bounds and source paint UV domains, excluding wheel trees."""
import hashlib,json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import node_matrix
catalog=json.loads((ROOT/'godot/assets/cars.json').read_text());reports=[]
for car in catalog['cars']:
 path=ROOT/'godot'/car['model_path'][6:];raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);binary=raw[28+length:];points=[];parts=[];paint_rows=[];excluded=[];paint_names={r['name']for r in car['paint_materials']};wheel_names={v for r in car['wheel_sockets']for k,v in r.items()if k in['node','tire_node']and isinstance(v,str)}
 def accessor(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];types={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'};n={'VEC2':2,'VEC3':3,'SCALAR':1}[a['type']];dtype=np.dtype(types[a['componentType']]);return np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize*n),dtype.itemsize))
 def visit(index,parent,skip=False):
  node=doc['nodes'][index];name=node.get('name','');world=parent@node_matrix(node);names=node.get('extras',{}).get('sourceNames',[]);skip=skip or name in wheel_names or name.lower().startswith(('wheel_','tire_'))or any(t in name.upper()for t in['WHEEL_STATIC','UNDER_SHADOW','HELMET'])or'HELMET'in names
  if'mesh'in node:
   mesh=doc['meshes'][node['mesh']]
   for pi,primitive in enumerate(mesh['primitives']):
    material=doc['materials'][primitive['material']];mname=material.get('name','')
    if skip or'UNDER_SHADOW'in mname:excluded.append(dict(node=name,material=mname));continue
    ids=accessor(primitive['indices']).ravel().astype(int);positions=accessor(primitive['attributes']['POSITION']);used=positions[np.unique(ids)]@world[:3,:3].T+world[:3,3];points.append(used);parts.append(dict(node=name,mesh=mesh.get('name'),material=mname,triangles=len(ids)//3,min=used.min(0).tolist(),max=used.max(0).tolist()))
    if mname not in paint_names or'TEXCOORD_0'not in primitive['attributes']:continue
    uv=accessor(primitive['attributes']['TEXCOORD_0']);tris=uv[ids].reshape(-1,3,2);used_uv=uv[np.unique(ids)];inside=np.all((tris>=0)&(tris<=1),axis=(1,2));vnegative=np.all(tris[:,:,1]<=0,axis=1);texture=material.get('pbrMetallicRoughness',{}).get('baseColorTexture',{}).get('index');sampler={}
    if texture is not None:sampler=doc.get('samplers',[])[doc['textures'][texture].get('sampler',0)]if doc.get('samplers')else{}
    paint_rows.append(dict(node=name,material=mname,triangles=len(tris),uv_min=used_uv.min(0).tolist(),uv_max=used_uv.max(0).tolist(),triangles_all_vertices_inside_unit_domain=int(inside.sum()),triangles_entirely_nonpositive_v=int(vnegative.sum()),source_sampler=dict(wrapS=sampler.get('wrapS',10497),wrapT=sampler.get('wrapT',10497))))
  for child in node.get('children',[]):visit(child,world,skip)
 for index in doc['scenes'][doc.get('scene',0)]['nodes']:visit(index,np.eye(4))
 assert points,car['code'];allpoints=np.concatenate(points);reports.append(dict(code=car['code'],model_path=car['model_path'],sha256=hashlib.sha256(raw).hexdigest(),body_bounds=dict(min=allpoints.min(0).tolist(),max=allpoints.max(0).tolist(),dimensions=np.ptp(allpoints,axis=0).tolist()),parts=parts,excluded=excluded,paint_uv=paint_rows,limits=['Body-only rendered geometry bounds are a donor-derived collision proxy adaptation, not recovered native collision hull.','Wheel/tire socket descendants, source wheel meshes, helmets and shadow planes excluded by exact prepared/source roles.']))
OUT=ROOT/'artifacts/juiced2-build/body-geometry-audit.json';OUT.write_text(json.dumps(dict(cars=reports),indent=2,allow_nan=False)+'\n')
for r in reports:
 if r['code']=='F100_1956':print(r['code'],'painttriangles',sum(p['triangles']for p in r['paint_uv']),'insideunit',sum(p['triangles_all_vertices_inside_unit_domain']for p in r['paint_uv']),'nonpositiveV',sum(p['triangles_entirely_nonpositive_v']for p in r['paint_uv']))
print('Measured30sourcebodybounds; runtime unchanged')
