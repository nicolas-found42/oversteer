"""Retain native Garage render-triangle hits at proven paint poseXZ."""
import json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import node_matrix
raw=(ROOT/'godot/assets/worlds/garage.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);binary=raw[28+n:];hits=[];point=np.array([-30.,30.])
def accessor(index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];columns={'SCALAR':1,'VEC3':3}[a['type']];return np.frombuffer(binary,dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']],count=a['count']*columns,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,columns)
def visit(index,parent,root):
 node=d['nodes'][index];matrix=parent@node_matrix(node)
 if 'mesh'in node:
  for primitive in d['meshes'][node['mesh']]['primitives']:
   positions=accessor(primitive['attributes']['POSITION']);positions=positions@matrix[:3,:3].T+matrix[:3,3];tri=positions[accessor(primitive['indices']).ravel()].reshape(-1,3,3);den=(tri[:,1,2]-tri[:,2,2])*(tri[:,0,0]-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(tri[:,0,2]-tri[:,2,2]);valid=abs(den)>1e-8;tri=tri[valid];den=den[valid];u=((tri[:,1,2]-tri[:,2,2])*(point[0]-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(point[1]-tri[:,2,2]))/den;v=((tri[:,2,2]-tri[:,0,2])*(point[0]-tri[:,2,0])+(tri[:,0,0]-tri[:,2,0])*(point[1]-tri[:,2,2]))/den;valid=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
   for height in u[valid]*tri[valid,0,1]+v[valid]*tri[valid,1,1]+(1-u[valid]-v[valid])*tri[valid,2,1]:hits.append(dict(node=root,material=primitive['material'],height=float(height)))
 for child in node.get('children',[]):visit(child,matrix,root)
for index in d['scenes'][0]['nodes']:
 name=d['nodes'][index]['name']
 if name.startswith(tuple(f'instance_{i}_source_'for i in range(6,15))):visit(index,np.eye(4),name)
assert len([h for h in hits if abs(h['height']+1.67)<.1])==2
(ROOT/'artifacts/juiced2-build/presentation/paintbooth-floor-hits.json').write_text(json.dumps(hits,indent=2,allow_nan=False)+'\n');print('Retained',len(hits),'source render-triangle hits; no runtime writes')
