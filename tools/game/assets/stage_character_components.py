"""Stage original modular JSM skins against the retained common M/F rigs.

No runtime writes. Geometry, palettes, weights, material slots and additive head
positions come from source. PBR material translation is explicitly an adaptation.
"""
import copy,hashlib,json,struct,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'staged-components';OUT.mkdir(exist_ok=True);(OUT/'textures').mkdir(exist_ok=True)
catalog=json.loads((SOURCE/'component-catalog-evidence.json').read_text());slots=json.loads((SOURCE/'component-material-slots.json').read_text());slot_by={s['sha256']:s for s in slots['skins']};art=json.loads((SOURCE/'avatar-materials.json').read_text());images={r['name'].lower():r for r in art['textures']};morphs=json.loads((SOURCE/'decoded-head-morphs.json').read_text());attrs=json.loads((SOURCE/'native-morph-attributes.json').read_text());genders={s['key']:set() for s in catalog['skins']};reports=[];skin_ids={};nonrenderable=[]
for c in catalog['components']:
 for s in c['skin_bindings']:genders[s['key']].update(c['gender'])
for image in art['textures']:shutil.copyfile(ROOT/image['path'],OUT/'textures'/Path(image['path']).name)
def load(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),bytearray(raw[28+n:])
templates={g:load(ROOT/'godot/assets/characters'/name) for g,name in [('male','native_male_baggy_t.glb'),('female','native_female_zip.glb')]}
def decode_geometry(raw,vs,material_count):
 nv=struct.unpack_from('<I',raw,vs+4)[0];strides=[st for st in [68,76] if raw[vs+8+nv*st:vs+12+nv*st]==struct.pack('<I',0x70000006)];assert len(strides)==1;stride=strides[0];ix=vs+8+nv*stride
 mo=raw.rfind(struct.pack('<I',0x7000000a),0,vs);matrix=np.array(struct.unpack_from('<12f',raw,mo-48)).reshape(3,4);v=np.array([struct.unpack_from('<3f',raw,vs+8+i*stride)for i in range(nv)]);positions=(v@matrix[:,:3].T+matrix[:,3])[:,[0,2,1]]/100;uv=np.array([struct.unpack_from('<2f',raw,vs+8+i*stride+60)for i in range(nv)]);weights=np.array([struct.unpack_from('<4f',raw,vs+8+i*stride+12)for i in range(nv)]);ids=np.array([struct.unpack_from('<4B',raw,vs+8+i*stride+28)for i in range(nv)]);assert np.isfinite(positions).all() and np.isfinite(uv).all();assert np.max(abs(weights.sum(1)-1))<1e-5
 at=mo+4;assert struct.unpack_from('<I',raw,at)[0]==0x70000005;count=struct.unpack_from('<I',raw,at+4)[0];at+=8;palette=[]
 for _ in range(count):
  length=struct.unpack_from('<I',raw,at)[0];name=raw[at+4:at+4+length].split(b'\0')[0].decode();p=(at+4+length+1+3)&~3;palette.append(dict(name=name,native_inverse_bind=list(struct.unpack_from('<12f',raw,p+24))));at=p+72
 assert at==vs;assert np.max(ids[weights>0])<count
 groups=[];cursor=ix+8;ng=struct.unpack_from('<I',raw,ix+4)[0]
 for gi in range(ng):
  first=struct.unpack_from('<I',raw,cursor)[0]
  if first==0:_,nt,mid=struct.unpack_from('<3I',raw,cursor);cursor+=12
  else:nt,mid=struct.unpack_from('<2I',raw,cursor);cursor+=8
  tri=np.array(struct.unpack_from('<'+str(nt*3)+'H',raw,cursor),dtype=np.uint32).reshape(-1,3);cursor=(cursor+nt*6+15)&~15;assert tri.max()<nv and mid<material_count
  groups.append((tri,mid))
 # Original authored normals are float3 at32, unit length. Source indices areCW;
 # theY/ZreflectionalreadyconvertswindingtoCCW. Preservebothwithoutwelding.
 smooth=(np.array([struct.unpack_from('<3f',raw,vs+8+i*stride+32)for i in range(nv)])@matrix[:,:3].T)[:,[0,2,1]]
 assert np.max(abs(np.linalg.norm(smooth,axis=1)-1))<1e-6
 return dict(vs=vs,nv=nv,matrix=matrix,positions=positions,uv=uv,weights=weights,ids=ids,palette=palette,groups=groups,smooth=smooth)
