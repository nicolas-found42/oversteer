"""Stage the original Paintshop room using its recovered placement consumer.

The scene is an unchanged subset of original Garage ZDF instances. No inferred
light sources or new room geometry are authored.
"""
import copy,hashlib,json,struct,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/presentation/paintbooth-stage';OUT.mkdir(exist_ok=True);SOURCE=ROOT/'godot/assets/worlds/garage.glb';raw=SOURCE.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:];original=copy.deepcopy(doc)
root_ids=[i for i in doc['scenes'][0]['nodes'] if doc['nodes'][i]['name']in{f'instance_{i}_source_{source}' for i,source in [(6,9),(7,10),(8,11),(9,12),(10,13),(11,14),(12,15),(13,15),(14,15)]}];assert len(root_ids)==9
node_ids=[]
def visit(i):
 node_ids.append(i)
 for child in doc['nodes'][i].get('children',[]):visit(child)
for root in root_ids:visit(root)
node_map={old:new for new,old in enumerate(node_ids)};nodes=[copy.deepcopy(doc['nodes'][i])for i in node_ids];mesh_ids=sorted({node['mesh']for node in nodes if 'mesh'in node});mesh_map={old:new for new,old in enumerate(mesh_ids)};meshes=[copy.deepcopy(doc['meshes'][i])for i in mesh_ids];primitives=[p for m in meshes for p in m['primitives']];material_ids=sorted({p['material']for p in primitives});material_map={old:new for new,old in enumerate(material_ids)};materials=[copy.deepcopy(doc['materials'][i])for i in material_ids]
for node in nodes:
 if 'mesh'in node:node['mesh']=mesh_map[node['mesh']]
 if 'children'in node:node['children']=[node_map[x]for x in node['children']]
used_accessors={a for p in primitives for a in [p['indices'],*p['attributes'].values()]};accessor_map={old:new for new,old in enumerate(sorted(used_accessors))};view_ids=sorted({doc['accessors'][a]['bufferView']for a in used_accessors});view_map={old:new for new,old in enumerate(view_ids)};compact=bytearray();views=[]
for old in view_ids:
 view=copy.deepcopy(doc['bufferViews'][old]);start=view.get('byteOffset',0);compact.extend(b'\0'*(-len(compact)%4));view['byteOffset']=len(compact);compact.extend(binary[start:start+view['byteLength']]);views.append(view)
accessors=[]
for old in sorted(used_accessors):
 ac=copy.deepcopy(doc['accessors'][old]);ac['bufferView']=view_map[ac['bufferView']];accessors.append(ac)
for p in primitives:p['indices']=accessor_map[p['indices']];p['attributes']={k:accessor_map[v]for k,v in p['attributes'].items()};p['material']=material_map[p['material']]
# Preserve original image/texture/sampler indices and relative paths exactly.
doc.update(nodes=nodes,meshes=meshes,materials=materials,bufferViews=views,accessors=accessors,scenes=[dict(name='OriginalPaintshop',nodes=[node_map[i]for i in root_ids])],scene=0,buffers=[dict(byteLength=len(compact))]);doc['extras']['paintshopSourceInstances']=[original['nodes'][i]['name']for i in root_ids];doc['extras']['limits']=['Exact original native BDL/ZDF geometry subset and VDL UVs.','Existing source texture/PBR translation retained; native DLT lighting, layered shaders and visibility remain separate.'];encoded=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();encoded+=b' '*(-len(encoded)%4);compact.extend(b'\0'*(-len(compact)%4));result=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(compact))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(compact),0x004e4942)+compact;(OUT/'paintbooth.glb').write_bytes(result)
for image in doc.get('images',[]):
 if 'uri'not in image:continue
 source=SOURCE.parent/image['uri'];dest=OUT/image['uri'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
D=ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/824A0000-.data.bin';data=D.read_bytes();position=list(struct.unpack_from('>3f',data,0x824C0028-0x824A0000));rotation=list(struct.unpack_from('>3f',data,0x824C0038-0x824A0000));cameras=json.loads((ROOT/'artifacts/juiced2-build/presentation/customization-cameras.json').read_text());camera=next(c for c in cameras['cameras']if c['name'].lower()=='paintshop');floor=json.loads((ROOT/'artifacts/juiced2-build/presentation/paintbooth-floor-hits.json').read_text());near=[h for h in floor if abs(h['height']-position[1]/100)<.1];assert len(near)==2
report=dict(model_path='res://assets/worlds/paintbooth.glb',source=dict(prepared_garage_sha256=hashlib.sha256(raw).hexdigest(),bdl=doc['extras']['source'],bdl_sha256=doc['extras']['sourceSha256'],zdf=doc['extras']['sourceInstanceScene'],zdf_sha256=doc['extras']['sourceInstanceSha256'],instances=doc['extras']['paintshopSourceInstances']),binding=dict(menu_consumer='821C22D0: selected string paint at8203E900 calls8219F788(mode1,reset1), then8219DEE8(mode2)',pose_consumer='8219F388 mode1 reads824C0028/824C0038',native_position_cm=position,native_euler_radians=rotation,position_rh_m=[-position[0]/100,position[1]/100,position[2]/100],euler_rh_radians=[-rotation[0],-rotation[1],rotation[2]],lighting_preset='tracks/garage/paintbooth.dlt',lighting_selector=2),camera=dict(source=cameras['source'],**camera),render_floor_candidates=near,donor_display=dict(position_rh_m=[-30,max(h['height']for h in near),30],status='Donor ground-reference adaptation to highest unchanged source render-floor triangle at original placementXZ; native physicsCG offsets are not applied to donor renderfeet'),counts=dict(instances=9,draws=len(meshes),triangles=sum(doc['accessors'][p['indices']]['count']//3 for p in primitives)),sha256=hashlib.sha256(result).hexdigest(),limits=['Native pose setter8219F788 adds10cm then convertscm→m before physics; that is a body/CG seed, not an arbitrary donor meshground offset.','Original DLT coefficients/spatial bounds are retained evidence; no lights inferred from preset names.','Camera projection axis is under separate source trace; component-relative donor camera anchoring remains an adaptation.'])
(OUT/'venue.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['counts'],report['binding']['position_rh_m'],report['donor_display'])
