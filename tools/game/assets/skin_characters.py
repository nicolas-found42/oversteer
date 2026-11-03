"""Retain actual source bone hierarchy, palette mapping and vertex skin weights.

The assembled parts are rebased to the source common M/F rig bind pose. Original
per-part inverse bind matrices are retained as evidence; original animations are
not invented or claimed here.
"""
import json,struct,math,hashlib,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-build/characters';out=source/'staged-complete'if'--stage'in sys.argv else ROOT/'godot/assets/characters';reports=[]
C=np.array([[.01,0,0,0],[0,0,.01,0],[0,.01,0,0],[0,0,0,1]],float);CI=np.linalg.inv(C)
def hierarchy(b):
 rows=[]
 def node(o,parent):
  assert struct.unpack_from('<I',b,o)[0]==0x70000008
  n=struct.unpack_from('<I',b,o+4)[0];name=b[o+8:o+8+n].decode();at=(o+8+n+1+3)&~3;m=np.eye(4);m[:3]=np.array(struct.unpack_from('<12f',b,at)).reshape(3,4);count=struct.unpack_from('<I',b,at+48)[0];assert count<200;idx=len(rows);rows.append(dict(name=name,parent=parent,local=m));o=at+52
  for _ in range(count):o=node(o,idx)
  return o
 assert b.find(b'posbip')>=8;node(b.find(b'posbip')-8,None)
 return rows
def quaternion(m):
 r=m[:3,:3];q=np.empty(4);trace=np.trace(r)
 if trace>0:
  s=math.sqrt(trace+1)*2;q[:]=[(r[2,1]-r[1,2])/s,(r[0,2]-r[2,0])/s,(r[1,0]-r[0,1])/s,s/4]
 else:
  i=int(np.argmax(np.diag(r)));j=(i+1)%3;k=(i+2)%3;s=math.sqrt(1+r[i,i]-r[j,j]-r[k,k])*2;q[i]=s/4;q[j]=(r[j,i]+r[i,j])/s;q[k]=(r[k,i]+r[i,k])/s;q[3]=(r[k,j]-r[j,k])/s
 return (q/np.linalg.norm(q)).tolist()
assemblies=json.loads((out/'verification.json'if'--stage'in sys.argv else ROOT/'artifacts/juiced2-build/native-character-verification.json').read_text())
for actor in assemblies:
 p=out/(actor['id']+'.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:])
 if d.get('extras',{}).get('nativeSkinning'):continue
 template=source/('avatar_lo-c7f1ce8a.bin'if 'female'in actor['id']else'avatar_lo-b41cce81.bin');bones=hierarchy(template.read_bytes());by={r['name']:i for i,r in enumerate(bones)};world=[];joint_nodes=[]
 def add(data,component,count,typ):
  while len(binary)%4:binary.append(0)
  vi=len(d['bufferViews']);d['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(data)));binary.extend(data);ai=len(d['accessors']);d['accessors'].append(dict(bufferView=vi,componentType=component,count=count,type=typ));return ai
 for i,bone in enumerate(bones):
  m=C@bone['local']@CI;w=m if bone['parent']is None else world[bone['parent']]@m;world.append(w);node=dict(name=bone['name'],translation=m[:3,3].tolist(),rotation=quaternion(m),extras={'nativeBoneIndex':i,'nativeParent':bone['parent']});joint_nodes.append(len(d['nodes']));d['nodes'].append(node)
 for i,bone in enumerate(bones):
  if bone['parent']is None:d['nodes'][0]['children'].append(joint_nodes[i])
  else:d['nodes'][joint_nodes[bone['parent']]].setdefault('children',[]).append(joint_nodes[i])
 ibms=np.stack([np.linalg.inv(w).T for w in world]).astype('<f4');ibma=add(ibms.tobytes(),5126,len(bones),'MAT4');d['skins']=[dict(name='OriginalNativeRig',joints=joint_nodes,skeleton=joint_nodes[0],inverseBindMatrices=ibma)];part_reports=[]
 for part in actor['sources']:
  b=(ROOT/part['path']).read_bytes();at=b.find(struct.pack('<I',0x70000005));count=struct.unpack_from('<I',b,at+4)[0];at+=8;palette=[]
  for i in range(count):
   length=struct.unpack_from('<I',b,at)[0];name=b[at+4:at+4+length].split(b'\0')[0].decode();o=(at+4+length+1+3)&~3;inverse=list(struct.unpack_from('<12f',b,o+24));palette.append(dict(name=name,native_inverse_bind=inverse));at=o+72
  vs=b.find(struct.pack('<I',0x70000007));nv=struct.unpack_from('<I',b,vs+4)[0];ix=b.find(struct.pack('<I',0x70000006),vs+8);stride=(ix-vs-8)//nv;assert at==vs;weights=np.array([struct.unpack_from('<4f',b,vs+8+i*stride+12)for i in range(nv)]);ids=np.array([struct.unpack_from('<4B',b,vs+8+i*stride+28)for i in range(nv)]);assert np.max(ids[weights>0])<count;assert np.max(np.abs(weights.sum(1)-1))<1e-5
  mapped=np.array([[by[palette[int(j)]['name']]if w>0 else 0 for j,w in zip(row,wr)]for row,wr in zip(ids,weights)],dtype=np.uint8);wa=add(weights.astype('<f4').tobytes(),5126,nv,'VEC4');ja=add(mapped.tobytes(),5121,nv,'VEC4');node=next(n for n in d['nodes']if n.get('name')==part['part']);node['skin']=0;node.setdefault('extras',{})['nativeBonePalette']=palette
  for primitive in d['meshes'][node['mesh']]['primitives']:primitive['attributes'].update(JOINTS_0=ja,WEIGHTS_0=wa)
  part_reports.append(dict(part=part['part'],joints=count,vertices=nv,max_weight_sum_error=float(np.max(np.abs(weights.sum(1)-1)))))
 d['extras']['nativeSkinning']=dict(source_hierarchy_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),bone_count=len(bones),status='Original hierarchy, named palette and per-vertex weights; inverse binds rebased to assembled source common rig. Original ANM decoding remains pending.');d['extras']['limits']=[x for x in d['extras'].get('limits',[])if 'skinning'not in x.lower()]+['Original ANM/facial morph animation execution remains pending.'];d['buffers'][0]['byteLength']=len(binary);j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary);reports.append(dict(id=actor['id'],bones=len(bones),parts=part_reports,hierarchy_source=str(template.relative_to(ROOT)),hierarchy_sha256=hashlib.sha256(template.read_bytes()).hexdigest()))
(out/'skinning.json').write_text(json.dumps(reports,indent=2)+'\n');(out/'skinning-report.json'if'--stage'in sys.argv else ROOT/'artifacts/juiced2-build/native-character-skinning.json').write_text(json.dumps(reports,indent=2)+'\n');print('Skinned',len(reports),'actual source assemblies')
