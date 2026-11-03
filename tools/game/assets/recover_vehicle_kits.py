"""Recover exact native 350Z accessory meshes; playable donor base is untouched.

Source namespace mesh\\<component>.xem is verified against the original archive
hashes. Original XEM hierarchy provides the wing's car-space mounting transform.
"""
import json,struct,zlib,hashlib,sys,re
from pathlib import Path
import numpy as np
from PIL import Image
from jfs_hash import filename_hash
from xenos_texture import decode
ROOT=Path(__file__).resolve().parents[3];BANK=sys.argv[1]if len(sys.argv)>1 else'350z';CAR=sys.argv[2]if len(sys.argv)>2 else'GT4_NISS0004';TAG=sys.argv[3]if len(sys.argv)>3 else'350Z';source=ROOT/'artifacts/juiced2-build/kits';source.mkdir(parents=True,exist_ok=True);out=ROOT/'godot/assets/kits';out.mkdir(parents=True,exist_ok=True)
inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());archives={}
with open(inv['iso'],'rb')as iso:
 for bank in [BANK,'shared']:
  files={}
  for ext in ['jfs','jfshdr']:
   row=next(r for r in inv['files']if r['path'].lower()==f'cars/{bank}.{ext}');iso.seek(row['offset']);files[ext]=iso.read(row['size'])
  h=files['jfshdr'];a=files['jfs'];members={}
  for i in range(struct.unpack_from('>I',h)[0]):
   k,o,p,u,_,_=struct.unpack_from('>6I',h,4+24*i);b=a[o:o+p];members[k]=b if p==u else zlib.decompress(b)
  archives[bank]=members
members=archives[BANK];hierarchies=[b for b in members.values()if b[:32].split(b'\0')[0].endswith(b'_ROOT')];assert hierarchies,(BANK,'missing source root hierarchy');hierarchy=max(hierarchies,key=len);world={}
def tree(o,parent):
 name=hierarchy[o:o+32].split(b'\0')[0].decode();m=np.array(struct.unpack_from('>16f',hierarchy,o+32)).reshape(4,4);w=parent@m;world[name]=w;geom=hierarchy[o+100:o+132].split(b'\0')[0].decode();at=o+(140 if geom!='NONE'else 136);children=struct.unpack_from('>I',hierarchy,at)[0];o=at+4
 for _ in range(children):o=tree(o,w)
 return o
assert tree(0,np.eye(4))==len(hierarchy)
kits=[]
config=next(r for r in json.loads((ROOT/'artifacts/juiced2-build/core-native-gameplay-config.json').read_text())['matched_records']if r.get('fields')and r['fields'][0][0]=='[BeginCar]'and str(r['fields'][0][1]).upper()==TAG.upper())['fields'];standards={r[1]:r[2]for r in config if r[0]=='STANDARD'}
definitions=[]
wing=next((r for r in config if r[0]=='CUSTOM'and r[1]=='SPOILER'and not any(w in str(r[3]).lower()for w in ['remove','none'])and filename_hash('mesh\\'+r[2]+'.xem')in members),None)
if wing and standards.get('SPOILER')in world:definitions.append((BANK+'-'+('varis-wing'if BANK=='350z'else'spoiler'),wing[3]+' rear wing · native '+TAG,'body',[wing[2]],standards['SPOILER'],'spoiler'))
seats=[r for r in world if r.startswith(standards.get('SEAT','UNAVAILABLE'))and filename_hash('mesh\\'+r+'.xem')in members]
if seats:definitions.append((BANK+'-native-seats','Juiced 2 seat pair · native '+TAG,'interior',seats,None,'seats'))
categories={'FBUMP':'front_bumper','RBUMP':'rear_bumper','SKIRT':'skirts','BONNET':'hood','BOOT':'trunk','ROOF':'roof','HEADLIGHTS':'headlights','REARLIGHTS':'taillights','WMIRROR':'mirrors'}
for slot,category in categories.items():
 row=next((r for r in config if r[0]=='CUSTOM'and r[1]==slot),None)
 if row is None or slot not in standards:continue
 component=row[2];base=standards[slot];names=[component]if filename_hash('mesh\\'+component+'.xem')in members else[c for c in [component+'_L',component+'_R']if filename_hash('mesh\\'+c+'.xem')in members];mounts={c:base+('_'+c[-1]if c.endswith(('_L','_R'))else'')for c in names}
 if not names or not all(m in world for m in mounts.values()):continue
 definitions.append((BANK+'-'+category,row[3]+' '+category.replace('_',' ')+' · native '+TAG,'body',names,mounts,category))
 if slot=='RBUMP'and len(row)>4 and standards.get('EXHAUST')in world and filename_hash('mesh\\'+row[4]+'.xem')in members:definitions.append((BANK+'-exhaust','Native twin exhaust · '+TAG,'body',[row[4]],standards['EXHAUST'],'exhaust'))
