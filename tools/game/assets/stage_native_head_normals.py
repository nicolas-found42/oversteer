"""Stage original head normals and source normal morphs; preserve geometry/rig."""
import hashlib,json,struct
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters'
OUT=SOURCE/'staged-head-normals';OUT.mkdir(exist_ok=True)
morphs=json.loads((SOURCE/'decoded-head-morphs.json').read_text())
raw=(ROOT/morphs['source']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==morphs['source']['sha256']
vs=raw.find(struct.pack('<I',0x70000007));nv=struct.unpack_from('<I',raw,vs+4)[0]
assert raw[vs+8+nv*68:vs+12+nv*68]==struct.pack('<I',0x70000006)
mo=raw.rfind(struct.pack('<I',0x7000000a),0,vs)
matrix=np.array(struct.unpack_from('<12f',raw,mo-48)).reshape(3,4)[:,:3]
assert np.allclose(matrix.T@matrix,np.eye(3),atol=1e-7)
native=np.array([struct.unpack_from('<3f',raw,vs+8+68*i+32)for i in range(nv)])
assert np.isfinite(native).all();length_error=float(np.max(abs(np.linalg.norm(native,axis=1)-1)));assert length_error<1e-6
normals=(native@matrix.T)[:,[0,2,1]]
reports=[]
for gender in ['male','female']:
 path=ROOT/f'godot/assets/characters/components/cc0ee14d_{gender}.glb';old=path.read_bytes();size=struct.unpack_from('<I',old,12)[0];doc=json.loads(old[20:20+size]);binary=bytearray(old[28+size:]);old_doc=json.loads(json.dumps(doc))
 def read_accessor(index):
  accessor=doc['accessors'][index];view=doc['bufferViews'][accessor['bufferView']];offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
  assert accessor['componentType']==5126 and accessor['type']=='VEC3'
  return np.frombuffer(binary,dtype='<f4',count=accessor['count']*3,offset=offset).reshape(-1,3).copy()
 def add(values):
  data=np.asarray(values,dtype='<f4');binary.extend(b'\0'*(-len(binary)%4));view=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=data.nbytes));binary.extend(data.tobytes());index=len(doc['accessors']);doc['accessors'].append(dict(bufferView=view,componentType=5126,count=len(data),type='VEC3'));return index
 mesh=doc['meshes'][0];assert len(mesh['primitives'][0]['targets'])==len(morphs['targets'])==100
 prior=read_accessor(mesh['primitives'][0]['attributes']['NORMAL']);dots=np.sum(prior*normals,axis=1)
 normal_index=add(normals);target_indices=[]
 for target in morphs['targets']:
  values=np.zeros((nv,3));start=target['first_vertex'];end=start+target['vertex_count'];assert end<=nv
  # Export position targets already use100×source_delta and weights0.01×level.
  values[start:end]=(np.asarray(target['normal_vectors'])@matrix.T)[:,[0,2,1]]*100
  target_indices.append(add(values))
 for primitive in mesh['primitives']:
  primitive['attributes']['NORMAL']=normal_index
  for target,index in zip(primitive['targets'],target_indices):target['NORMAL']=index
 doc['buffers'][0]['byteLength']=len(binary)
 encoded=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();encoded+=b' '*(-len(encoded)%4);binary.extend(b'\0'*(-len(binary)%4))
 result=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
 (OUT/path.name).write_bytes(result)
 reports.append(dict(gender=gender,path=str((OUT/path.name).relative_to(ROOT)),source_glb_sha256=hashlib.sha256(old).hexdigest(),staged_glb_sha256=hashlib.sha256(result).hexdigest(),vertices=nv,normal_targets=100,base_normal_dot_prior_percentiles=np.percentile(dots,[0,1,10,50,90,100]).tolist(),changed_normals_dot_below_095=int(np.sum(dots<.95)),preserved='AllPOSITION/index/UV/weights/joints/rig/material/position-targetaccessors unchanged; only NORMALbindings/accessorsadded'))
report=dict(source=morphs['source'],source_vertex_stride=68,normal_byte_offset=32,source_unit_length_max_error=length_error,consumer='8223B298passesr6=0to82257450;loc822575CCchoosesfactor1andaddsweight*target.normalbuffer4tobase.normalbuffer4',export='Originalnormalfloat3 transformedorthonormalmeshbasisandY/Zswap;normaldelta100×andweight0.01×nativelevel',components=reports,limits=['Source-onlystage;Godotimport/actualrenderstillrequired.','No UV-seamwelding or invented smoothing.','No proofyetthatmissingNORMALtargetssolecauseofreportedcrease;compareactualneutral/morphednativecaptures.'])
(OUT/'proof.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('Staged2originalheadnormalmeshes/100NORMALtargets each; sourceuniterror',length_error)
