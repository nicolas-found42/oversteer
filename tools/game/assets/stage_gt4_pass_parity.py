"""Stage the pinned donor viewer's GT4 pass/culling rules; --publish opts in.

This changes no texture bytes, paint masks, geometry coordinates or variant IDs.
The source viewer omits mat-1 BLEND overlay redraws and forces front-facing body
materials. It is a static-preview translation, not native GS shader emulation.
"""
import json,re,struct,hashlib,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit'
OUT.mkdir(exist_ok=True)
SOURCE='https://github.com/nicolas-found42/carmodels/blob/ce047799fc550cdf92e4f7b62d97ef5c603e53ad/dealership/materials.mjs'
report=[]
catalog_path=ROOT/'data/juiced2/cars.json';catalog=json.loads(catalog_path.read_text())
for car in catalog['cars']:
 if car['game']!='gran-turismo-4':continue
 path=ROOT/'godot/assets/cars'/f"{car['code']}.glb"
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0]
 doc=json.loads(raw[20:20+size]);tail=raw[20+size:]
 overlays=[];culled=[];removed=[]
 for index,material in enumerate(doc['materials']):
  name=material.get('name','')
  if re.search(r'_body_.*_mat-1(?:\+vc)?_BLEND_',name):overlays.append(index)
  if re.match(r'material_\d+_body_',name) and material.get('doubleSided',False):
   material['doubleSided']=False;culled.append(index)
 for mesh_index,mesh in enumerate(doc['meshes']):
  keep=[]
  for primitive_index,primitive in enumerate(mesh['primitives']):
   if primitive.get('material')in overlays:
    removed.append({'mesh':mesh_index,'primitive':primitive_index,'material':primitive['material']})
   else:keep.append(primitive)
  if not keep:raise ValueError('Source parity would leave an empty mesh: '+car['code'])
  mesh['primitives']=keep
 evidence={'code':car['code'],'source_sha256':hashlib.sha256(raw).hexdigest(),'source_rule_url':SOURCE,'removed_overlay_primitives':removed,'front_facing_body_materials':culled,'claim_limits':['Exact pinned static viewer pass/culling parity only.','No claim of recovered native GT4 glass shading or paint isolation.','Requires actual native before/after visual review before publishing.']}
 doc.setdefault('extras',{})['oversteerStagedPassParity']=evidence
 payload=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();payload+=b' '*((-len(payload))%4)
 result=struct.pack('<4sIIII',b'glTF',2,20+len(payload)+len(tail),len(payload),0x4e4f534a)+payload+tail
 (OUT/path.name).write_bytes(result);report.append(evidence)
 if '--publish'in sys.argv:
  path.write_bytes(result);car['prepared_sha256']=hashlib.sha256(result).hexdigest();car['donor_pass_parity']=evidence
  for variant in car['factory_variants']:variant['mappings']=[]
  for mi,mesh in enumerate(doc['meshes']):
   for pi,primitive in enumerate(mesh['primitives']):
    for mapping in primitive.get('extensions',{}).get('KHR_materials_variants',{}).get('mappings',[]):
     for vi in mapping['variants']:car['factory_variants'][vi]['mappings'].append({'mesh':mi,'primitive':pi,'material':mapping['material']})
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if '--publish'in sys.argv:
 catalog_path.write_text(json.dumps(catalog,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(catalog_path.read_bytes())
print('Published'if'--publish'in sys.argv else'Staged',len(report),'GT4 cars;',sum(len(r['removed_overlay_primitives'])for r in report),'overlay draws omitted')