for kid,name,kind,names,mount_spec,category in definitions:
 mount=mount_spec
 d={'asset':{'version':'2.0','generator':'Oversteer source accessory decoder'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'images':[],'textures':[],'bufferViews':[],'accessors':[]};binary=bytearray();sources=[];paint=[]
 def add(data,component,count,typ,target):
  while len(binary)%4:binary.append(0)
  vi=len(d['bufferViews']);d['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(data),target=target));binary.extend(data);ai=len(d['accessors']);d['accessors'].append(dict(bufferView=vi,componentType=component,count=count,type=typ));return ai
 for component in names:
  mount=mount_spec.get(component)if isinstance(mount_spec,dict)else mount_spec
  filename='mesh\\'+component+'.xem';key=filename_hash(filename);b=members[key];ni=struct.unpack_from('>I',b)[0];indices=struct.unpack_from('>'+str(ni)+'H',b,4);o=4+2*ni;ng=struct.unpack_from('>I',b,o)[0];o+=4;primitives=[];index_cursor=0
  for gi in range(ng):
   material=b[o:o+32].split(b'\0')[0].decode();count,_reserved=struct.unpack_from('>2I',b,o+36);start=index_cursor;index_cursor+=count;declarations=struct.unpack_from('>I',b,o+104)[0];stride,nv=struct.unpack_from('>2I',b,o+108+12*declarations);vs=o+116+12*declarations;positions=[]
   for i in range(nv):
    p=np.array([*struct.unpack_from('>3f',b,vs+i*stride),1]);p=(world[mount]@p)if mount else p;positions.append([p[0]/100,p[1]/100,-p[2]/100])
   triangles=[];strip=[]
   for index in indices[start:start+count]:
    if index==65535:strip=[];continue
    strip.append(index)
    if len(strip)>=3:
     a,c,e=strip[-3:]
     if len(strip)%2==0:a,c=c,a
     if len({a,c,e})==3:triangles.extend([a,e,c])
   assert triangles and max(triangles)<nv;ps=np.array(positions);normals=np.zeros((nv,3))
   for tri in np.array(triangles).reshape(-1,3):
    normal=np.cross(ps[tri[1]]-ps[tri[0]],ps[tri[2]]-ps[tri[0]])
    for i in tri:normals[i]+=normal
   normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-8);pa=add(ps.astype('<f4').tobytes(),5126,nv,'VEC3',34962);d['accessors'][pa].update(min=ps.min(0).tolist(),max=ps.max(0).tolist());na=add(normals.astype('<f4').tobytes(),5126,nv,'VEC3',34962);ia=add(struct.pack('<'+str(len(triangles))+'I',*triangles),5125,len(triangles),'SCALAR',34963)
   mat=dict(name=f'native_{component}_{material}',doubleSided=True,pbrMetallicRoughness=dict(baseColorFactor=[.08,.08,.08,1],metallicFactor=.1,roughnessFactor=.6));attrs=dict(POSITION=pa,NORMAL=na)
   texture_filename='Textures\\'+material+'.ddt';tk=filename_hash(texture_filename);tb=next((bank[tk]for bank in archives.values()if tk in bank),None)
   if tb and len(tb)>40:
    fmt,w,h=struct.unpack_from('>3I',tb);im=decode(tb[40:],w,h,fmt)
    if im:
     dest=f'{tk:08x}.png';im.save(out/dest);png=(out/dest).read_bytes()
     while len(binary)%4:binary.append(0)
     d['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(png)));binary.extend(png);d['images'].append(dict(bufferView=len(d['bufferViews'])-1,mimeType='image/png'));d['textures'].append({'source':len(d['images'])-1});mat['pbrMetallicRoughness']['baseColorTexture']={'index':len(d['textures'])-1};mat['pbrMetallicRoughness']['baseColorFactor']=[1]*4
     uv_offset=next((struct.unpack_from('>I',b,o+108+i*12)[0]for i in range(declarations)if struct.unpack_from('>I',b,o+108+i*12+8)[0]>>16==5),stride-8)
     if 0<=uv_offset<=stride-4:
      uv=[struct.unpack_from('>2e',b,vs+i*stride+uv_offset)for i in range(nv)];attrs['TEXCOORD_0']=add(np.array(uv,dtype='<f4').tobytes(),5126,nv,'VEC2',34962)
   mi=len(d['materials']);d['materials'].append(mat);primitives.append(dict(attributes=attrs,indices=ia,material=mi));o=vs+stride*nv
  d['meshes'].append(dict(name=component,primitives=primitives));d['nodes'].append(dict(name=component,mesh=len(d['meshes'])-1));d['scenes'][0]['nodes'].append(len(d['nodes'])-1);sources.append(dict(filename=filename,key=f'{key:08x}',sha256=hashlib.sha256(b).hexdigest(),bank=f'cars/{BANK}.jfs'))
 d['buffers']=[{'byteLength':len(binary)}];d['extras']={'source_accessory_only':True,'compatible_car':CAR,'source_meshes':sources,'source_mount':mount,'coordinate_conversion':'native car +Z to donor -Z by reflecting Z; triangle winding reversed','adaptation':f'Native {TAG} accessory fitted to accepted {CAR} donor; original playable base geometry is unchanged.'};j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);(out/(kid+'.glb')).write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary)
 kits.append(dict(id=kid,name=name,kind=kind,category=category,fit_status='verified_blender'if BANK=='350z'and category in ['spoiler','seats']else'decoded_pending_fit',compatible_cars=[CAR],model_path=f'res://assets/kits/{kid}.glb',paint_materials=paint,source=sources,adaptation=d['extras']['adaptation'],limits=['Native accessory geometry with original mounting coordinates; donor fit needs native runtime visual verification.','Seat pair is an adapted support accessory, not a claim of an original interior customization menu.']));print(kid,flush=True)