for skin in catalog['skins']:
 raw=(ROOT/skin['path']).read_bytes();sha=hashlib.sha256(raw).hexdigest();source_slots=slot_by[sha]['materials'];parts=[];vs=raw.find(struct.pack('<I',0x70000007))
 while vs>=0:
  nv=struct.unpack_from('<I',raw,vs+4)[0]
  if nv and any(raw[vs+8+nv*st:vs+12+nv*st]==struct.pack('<I',0x70000006)for st in [68,76]):parts.append(decode_geometry(raw,vs,len(source_slots)))
  vs=raw.find(struct.pack('<I',0x70000007),vs+1)
 if not parts:
  nonrenderable.append(dict(source=skin,reason='Original member contains hierarchy/materials but no skinned vertex chunk70000007'));skin_ids[skin['key']]=[];continue
 for gender in sorted(genders[skin['key']] or {'male','female'}):
  doc,binary=copy.deepcopy(templates[gender]);by={doc['nodes'][n]['name']:i for i,n in enumerate(doc['skins'][0]['joints'])}
  def add(values,typ,component=5126):
   data=np.asarray(values,dtype={5126:'<f4',5125:'<u4',5121:'u1'}[component]);binary.extend(b'\0'*(-len(binary)%4));vi=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=data.nbytes));binary.extend(data.tobytes());ai=len(doc['accessors']);ac=dict(bufferView=vi,componentType=component,count=len(data),type=typ)
   if typ=='VEC3':ac.update(min=data.min(0).tolist(),max=data.max(0).tolist())
   doc['accessors'].append(ac);return ai
  doc['images']=[];doc['textures']=[];doc['materials']=[];doc['meshes']=[];material_report=[]
  for m in source_slots:
   base=Path(m['native_jtd']).stem;image=images.get(base.lower());name=f"native_slot_{m['slot']}_{base or 'empty'}";pbr=dict(baseColorFactor=[1,1,1,1],roughnessFactor=.7,metallicFactor=0)
   if image:
    ti=len(doc['textures']);doc['images'].append(dict(uri='textures/'+Path(image['path']).name));doc['textures'].append(dict(source=len(doc['images'])-1));pbr['baseColorTexture']=dict(index=ti)
   doc['materials'].append(dict(name=name,pbrMetallicRoughness=pbr,doubleSided=True,extras=dict(nativeJtd=m['native_jtd'],translation='Original image with authored neutral PBR; native cloth/HSV shader unresolved')));material_report.append(dict(slot=m['slot'],name=name,native_jtd=m['native_jtd'],base_texture_path='res://assets/characters/components/textures/'+Path(image['path']).name if image else None))
  for node in doc['nodes']:node.pop('mesh',None);node.pop('skin',None)
  morph_map=[];mesh_nodes=[]
  for part_index,part in enumerate(parts):
   nv=part['nv'];matrix=part['matrix'];positions=part['positions'];uv=part['uv'];weights=part['weights'];ids=part['ids'];palette=part['palette'];groups=part['groups'];smooth=part['smooth'];mapped=np.array([[by[palette[int(j)]['name']]if w>0 else 0 for j,w in zip(row,wr)]for row,wr in zip(ids,weights)],dtype=np.uint8)
   attributes=dict(POSITION=add(positions,'VEC3'),NORMAL=add(smooth,'VEC3'),TEXCOORD_0=add(uv,'VEC2'),JOINTS_0=add(mapped,'VEC4',5121),WEIGHTS_0=add(weights,'VEC4'));primitives=[dict(attributes=attributes.copy(),indices=add(t.reshape(-1),'SCALAR',5125),material=mid)for t,mid in groups];mesh=dict(name=skin['native_name']+'_part_'+str(part_index),primitives=primitives)
   if sha==morphs['source']['sha256']:
    targets=[]
    for target in morphs['targets']:
     values=np.zeros((nv,3));start=target['first_vertex'];end=start+target['vertex_count'];assert end<=nv;values[start:end]=(np.asarray(target['position_vectors'])@matrix[:,:3].T)[:,[0,2,1]];normal_values=np.zeros((nv,3));normal_values[start:end]=(np.asarray(target['normal_vectors'])@matrix[:,:3].T)[:,[0,2,1]]*100;targets.append(dict(POSITION=add(values,'VEC3'),NORMAL=add(normal_values,'VEC3')))
    for p in primitives:p['targets']=targets
    mesh.update(weights=[0]*len(targets),extras=dict(targetNames=[t['name']for t in morphs['targets']]));lookup={t['name'].lower():i for i,t in enumerate(morphs['targets'])};morph_map=[dict(name=a['name'],native_attribute_index=a['index'],target_index=lookup[a['name'].lower()],default_constructor_weight=0,native_level_to_render_weight=.01,export_delta_multiplier=100)for a in attrs['attributes']if a['kind']=='geometry']
   mesh_index=len(doc['meshes']);doc['meshes'].append(mesh);node_index=1 if part_index==0 else len(doc['nodes'])
   if part_index:doc['nodes'].append({});doc['nodes'][0]['children'].append(node_index)
   name=skin['native_name']+'_part_'+str(part_index);doc['nodes'][node_index].update(name=name,mesh=mesh_index,skin=0,extras=dict(nativeBonePalette=palette,nativeVertexChunkOffset=part['vs']));mesh_nodes.append(dict(index=node_index,name=name,source_vertex_chunk_offset=part['vs']))
  primitives=[primitive for mesh in doc['meshes']for primitive in mesh['primitives']]
  # Components bind to the authoritative base skeleton; clips stay on that actor.
  doc.pop('animations',None)
  used={doc['skins'][0]['inverseBindMatrices']}
  for primitive in primitives:
   used.add(primitive['indices']);used.update(primitive['attributes'].values())
   for target in primitive.get('targets',[]):used.update(target.values())
  accessor_map={old:new for new,old in enumerate(sorted(used))};view_ids=sorted({doc['accessors'][a]['bufferView']for a in used});view_map={old:new for new,old in enumerate(view_ids)};compact=bytearray();views=[]
  for old in view_ids:
   view=copy.deepcopy(doc['bufferViews'][old]);start=view.get('byteOffset',0);compact.extend(b'\0'*(-len(compact)%4));view['byteOffset']=len(compact);compact.extend(binary[start:start+view['byteLength']]);views.append(view)
  accessors=[]
  for old in sorted(used):
   accessor=copy.deepcopy(doc['accessors'][old]);accessor['bufferView']=view_map[accessor['bufferView']];accessors.append(accessor)
  for primitive in primitives:
   primitive['indices']=accessor_map[primitive['indices']];primitive['attributes']={k:accessor_map[v]for k,v in primitive['attributes'].items()}
   if 'targets'in primitive:primitive['targets']=[{k:accessor_map[v]for k,v in target.items()}for target in primitive['targets']]
  doc['skins'][0]['inverseBindMatrices']=accessor_map[doc['skins'][0]['inverseBindMatrices']];doc['accessors']=accessors;doc['bufferViews']=views;binary=compact
  doc['extras']=dict(nativeSource=skin,commonRig=gender,limits=['Geometry/weights/material references are source; common rig inverse binds are rebased as in existing actors.','NeutralPBRisadapted;originalfloat3normals/indexwindingandadditivenormalmorphsretained;nativecloth/HSVshaderseparate.','Source common actor root normalization preserved; no independent component grounding.','Morph zero weights are constructor values, not a recovered creator preset.']);doc['buffers'][0]['byteLength']=len(binary);encoded=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();encoded+=b' '*(-len(encoded)%4);binary.extend(b'\0'*(-len(binary)%4));result=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary;ident=skin['key']+'_'+gender;path=OUT/(ident+'.glb');path.write_bytes(result);skin_ids.setdefault(skin['key'],[]).append(ident);reports.append(dict(id=ident,native_name=skin['native_name'],gender_compatibility=[gender]if genders[skin['key']]else[],gender_tag='M'if gender=='male'else'F',rig=gender,model_path=f'res://assets/characters/components/{ident}.glb',materials=material_report,morph_attributes=morph_map,vertices=sum(p['nv']for p in parts),used_vertices=sum(len(set(int(i)for t,_ in p['groups']for i in t.reshape(-1)))for p in parts),triangles=sum(len(t)for p in parts for t,_ in p['groups']),bone_count=len(by),source=skin,sha256=hashlib.sha256(result).hexdigest(),rig_identity=hashlib.sha256(json.dumps([doc['nodes'][n] for n in doc['skins'][0]['joints']],sort_keys=True).encode()).hexdigest(),root_transform={k:v for k,v in doc['nodes'][0].items()if k in ['translation','rotation','scale']},mesh_node_index=1,mesh_node_name=mesh_nodes[0]['name'],mesh_nodes=mesh_nodes,animations=[],base_animation_actor='res://assets/characters/'+('native_male_baggy_t.glb'if gender=='male'else'native_female_zip.glb'),weight_sum_max_error=max(float(np.max(abs(p['weights'].sum(1)-1)))for p in parts)))
