"""Restore exact VDL-bound source UV channels without changing geometry."""
import json,struct,re,math,hashlib,sys
from pathlib import Path
from native_vertex_declarations import declarations
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/world-uv';OUT.mkdir(exist_ok=True);inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());files={r['path'].lower():r for r in inv['files']};sources={};reports=[]
contract_path=ROOT/'godot/assets/worlds/render-contract.json';contracts=json.loads(contract_path.read_text())if contract_path.exists()else dict(worlds={},catalogs={})
with open(inv['iso'],'rb')as iso:
 for path in (ROOT/'godot/assets/worlds').glob('*.glb'):
  raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);source=doc.get('extras',{}).get('source')
  if not source or not source.lower().endswith('geom.bdl'):continue
  if '--tunnel-only'in sys.argv and'/tunnel/'not in source.lower():continue
  if '--only-file'in sys.argv and path.name!=sys.argv[sys.argv.index('--only-file')+1]:continue
  if source not in sources:
   row=files[source.lower()];iso.seek(row['offset']);geometry=iso.read(row['size']);vname=source[:-8]+'.vdl';row=files[vname.lower()];iso.seek(row['offset']);vdl=iso.read(row['size']);sources[source]=(geometry,declarations(vdl),hashlib.sha256(vdl).hexdigest(),vname)
  geometry,decls,vsha,vname=sources[source];sections=struct.unpack_from('>4I',geometry);vertexstart=sum(sections[:3]);binary=bytearray(raw[28+size:]);changes=[];catalog_id=re.sub('[^a-z0-9]+','_',source.split('/')[1].lower()).strip('_')
  for mesh in doc['meshes']:
   match=re.fullmatch(r'native_(\d+)_(\d+)',mesh.get('name',''))
   if not match:continue
   mi,gi=map(int,match.groups());descriptor=sections[0]+struct.unpack_from('>I',geometry,20+mi*60+12)[0]+gi*92;stride,n,vo,di=struct.unpack_from('>4I',geometry,descriptor+76);assert di<len(decls)
   channels=[]
   for entry in decls[di]:
    if entry['usage']!=5:continue
    assert entry['format']==0x002c235f and entry['offset']+4<=stride
    uv=[struct.unpack_from('>2e',geometry,vertexstart+vo+i*stride+entry['offset'])for i in range(n)];invalid=[i for i,v in enumerate(uv)if not all(math.isfinite(x)for x in v)]
    if invalid:
     for primitive in mesh['primitives']:primitive['attributes'].pop('TEXCOORD_'+str(entry['index']),None)
     channels.append(dict(semantic_index=entry['index'],offset=entry['offset'],format=hex(entry['format']),status='original_nonfinite_channel_omitted',invalid_vertex_indices=invalid,limits='Declared source channel contains native infinities/NaNs; shader consumption unknown. No replacement UV values invented.'));continue
    while len(binary)%4:binary.append(0)
    vi=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=n*8,target=34962));binary.extend(b''.join(struct.pack('<2f',*v)for v in uv));ai=len(doc['accessors']);doc['accessors'].append(dict(bufferView=vi,componentType=5126,count=n,type='VEC2'))
    for primitive in mesh['primitives']:assert doc['accessors'][primitive['attributes']['POSITION']]['count']==n;primitive['attributes']['TEXCOORD_'+str(entry['index'])]=ai
    channels.append(dict(semantic_index=entry['index'],offset=entry['offset'],format=hex(entry['format']),min=[min(v[j]for v in uv)for j in range(2)],max=[max(v[j]for v in uv)for j in range(2)]))
   changes.append(dict(mesh=mesh['name'],stride=stride,declaration=di,channels=channels))
   for primitive in mesh['primitives']:
    primitive.setdefault('extras',{})['nativeTexcoordAccessors']={k:v for k,v in primitive['attributes'].items()if k.startswith('TEXCOORD_')}
    if '--layered-tarmac'in sys.argv and doc['materials'][primitive['material']].get('extras',{}).get('nativeShader','').lower()=='tarmac':
     assert'TEXCOORD_2'in primitive['attributes'];primitive['attributes']['TEXCOORD_1']=primitive['attributes']['TEXCOORD_2']
  translated=[]
  for material in doc['materials']:
   ex=material.get('extras',{})
   if ex.get('nativeShader','').lower()!='tarmac':continue
   bindings=ex.get('nativeTextureBindings',{});base=bindings.get('tarmacTexture');marks=bindings.get('markingsTexture')
   if base is None:continue
   uri=f'textures/{catalog_id}/{base}.png';image=next((i for i,r in enumerate(doc.get('images',[]))if r.get('uri')==uri),None)
   if image is None:continue
   texture=next((i for i,r in enumerate(doc['textures'])if r['source']==image),None);assert texture is not None
   row=dict(name=material['name'],base_texture_path='res://assets/worlds/'+uri,markings_texture_path=f'res://assets/worlds/textures/{catalog_id}/{marks}.png'if marks is not None else None,native_scalars=ex.get('nativeScalars',{}),base_uv_native=0,markings_uv_native=2,godot_uv2_native=2 if'--layered-tarmac'in sys.argv else 1,limits=['Original texture art, UV attributes and parameter values are recovered.','Base-on-UV0 plus markings-on-UV2 is an explicit layered PBR translation; full native shader sampling/scale/blend expression is not claimed.'])
   translated.append(row)
   if '--layered-tarmac'in sys.argv:material['pbrMetallicRoughness']['baseColorTexture']={'index':texture};ex['roadTranslation']='Original tarmac texture restored; original VDL UV0 and nativeUV2 mapped to Godot secondUV for separate native markings layer; native shader sampling expression remains reconstructed.'
  contracts['worlds'][path.name]=catalog_id;contracts['catalogs'][catalog_id]=dict(materials_path=f'res://assets/worlds/{catalog_id}-materials.json',texture_directory=f'res://assets/worlds/textures/{catalog_id}',tarmac=translated,vdl=vname,vdl_sha256=vsha)
  evidence=dict(source=source,vdl=vname,vdl_sha256=vsha,source_glb_sha256=hashlib.sha256(raw).hexdigest(),draws=changes,limits=['Exact original VDL declaration index at draw descriptor+88, semantic5 TEXCOORD, native half2 format.','Geometry positions, indices, transforms and material bindings are unchanged.','Original layered shader UV selection/scrolling remains separate from source attribute recovery.'])
  doc['extras']['nativeVertexDeclarations']=dict(vdl=vname,sha256=vsha,texcoord_usage=5,format='0x002c235f half2',descriptor_declaration_offset=88);doc['buffers'][0]['byteLength']=len(binary);j=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;(OUT/path.name).write_bytes(result);reports.append(dict(path=path.name,**evidence))
  if '--publish'in sys.argv:path.write_bytes(result)
(OUT/'report.json').write_text(json.dumps(reports,indent=2)+'\n');(OUT/'render-contract.json').write_text(json.dumps(contracts,indent=2)+'\n')
if '--publish'in sys.argv:contract_path.write_text(json.dumps(contracts,indent=2)+'\n')
print('Published'if'--publish'in sys.argv else'Staged',len(reports),'worlds with exact original VDL UV channels')