catalog_path=ROOT/'data/juiced2/kits.json'
if catalog_path.exists():kits=[k for k in json.loads(catalog_path.read_text())['kits']if CAR not in k['compatible_cars']]+kits
(ROOT/'godot/assets/kits.json').write_text(json.dumps(dict(kits=kits),indent=2)+'\n');(ROOT/'data/juiced2/kits.json').write_text(json.dumps(dict(kits=kits),indent=2)+'\n')
for path in [ROOT/'data/juiced2/content.json',ROOT/'godot/assets/game-content.json']:
 content=json.loads(path.read_text());car=next(c for c in content['cars']if c['id']==CAR);car['body_kits']=[k['id']for k in kits if CAR in k['compatible_cars']and k['kind']=='body'and k['fit_status']=='verified_blender'];car['interior_kits']=[k['id']for k in kits if CAR in k['compatible_cars']and k['kind']=='interior'and k['fit_status']=='verified_blender'];car['parts']={k['category']:[k['id']]for k in kits if CAR in k['compatible_cars']and k['fit_status']=='verified_blender'};path.write_text(json.dumps(content,indent=2)+'\n')
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());car=next(c for c in doc['cars']if c['code']==CAR);car['kits']=[k for k in kits if CAR in k['compatible_cars']];p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes())
