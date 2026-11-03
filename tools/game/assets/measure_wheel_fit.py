"""Measure actual outboard rim faces and replacement local transforms.

Outputs evidence only unless --apply is given. Replacements preserve the source
wheel face position rather than centering their narrower barrel behind a tire cap.
"""
import sys,json,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import decode_scene,node_matrix
styles={}
for name in ['sport','mesh','deep-dish']:
 ps=np.concatenate([p['positions'][np.unique(p['indices'])]for p in decode_scene((ROOT/'godot/assets/wheels'/f'{name}.glb').read_bytes())]);faces=[]
 for part in decode_scene((ROOT/'godot/assets/wheels'/f'{name}.glb').read_bytes()):
  tri=part['positions'][part['indices']];centroids=tri.mean(1);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9);radii=np.linalg.norm(centroids[:,1:],axis=1);faces.extend(centroids[(abs(normal[:,0])>.5)&(radii>.15)&(radii<.85),0])
 styles[name]=float(np.median(faces))if faces else float(ps[:,0].max())
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());reports=[]
for car in doc['cars']:
 raw=(ROOT/'godot/assets/cars'/f"{car['code']}.glb").read_bytes();d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);world={};named={}
 def visit(i,parent):
  w=parent@node_matrix(d['nodes'][i]);world[i]=w;named[d['nodes'][i].get('name','')]=i
  for c in d['nodes'][i].get('children',[]):visit(c,w)
 for i in d['scenes'][0]['nodes']:visit(i,np.eye(4))
 parts=decode_scene(raw,car['game']);sockets=[]
 for socket in car['wheel_sockets']:
  idx=named[socket['node']];vertexparts=[];binary=raw[28+struct.unpack_from('<I',raw,12)[0]:]
  def accessor(ai):
   ac=d['accessors'][ai];v=d['bufferViews'][ac['bufferView']];dtype=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[ac['componentType']]);columns={'SCALAR':1,'VEC3':3}[ac['type']];offset=v.get('byteOffset',0)+ac.get('byteOffset',0);return np.ndarray((ac['count'],columns),dtype=dtype,buffer=binary,offset=offset,strides=(v.get('byteStride',dtype.itemsize*columns),dtype.itemsize)).copy()
  def collect(i):
   if 'mesh'in d['nodes'][i]:
    for primitive in d['meshes'][d['nodes'][i]['mesh']]['primitives']:
     positions=accessor(primitive['attributes']['POSITION']);ids=np.unique(accessor(primitive['indices']));positions=positions[ids];vertexparts.append(positions@world[i][:3,:3].T+world[i][:3,3])
   for c in d['nodes'][i].get('children',[]):collect(c)
  collect(idx);ps=np.concatenate(vertexparts);centre=world[idx][:3,3];side=1 if centre[0]>0 else -1;face=float((ps[:,0]*side).max());target=face-float(centre[0]*side)
  if socket.get('tire_embedded'):
   tire_raw=(ROOT/'godot/assets/wheels/shared-tire.glb').read_bytes();tps=np.concatenate([t['positions'][np.unique(t['indices'])]for t in decode_scene(tire_raw)]);original_width=float(np.ptp(ps[:,0]));desired_tire=np.diag([side*original_width/np.ptp(tps[:,0]),socket['outer_radius'],side*socket['outer_radius'],1.]);desired_tire[:3,3]=(ps.min(0)+ps.max(0))/2;socket['replacement_tire_transform']=(np.linalg.inv(world[idx])@desired_tire).T.reshape(-1).tolist();tire_face=float(((ps.min(0)+ps.max(0))/2)[0]*side+original_width/2);target=max(face,tire_face+.008)-float(centre[0]*side)
  basis=np.diag([side,1,side,1]);transforms={}
  for style,model_face in styles.items():
   desired=basis.copy().astype(float);desired[:3,:3]*=socket['radius'];desired[:3,3]=centre+np.array([side*(target-socket['radius']*model_face),0,0]);local=np.linalg.inv(world[idx])@desired;transforms[style]=local.T.reshape(-1).tolist()
  socket['replacement_transforms']=transforms;socket['rim_outboard_face_offset_m']=target;socket['rim_face_source']='Original selected native rim vertices'if not socket.get('tire_embedded')else'Combined original rim/tire outer face; rim separation unresolved';sockets.append(dict(node=socket['node'],centre=centre.tolist(),rim_face_offset_m=target,replacement_transforms=transforms,replacement_tire_transform=socket.get('replacement_tire_transform')))
 reports.append(dict(code=car['code'],sockets=sockets))
(ROOT/'artifacts/juiced2-build/wheel-replacement-fit.json').write_text(json.dumps(dict(styles_outboard_x=styles,cars=reports),indent=2)+'\n')
if '--apply'in sys.argv:p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes())
print('Measured120originalrimfaces; replacement transforms', 'APPLIED'if'--apply'in sys.argv else'evidence-only')
