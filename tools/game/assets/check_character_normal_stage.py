"""Check source normal stage against current published geometry and morphs."""
import hashlib,json,struct
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3];SRC=ROOT/'artifacts/juiced2-build/characters';STAGE=SRC/'staged-components'
manifest=json.loads((STAGE/'components.json').read_text());reports=[]
def load(path):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];return raw,json.loads(raw[20:20+size]),raw[28+size:]
def array(doc,binary,index):
 a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
 return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,count)
morphs=json.loads((SRC/'decoded-head-morphs.json').read_text())
for skin in manifest['skins']:
 old,prior,b0=load(ROOT/'godot/assets/characters/components'/(skin['id']+'.glb'));new,doc,b1=load(STAGE/(skin['id']+'.glb'))
 assert hashlib.sha256(new).hexdigest()==skin['sha256']
 assert doc['skins']==prior['skins'] and doc['nodes']==prior['nodes']
 assert len(doc['meshes'])==len(prior['meshes'])
 triangles=0;targets=0
 for m0,m1 in zip(prior['meshes'],doc['meshes']):
  assert len(m0['primitives'])==len(m1['primitives'])
  for p0,p1 in zip(m0['primitives'],m1['primitives']):
   assert p0['material']==p1['material']
   for attr in ['POSITION','TEXCOORD_0','WEIGHTS_0','JOINTS_0']:
    assert np.array_equal(array(prior,b0,p0['attributes'][attr]),array(doc,b1,p1['attributes'][attr])),(skin['id'],attr)
   old_tri=array(prior,b0,p0['indices']).reshape(-1,3);new_tri=array(doc,b1,p1['indices']).reshape(-1,3)
   assert np.array_equal(new_tri,old_tri[:,[0,2,1]])
   triangles+=len(new_tri)
   n=array(doc,b1,p1['attributes']['NORMAL']);assert np.isfinite(n).all()and np.max(abs(np.linalg.norm(n,axis=1)-1))<1e-6
   for i,(t0,t1)in enumerate(zip(p0.get('targets',[]),p1.get('targets',[]))):
    assert np.array_equal(array(prior,b0,t0['POSITION']),array(doc,b1,t1['POSITION']))
    normal=array(doc,b1,t1['NORMAL']);target=morphs['targets'][i];expected=np.zeros(normal.shape,dtype='<f4');start=target['first_vertex'];end=start+target['vertex_count'];expected[start:end]=np.asarray(target['normal_vectors'])[:,[0,2,1]]*100
    assert np.array_equal(normal,expected), (skin['id'],i)
    targets+=1
 reports.append(dict(id=skin['id'],old_sha256=hashlib.sha256(old).hexdigest(),new_sha256=hashlib.sha256(new).hexdigest(),triangles=triangles,normal_targets_across_primitives=targets,geometry_and_rig_unchanged=True,only_triangle_winding_reversed=True))
proof=dict(components=reports,summary=dict(components=len(reports),geometry_rig_uv_weights_position_targets_preserved=True,triangle_winding_only_reversed=True,all_native_normal_targets_exact=True),limits=['MaterialsourcebindingandnativeGPUlightingareseparate.','SourceNORMALtargetsretainoriginalhardedges;novertexweldorrecomputednormals.'])
(SRC/'normal-proof/numerical.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n');print(proof['summary'])
