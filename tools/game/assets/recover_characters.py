"""Recover two static avatar previews from original JSM component geometry.

Uses original mesh transforms, vertices, normals, UVs, and triangle/material groups.
Skeleton animation/morph execution is not claimed; these are source-part assemblies.
"""
import sys,json,struct,re,hashlib,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-build/characters';out=source/'staged-complete'if'--stage'in sys.argv else ROOT/'godot/assets/characters';out.mkdir(parents=True,exist_ok=True);tex=out/'textures';tex.mkdir(exist_ok=True)
for original,name in [('player01-d3f4d651.png','native-face.png'),('player01-40ab92bc.png','native-eye.png'),('player01-ab749370.png','native-hands.png')]:
 if(source/original).exists():(tex/name).write_bytes((source/original).read_bytes())
assemblies=[dict(id='native_male_baggy_t',name='Native male · baggy T',gender='M',parts=[('head','avatar_lo-cc0ee14d'),('top','avatar_lo-b41cce81'),('bottom','avatar_lo-a0a7c954'),('shoes','avatar_lo-0f990425'),('hands','avatar_lo-eb1c430d')]),dict(id='native_female_zip',name='Native female · T shirt',gender='F',parts=[('head','avatar_lo-cc0ee14d'),('top','avatar_lo-c7f1ce8a'),('bottom','avatar_lo-95fc83aa'),('shoes','avatar_lo-63819074'),('hands','avatar_lo-11328372')])];manifest=[];reports=[]
for actor in assemblies:
 actor['parts'].append(('hair','player01-6b2adb5b'))
 doc={'asset':{'version':'2.0','generator':'Oversteer native JSM component decoder'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'NativeAvatar','children':[],'rotation':[0,1,0,0]}],'meshes':[],'materials':[],'bufferViews':[],'accessors':[],'images':[{'uri':'textures/native-face.png'},{'uri':'textures/native-eye.png'},{'uri':'textures/native-hands.png'}],'textures':[{'source':0},{'source':1},{'source':2}],'extras':{'interpretation':'Static assembly of original native avatar parts; exact original preset combination and gender head morph not asserted.','limits':['Original skinning, gender-specific facial morph execution and animation playback are not implemented; source base head is shared.','Face/eye/hand albedos recovered; cloth colors are authored PBR customization defaults.']}};binary=bytearray();sources=[];allpoints=[]
 def add(data,component,count,kind,target):
  while len(binary)%4:binary.append(0)
  v=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(data),'target':target});binary.extend(data);a=len(doc['accessors']);doc['accessors'].append({'bufferView':v,'componentType':component,'count':count,'type':kind});return a
 for part,stem in actor['parts']:
  p=source/(stem+'.bin');b=p.read_bytes();vs=b.find(struct.pack('<I',0x70000007));nv=struct.unpack_from('<I',b,vs+4)[0];ix=b.find(struct.pack('<I',0x70000006),vs+8);stride=(ix-vs-8)//nv;assert stride in [68,76] and vs+8+nv*stride==ix
  mo=b.find(struct.pack('<I',0x7000000a));mat=np.array(struct.unpack_from('<12f',b,mo-48)).reshape(3,4);positions=[];normals=[];uvs=[]
  for i in range(nv):
   row=vs+8+i*stride;v=np.array(struct.unpack_from('<3f',b,row));n=np.array(struct.unpack_from('<3f',b,row+32));v=mat[:,:3]@v+mat[:,3];n=mat[:,:3]@n;n=n/max(np.linalg.norm(n),1e-8);positions.append([v[0]/100,v[2]/100,v[1]/100]);normals.append([n[0],n[2],n[1]]);uvs.append(struct.unpack_from('<2f',b,row+60))
  allpoints.extend(positions);pa=add(b''.join(struct.pack('<3f',*v)for v in positions),5126,nv,'VEC3',34962);doc['accessors'][pa]['min']=np.min(positions,axis=0).tolist();doc['accessors'][pa]['max']=np.max(positions,axis=0).tolist();na=add(b''.join(struct.pack('<3f',*v)for v in normals),5126,nv,'VEC3',34962);ua=add(b''.join(struct.pack('<2f',*v)for v in uvs),5126,nv,'VEC2',34962)
  groups=struct.unpack_from('<I',b,ix+4)[0];print(actor['id'],part,nv,stride,groups,flush=True);cursor=ix+8;primitives=[]
  for gi in range(groups):
   reserved=struct.unpack_from('<I',b,cursor)[0]
   if reserved==0:reserved,nt,material_id=struct.unpack_from('<3I',b,cursor);cursor+=12
   else:nt,material_id=struct.unpack_from('<2I',b,cursor);cursor+=8
   indices=list(struct.unpack_from('<'+str(nt*3)+'H',b,cursor));cursor=(cursor+nt*6+15)&~15;assert indices and max(indices)<nv,(part,gi,reserved,nt,material_id,cursor,nv)
   for j in range(0,len(indices),3):indices[j+1],indices[j+2]=indices[j+2],indices[j+1]
   ia=add(struct.pack('<'+str(len(indices))+'I',*indices),5125,len(indices),'SCALAR',34963);kind=part
   if part=='head':kind='skin'if material_id in [0,2]else'eyes'if material_id==3 else'hair'
   if part=='hands':kind='skin'
   color={'skin':[1,1,1,1],'eyes':[1,1,1,1],'hair':[.08,.045,.025,1],'top':[.12,.17,.25,1],'bottom':[.045,.065,.11,1],'shoes':[.075,.075,.075,1]}.get(kind,[.4,.4,.4,1]);material={'name':f'{kind}_{part}_{gi}','pbrMetallicRoughness':{'baseColorFactor':color,'roughnessFactor':.7,'metallicFactor':0},'doubleSided':True}
   if kind=='skin':material['pbrMetallicRoughness']['baseColorTexture']={'index':2 if part=='hands'else 0}
   if kind=='eyes':material['pbrMetallicRoughness']['baseColorTexture']={'index':1}
   mid=len(doc['materials']);doc['materials'].append(material);primitives.append({'attributes':{'POSITION':pa,'NORMAL':na,'TEXCOORD_0':ua},'indices':ia,'material':mid})
  # Reconstruct geometric normals: the source packed skin-normal interpretation is unresolved.
  smooth=np.zeros((nv,3),dtype=float)
  for prim in primitives:
   ac=doc['accessors'][prim['indices']];view=doc['bufferViews'][ac['bufferView']];ids=np.frombuffer(bytes(binary),dtype='<u4',count=ac['count'],offset=view['byteOffset']).reshape(-1,3);ps=np.asarray(positions)
   for tri in ids:
    normal=np.cross(ps[tri[1]]-ps[tri[0]],ps[tri[2]]-ps[tri[0]])
    for vi in tri:smooth[vi]+=normal
  smooth/=np.maximum(np.linalg.norm(smooth,axis=1)[:,None],1e-9);na=add(smooth.astype('<f4').tobytes(),5126,nv,'VEC3',34962)
  for prim in primitives:prim['attributes']['NORMAL']=na
  mesh=len(doc['meshes']);doc['meshes'].append({'name':part,'primitives':primitives});node=len(doc['nodes']);doc['nodes'].append({'name':part,'mesh':mesh});doc['nodes'][0]['children'].append(node);sources.append(dict(part=part,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),vertices=nv,stride=stride,groups=groups))
 doc['nodes'][0]['translation']=[0,-float(np.min(allpoints,axis=0)[1]),0];doc['buffers']=[{'byteLength':len(binary)}];j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;(out/(actor['id']+'.glb')).write_bytes(result)
 row={k:actor[k]for k in ['id','name','gender']};row['model_path']=f'res://assets/characters/{actor["id"]}.glb';row['source_status']='original native static component assembly; not exact recovered preset/morph/animation';
 for kind,key in [('skin','skin_materials'),('hair','hair_materials'),('top','top_materials'),('bottom','bottom_materials')]:row[key]=[m['name']for m in doc['materials']if m['name'].startswith(kind+'_')]
 manifest.append(row);reports.append(dict(id=actor['id'],sources=sources,height_m=float(np.ptp(np.array(allpoints)[:,1])),limits=doc['extras']['limits']))
(out/'avatars.json').write_text(json.dumps(dict(characters=manifest),indent=2)+'\n');(out/'verification.json'if'--stage'in sys.argv else ROOT/'artifacts/juiced2-build/native-character-verification.json').write_text(json.dumps(reports,indent=2)+'\n');print('Recovered2source-partavatarstaticpreviews')
