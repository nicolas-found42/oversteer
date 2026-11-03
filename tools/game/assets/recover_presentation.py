"""Recover original tunnel BOL objects, marker transforms and frontend cameras."""
import json,struct,re,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());row=next(x for x in inv['files']if x['path'].lower()=='tracks/tunnel/tunnel.bol')
with open(inv['iso'],'rb')as f:f.seek(row['offset']);b=f.read(row['size'])
n=struct.unpack_from('>I',b)[0];o=4;records=[]
for i in range(n):
 name=b[o:o+32].split(b'\0')[0].decode('ascii');a=struct.unpack_from('>16f',b,o+32);flags=struct.unpack_from('>I',b,o+96)[0];assert all(math.isfinite(v)for v in a);matrix=[a[r*4+c]*(-1 if (r==0)!=(c==0)else 1)/(100 if c==3 and r<3 else 1)for c in range(4)for r in range(4)];records.append(dict(name=name,offset=o,flags=flags,marker=bool(flags&1),native_matrix=list(a),matrix=matrix,geometry_id=None if flags&1 else struct.unpack_from('>I',b,o+100)[0]));o+=112 if flags&1 else 116
assert o==len(b)
for ident in ['tunnel','tunnel_tunnel']:
 p=ROOT/'godot/assets/worlds'/f'{ident}.glb';raw=p.read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);tail=raw[20+size:]
 if d.get('extras',{}).get('nativeBolScene'):continue
 assert d['extras']['coordinate_system']=='godot-rh-reflect-x';groups={}
 for i,m in enumerate(d['meshes']):groups.setdefault(int(re.match(r'native_(\d+)_',m['name'])[1]),[]).append(i)
 for record in records:
  children=[];at=len(d['nodes']);node=dict(name=record['name'],matrix=record['matrix'],extras={'nativeBolOffset':record['offset'],'nativeFlags':record['flags'],'source':'tracks/tunnel/tunnel.bol','nativeVisibilityLogic':'Original flags retained; runtime conditional visibility/animation not yet recovered'})
  if record['geometry_id']is not None:
   assert record['geometry_id']in groups
   children=list(range(at+1,at+1+len(groups[record['geometry_id']])));node['children']=children
  d['nodes'].append(node)
  for mesh in groups.get(record['geometry_id'],[]):d['nodes'].append(dict(name=f'{record["name"]}_draw_{mesh}',mesh=mesh))
  d['scenes'][0]['nodes'].append(at)
 d['extras']['nativeBolScene']='tracks/tunnel/tunnel.bol';d['extras']['nativeBolSourceSha256']=hashlib.sha256(b).hexdigest();j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail)
source=json.loads((ROOT/'artifacts/juiced2-build/core-native-gameplay-config.json').read_text())['matched_records'];cameras=[]
for key in ['6bf39453','ec7a2457']:
 r=next(r for r in source if r['key']==key);current=None
 for field in r['fields']:
  if field[0]=='[Cam]':current=dict(name=field[1],native_rows=[],source_key=key,source_member=r['index'],source_sha256=r['sha256'])
  elif field[0]=='[EndCam]':cameras.append(current);current=None
  elif current is not None:current['native_rows'].append(field)
result=dict(coordinate_system='godot-rh-reflect-x',markers=records,cameras=cameras,source=dict(path=row['path'],offset=row['offset'],sha256=hashlib.sha256(b).hexdigest()),limits=['Native original source camera rows retained; offsets use native X sign and must reflect X when applied.','TunnelCol shader animation/conditional BOL visibility remain to be implemented; native geometry alone is not complete visual parity.'])
(ROOT/'data/juiced2/presentation.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'godot/assets/presentation.json').write_text(json.dumps(result,indent=2)+'\n');print('Recovered',len(records),'original BOL objects/markers;',len(cameras),'source camera presets')