components=[]
for c in catalog['components']:
 row=copy.deepcopy(c);row['native_initial_mesh_enabled']=not any(r[0]=='hidden'for r in c['native_rows']);row['native_mesh_enable_source']='82239018 passes flags&4 to82243420, which stores !hidden at mesh-option+0';row['gender_tags']=['M'if g=='male'else'F'for g in c['gender']];row['skin_ids']=[i for s in c['skin_bindings']for i in skin_ids[s['key']]];row['availability_status']='gender/subname list candidate; unlock consumer unresolved'if c['gender'] and any(r[0]=='subname'and r[1]!='unnamed'for r in c['native_rows'])else'NPC/default or availability unresolved';row['replacement_slots']=copy.deepcopy(next(x['materials']for x in slots['components']if x['component_id']==c['id']))
 for replacement in row['replacement_slots']:
  if replacement['texture_path']:
   replacement['source_texture_path']=replacement['texture_path'];replacement['texture_path']='res://assets/characters/components/textures/'+Path(replacement['texture_path']).name
 components.append(row)
preset_report=json.loads((SOURCE/'native-avatar-presets.json').read_text());component_by={(c['category'].lower(),c['name'].lower()):c['id']for c in components if c['category']and c['name']}
for preset in preset_report['presets']:
 for component in preset['components']:component['component_id']=component_by.get((component['category'].lower(),component['native_component_name'].lower()))
 assert all(c['component_id']for c in preset['components'])
 preset['native_gender']=preset['gender'];preset['gender']='M'if preset['native_gender']=='MALE'else'F';preset['native_attributes']=preset['morph_levels'].copy();preset['native_components']={component['category'].lower():component['component_id']for component in preset['components']}
manifest=dict(schema_version=1,native_presets=preset_report,creator_controls=json.loads((SOURCE/'native-avatar-controls.json').read_text()),coordinate_contract=dict(units='metres',normalization='Same common-gender actor root and original bind-pose basis as existing complete avatars; attach at identity and do not ground or rotate individual components',preferred_attachment='Rebind exact joint names to the common gender skeleton; source clips remain on the complete base actor',base_mesh_nodes={'skin':['head'],'top':['top'],'bottom':['bottom'],'hand':['hands'],'feet':['shoes'],'hair':['hair'],'hat':[]},base_mesh_mapping_status='Prepared assembly node identities, not native outfit visibility or hat/hair exclusion rules'),skins=reports,nonrenderable=nonrenderable,components=components,limits=['Source-only staging; no runtime publication.','146 candidate records are not an all-unlocked player catalog.','Shared original rig retained; original clips remain on base actors; garment materials remain explicit adaptations; original normals and winding are retained.']);(OUT/'components.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Staged',len(reports),'rig-specific meshes from',len(catalog['skins']),'source skins;',len(components),'raw component rules')
