"""Decode supplied Xbox360 native BDL static world geometry into glTF.

Section-size/header interpretation validated against all vertex/index bounds.
Native material indices retained; current neutral PBR is an authored preview.
"""
import json,struct,math,re,hashlib,collections,sys
from pathlib import Path
from world_indices import triangles as decode_triangles
ROOT=Path(__file__).resolve().parents[3];inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());out=ROOT/'godot/assets/worlds';out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT))
from tools.game.assets.xenos_texture import decode
from tools.game.assets.native_vertex_declarations import declarations
reports=[]
def glb(doc,binary):
 binary+=b'\0'*((-len(binary))%4);doc['buffers']=[{'byteLength':len(binary)}];j=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4)
 return struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
with open(inv['iso'],'rb') as iso:
 for f in inv['files']:
  if not f['path'].endswith('Geom.bdl'):continue
  iso.seek(f['offset']);b=iso.read(f['size']);sections=struct.unpack_from('>4I',b);count=struct.unpack_from('>I',b,16)[0];descstart=sections[0];idxstart=sum(sections[:2]);vertstart=sum(sections[:3]);ident=re.sub('[^a-z0-9]+','_',f['path'].split('/')[1].lower()).strip('_')
  doc=dict(asset={'version':'2.0','generator':'Oversteer native Xbox360 BDL decoder'},scene=0,scenes=[{'nodes':[]}],nodes=[],meshes=[],materials=[],bufferViews=[],accessors=[],extras={'source':f['path'],'sourceSha256':hashlib.sha256(b).hexdigest(),'limits':['Recovered native world geometry, original VDL-bound half UV channels and DXT albedo; PBR finish reconstructed.','Static meshes only; animated props and object placement from BOL remain separate.'],'units':'cm to metres inferred'})
  texture_file=next((x for x in inv['files'] if x['path']==f['path'].replace('Geom.bdl','Tex.bdl')),None)
  material_file=next((x for x in inv['files'] if x['path']==f['path'].replace('Geom.bdl','Mtl.bdl')),None)
  texture_bytes=b'';native_materials={};texture_cache={}
  declaration_file=next(x for x in inv['files']if x['path'].lower()==f['path'].replace('Geom.bdl','.vdl').lower());iso.seek(declaration_file['offset']);native_declarations=declarations(iso.read(declaration_file['size']))
  if texture_file:iso.seek(texture_file['offset']);texture_bytes=iso.read(texture_file['size'])
  if material_file:
   iso.seek(material_file['offset']);mb=iso.read(material_file['size']);ms,_,mc=struct.unpack_from('>3I',mb)
   for mid in range(mc):
    mo=ms+struct.unpack_from('>I',mb,16+mid*16)[0];end=ms+struct.unpack_from('>I',mb,16+(mid+1)*16)[0] if mid+1<mc else len(mb)
    shader=mb[mo:mo+32].split(b'\0')[0].decode(errors='replace');block=mb[mo:end];bindings={};scalars={}
    for match in re.finditer(rb'[A-Za-z_][A-Za-z_0-9]{2,}\0',block):
     po=match.start();parameter=match.group()[:-1].decode()
     if po<36:continue
     if po+40>len(block):continue
     ptype=struct.unpack_from('>I',block,po+32)[0]
     if ptype==5:bindings[parameter]=struct.unpack_from('>I',block,po+36)[0]
     elif ptype==2:scalars[parameter]=struct.unpack_from('>f',block,po+36)[0]
     elif ptype==6 and po+44<=len(block):scalars[parameter]=list(struct.unpack_from('>2f',block,po+36))
    tid=next((bindings[name] for name in ['baseTexture','diffuseTexture','albedoTexture','tarmacTexture','colourTexture','BarkTexture','FrondTexture','LeafTexture'] if name in bindings),None)
    native_materials[mid]=(shader,tid,bindings,scalars)
  doc['images']=[];doc['textures']=[]
  def texture(tid):
   if tid in texture_cache:return texture_cache[tid]
   texture_cache[tid]=None
   if tid is None or not texture_bytes:return None
   th,_,tc=struct.unpack_from('>3I',texture_bytes)
   if tid>=tc:return None
   fmt,w,height=struct.unpack_from('>3I',texture_bytes,12+tid*44);off=struct.unpack_from('>I',texture_bytes,52+tid*44)[0];end=struct.unpack_from('>I',texture_bytes,52+(tid+1)*44)[0] if tid+1<tc else len(texture_bytes)-th
   if w>4096 or height>4096:return None
   im=decode(texture_bytes[th+off:th+end],w,height,fmt)
   if im is None:return None
   dest=out/'textures'/ident;dest.mkdir(parents=True,exist_ok=True);im.save(dest/f'{tid}.png');tex=len(doc['textures']);doc['images'].append({'uri':f'textures/{ident}/{tid}.png'});doc['textures'].append({'source':len(doc['images'])-1});texture_cache[tid]=tex;return tex
  binary=bytearray();materials={};skips=collections.Counter();tris=0
  def append(data,target):
   while len(binary)%4:binary.append(0)
   index=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(data),'target':target});binary.extend(data);return index
  for mi in range(count):
   h=20+mi*60;indexoff,indexcount,groups,descoff=struct.unpack_from('>4I',b,h)
   for gi in range(groups):
    at=descstart+descoff+gi*92
    material,indexfirst,nindices=struct.unpack_from('>3I',b,at);stride,nverts,vertoff=struct.unpack_from('>3I',b,at+76)
    if stride<12 or stride>128 or nverts>1000000 or vertstart+vertoff+nverts*stride>len(b) or idxstart+indexoff+(indexfirst+nindices)*2>vertstart:skips['invalid_span']+=1;continue
    positions=[struct.unpack_from('>3f',b,vertstart+vertoff+i*stride) for i in range(nverts)]
    if not positions or any(not math.isfinite(v) or abs(v)>1e8 for p in positions for v in p):skips['invalid_position']+=1;continue
    indices=struct.unpack_from('>'+str(nindices)+'H',b,idxstart+indexoff+indexfirst*2)
    if any(v>=nverts and v!=65535 for v in indices):skips['index_bounds']+=1;continue
    triangles=decode_triangles(indices,struct.unpack_from('>I',b,at+12)[0])
    if not triangles:continue
    positions=[[v/100 for v in p] for p in positions];low=[min(p[i] for p in positions) for i in range(3)];high=[max(p[i] for p in positions) for i in range(3)]
    pv=append(b''.join(struct.pack('<3f',*p) for p in positions),34962);pa=len(doc['accessors']);doc['accessors'].append({'bufferView':pv,'componentType':5126,'count':nverts,'type':'VEC3','min':low,'max':high})
    uv_accessors={};declaration_index=struct.unpack_from('>I',b,at+88)[0]
    for element in native_declarations[declaration_index]:
     if element['usage']!=5:continue
     assert element['format']==0x002c235f and element['offset']+4<=stride
     uvs=[struct.unpack_from('>2e',b,vertstart+vertoff+i*stride+element['offset'])for i in range(nverts)]
     if not all(math.isfinite(v)for uv in uvs for v in uv):skips['declared_nonfinite_uv_channel_omitted']+=1;continue
     uvview=append(b''.join(struct.pack('<2f',*uv)for uv in uvs),34962);uv_accessors['TEXCOORD_'+str(element['index'])]=len(doc['accessors']);doc['accessors'].append({'bufferView':uvview,'componentType':5126,'count':nverts,'type':'VEC2'})
    iv=append(struct.pack('<'+str(len(triangles))+'I',*triangles),34963);ia=len(doc['accessors']);doc['accessors'].append({'bufferView':iv,'componentType':5125,'count':len(triangles),'type':'SCALAR'})
    if material not in materials:
     materials[material]=len(doc['materials']);doc['materials'].append({'name':f'native_material_{material}','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.38,.4,.43,1],'roughnessFactor':.85,'metallicFactor':0},'extras':{'nativeMaterialId':material,'translation':'neutral preview pending original material decoding'}})
    if material in native_materials:
     shader,tid,bindings,scalars=native_materials[material];mat=doc['materials'][materials[material]];mat['extras'].update({'nativeShader':shader,'baseTextureId':tid,'nativeTextureBindings':bindings,'nativeScalars':scalars});tex=texture(tid)
     for bound_id in bindings.values():texture(bound_id)
     if tex is not None:
      mat['pbrMetallicRoughness']['baseColorFactor']=[1,1,1,1];mat['pbrMetallicRoughness']['baseColorTexture']={'index':tex};mat['alphaMode']='MASK';mat['alphaCutoff']=.3;mat['extras']['translation']='recovered native top-mip DXT albedo; reconstructed PBR finish'
    attrs={'POSITION':pa}
    attrs.update(uv_accessors)
    doc['meshes'].append({'name':f'native_{mi}_{gi}','primitives':[{'attributes':attrs,'indices':ia,'material':materials[material]}]});doc['nodes'].append({'name':f'native_{mi}_{gi}','mesh':len(doc['meshes'])-1});doc['scenes'][0]['nodes'].append(len(doc['nodes'])-1);tris+=len(triangles)//3
  path=out/f'{ident}.glb';path.write_bytes(glb(doc,binary));(out/f'{ident}-materials.json').write_text(json.dumps([dict(name=m['name'],**m['extras'])for m in doc['materials']],indent=2)+'\n');reports.append(dict(id=ident,model_path=f'res://assets/worlds/{ident}.glb',source=f['path'],source_offset=f['offset'],sha256=hashlib.sha256(b).hexdigest(),native_mesh_count=count,decoded_draws=len(doc['meshes']),triangles=tris,skipped=dict(skips),sections=list(sections),coordinate_origin=[0,0,0],scale=.01,material_status='recovered native DXT top-mip albedo and halfUV; reconstructed PBR finish'));print(ident,len(doc['meshes']),tris,dict(skips),flush=True)
(ROOT/'data/juiced2/worlds.json').write_text(json.dumps(reports,indent=2)+'\n');(ROOT/'godot/assets/worlds.json').write_text(json.dumps(reports,indent=2)+'\n');(ROOT/'artifacts/juiced2-build/world-geometry-verification.json').write_text(json.dumps(reports,indent=2)+'\n')
