"""Apply original ZDF static scene instances to native BDL geometry definitions."""
import json,struct,re,copy,hashlib,collections,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());base=ROOT/'godot/assets/worlds';catalog=ROOT/'artifacts/juiced2-build/world-catalogs';catalog.mkdir(parents=True,exist_ok=True)
reports=[]
def pack(d,tail):
 j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);return struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail
with open(inv['iso'],'rb') as iso:
 for f in inv['files']:
  if not f['path'].endswith('.zdf'):continue
  city=re.sub('[^a-z0-9]+','_',f['path'].split('/')[1].lower()).strip('_');ident=re.sub('[^a-z0-9]+','_',f['path'][7:].replace('zone0.zdf','').lower()).strip('_')
  source=catalog/(city+'.glb')
  current=(base/(city+'.glb')).read_bytes();cj=struct.unpack_from('<I',current,12)[0];current_doc=json.loads(current[20:20+cj])
  if not source.exists() or 'sourceInstanceScene' not in current_doc.get('extras',{}):source.write_bytes(current)
  original=source.read_bytes();js=struct.unpack_from('<I',original,12)[0];d=json.loads(original[20:20+js]);tail=original[20+js:]
  groups=collections.defaultdict(list)
  for i,m in enumerate(d['meshes']):groups[int(re.match(r'native_(\d+)_',m['name'])[1])].append(i)
  iso.seek(f['offset']);b=iso.read(f['size']);tree=struct.unpack_from('>I',b,24)[0];o=28+tree;n=struct.unpack_from('>I',b,o)[0];mo=o+4+n*8+(2 if n%2 else 0);nm=struct.unpack_from('>I',b,mo)[0];assert mo+4+nm*48==len(b)
  instances=[struct.unpack_from('>2HI',b,o+4+i*8) for i in range(n)];matrices=[struct.unpack_from('>12f',b,mo+4+i*48) for i in range(nm)];nodes=[];roots=[];missing=0;inactive=[]
  for ii,(native_id,matrix_id,flags_mesh) in enumerate(instances):
   mesh_id=flags_mesh&0x3fff;assert matrix_id<nm
   if mesh_id not in groups:missing+=1;continue
   a=matrices[matrix_id]
   if not all(math.isfinite(x)for x in a):
    assert all(math.isnan(x)for x in a),(f['path'],matrix_id,a)
    inactive.append(dict(instance=ii,native_id=native_id,matrix_index=matrix_id,reason='Original complete 3x4 matrix is all NaN; inactive placeholder omitted'));continue
   matrix=[a[0],a[4],a[8],0,a[1],a[5],a[9],0,a[2],a[6],a[10],0,a[3]/100,a[7]/100,a[11]/100,1]
   if d.get('extras',{}).get('coordinate_system')=='godot-rh-reflect-x':matrix=[x*(-1 if (i%4==0)!=(i//4==0) else 1)for i,x in enumerate(matrix)]
   root=len(nodes);children=list(range(root+1,root+1+len(groups[mesh_id])));nodes.append({'name':f'instance_{ii}_source_{mesh_id}','matrix':matrix,'children':children,'extras':{'nativeInstanceId':native_id,'nativeFlags':flags_mesh>>14,'matrixIndex':matrix_id}})
   for draw in groups[mesh_id]:nodes.append({'name':f'draw_{draw}','mesh':draw})
   roots.append(root)
  d['nodes']=nodes;d['scenes']=[{'name':ident,'nodes':roots}];d['scene']=0;d['extras']['inactiveNativeInstances']=inactive;d['extras']['sourceInstanceScene']=f['path'];d['extras']['sourceInstanceSha256']=hashlib.sha256(b).hexdigest();data=pack(d,tail);dest=base/(ident+'.glb');dest.write_bytes(data)
  if not any(r['city_id']==city for r in reports):(base/(city+'.glb')).write_bytes(data)
  reports.append(dict(id=ident,city_id=city,model_path=f'res://assets/worlds/{ident}.glb',source=f['path'],source_offset=f['offset'],source_sha256=hashlib.sha256(b).hexdigest(),instances=n,unique_matrices=nm,missing_meshes=missing,source_bounds_m=[v/100 for v in struct.unpack_from('>6f',b)],coordinate_origin=[0,0,0],scale=.01));print(ident,n,nm,'missing',missing,flush=True)
(ROOT/'data/juiced2/world-scenes.json').write_text(json.dumps(reports,indent=2)+'\n');(ROOT/'godot/assets/world-scenes.json').write_text(json.dumps(reports,indent=2)+'\n');(ROOT/'artifacts/juiced2-build/world-instance-verification.json').write_text(json.dumps(reports,indent=2)+'\n')
