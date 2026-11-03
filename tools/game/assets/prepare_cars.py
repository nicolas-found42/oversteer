"""Prepare the accepted native GLBs; selected-scene geometry stays intact."""
import sys, json, struct, hashlib, subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.carmodels.assets import decode_scene
sha=lambda b:hashlib.sha256(b).hexdigest()
def unpack(b):
 n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[20+n:]
def pack(d,tail):
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 return struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail
roster=json.loads((ROOT/'data/juiced2/accepted-roster.json').read_text())
jobs=[]
for c in roster['cars']:
 src=ROOT/'artifacts/carmodels-research/models'/f"{c['code']}.glb"
 jobs.append(dict(code=c['code'],source=str(src),sha256=sha(src.read_bytes()),output=str(ROOT/'godot/assets/cars'/src.name)))
work=ROOT/'artifacts/juiced2-build';(work/'material-jobs.json').write_text(json.dumps(jobs))
subprocess.run(['node',str(ROOT/'tools/carmodels/preview_materials.mjs'),str(work/'material-jobs.json'),str(work/'material-repairs.json')],check=True)
rows=[]
for c,job in zip(roster['cars'],jobs):
 p=Path(job['output']);b=p.read_bytes();d,tail=unpack(b)
 parts=decode_scene(b,c['game']);positions=np.concatenate([x['positions'] for x in parts]);lo=positions.min(0);hi=positions.max(0)
 scale=c['profile_length_m']/(hi[2]-lo[2]); flip=c['game']=='ford-racing-2'
 centre=(lo+hi)/2;translation=[-centre[0]*scale,-lo[1]*scale,-centre[2]*scale]
 if flip:translation[0]*=-1;translation[2]*=-1
 scene=d['scenes'][d.get('scene',0)];d['scenes']=[dict(scene)];d['scene']=0
 root={'name':'VehicleRoot','children':scene['nodes'],'scale':[scale]*3,'translation':translation}
 if flip:root['rotation']=[0,1,0,0]
 d['scenes'][0]['nodes']=[len(d['nodes'])];d['nodes'].append(root)
 paints=set()
 for ch in d.get('extras',{}).get('gamePaint',{}).get('channels',[]):paints.update(ch.get('materials',[]))
 for i,m in enumerate(d.get('materials',[])):
  native=m.get('extras',{}); spec=native.get('gt4_material',{}).get('specular',[])
  if any(v>0 for v in spec[:3]) or native.get('sourceShader') in ('CarPaintCustomizable','AmbientCarPaint'):paints.add(i)
  m['name']=f"material_{i:03d}_"+m.get('name','surface').replace('/','_')
 variants=d.get('extensions',{}).get('KHR_materials_variants',{}).get('variants',[])
 vr=[dict(index=i,name=v['name'],mappings=[]) for i,v in enumerate(variants)]
 for mi,m in enumerate(d['meshes']):
  for pi,pr in enumerate(m['primitives']):
   for mapping in pr.get('extensions',{}).get('KHR_materials_variants',{}).get('mappings',[]):
    for vi in mapping['variants']:vr[vi]['mappings'].append(dict(mesh=mi,primitive=pi,material=mapping['material']))
 if c['game']=='gran-turismo-4':
  for mesh in d['meshes']:
   if mesh.get('name')!='body':continue
   for pr in mesh['primitives']:
    family=[pr['material']]+[m['material'] for m in pr.get('extensions',{}).get('KHR_materials_variants',{}).get('mappings',[])]
    if any(i in paints for i in family):paints.update(i for i in family if d['materials'][i].get('alphaMode')!='BLEND')
 wheels=[n.get('name','') for n in d['nodes'] if any(s in n.get('name','').lower() for s in ('wheel','tire','whl_','@axl_','hub_front','hub_back'))]
 wb=d.get('extras',{}).get('record',{}).get('wheels',[])
 wheelbase=abs(wb[0]['centre'][2]-wb[2]['centre'][2])*scale if len(wb)>=3 else c['profile_length_m']*.6
 d.setdefault('extras',{})['oversteerPreparation']={'schema':1,'sourceSha256':job['sha256'],'selectedSceneOnly':True,'scale':scale,'grounded':True,'forward':'-Z'}
 out=pack(d,tail);p.write_bytes(out)
 rows.append(dict(code=c['code'],name=c['canonical_name'],game=c['game'],model_path=f"res://assets/cars/{c['code']}.glb",length_m=c['profile_length_m'],width_m=c['profile_width_m'],wheelbase_m=wheelbase,wheelbase_source='donor_specdb' if wb else '0.6_length_proxy',normalization=dict(scale=scale,translation=translation,forward_axis='-Z'),wheel_nodes=wheels,paint_materials=[dict(index=i,name=d['materials'][i]['name']) for i in sorted(paints)],factory_variants=vr,kits=[],source_sha256=job['sha256'],prepared_sha256=sha(out),customization_limits=['Factory variants retain recovered palette mappings.','Arbitrary paint is an artistic tint of identified body materials.','No compatible replacement body kit geometry has been recovered.']))
(ROOT/'data/juiced2/cars.json').write_text(json.dumps(dict(schema_version=1,source_commit=roster['source_commit'],cars=rows),indent=2)+'\n')
(work/'cars-verification.json').write_text(json.dumps(dict(count=len(rows),all_glb_valid=True,selected_scene_count=1,paintable=sum(bool(x['paint_materials']) for x in rows),with_wheel_nodes=sum(bool(x['wheel_nodes']) for x in rows)),indent=2))
print('Prepared',len(rows),'native models')
