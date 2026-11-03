"""Translate native tarmac's road UV channel and original texture layers to PBR.

This is an explicit preview translation, not native Xbox shader execution.
"""
import json,struct,re,math
from pathlib import Path
from PIL import Image
from native_vertex_declarations import declarations
ROOT=Path(__file__).resolve().parents[3];inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());catalog=ROOT/'artifacts/juiced2-build/world-catalogs';out=ROOT/'godot/assets/worlds';reports=[]
with open(inv['iso'],'rb')as iso:
 for f in inv['files']:
  if not f['path'].endswith('Geom.bdl'):continue
  city=re.sub('[^a-z0-9]+','_',f['path'].split('/')[1].lower()).strip('_');p=catalog/(city+'.glb');raw=p.read_bytes();js=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+js]);binary=bytearray(raw[28+js:]);iso.seek(f['offset']);source=iso.read(f['size']);sections=struct.unpack_from('>4I',source);vertexstart=sum(sections[:3]);changes=0;materials=0
  vdl=next(x for x in inv['files']if x['path'].lower()==f['path'].replace('Geom.bdl','.vdl').lower());iso.seek(vdl['offset']);decls=declarations(iso.read(vdl['size']))
  for mesh in d['meshes']:
   mi,gi=map(int,re.match(r'native_(\d+)_(\d+)',mesh['name']).groups());header=20+mi*60;do=struct.unpack_from('>I',source,header+12)[0];at=sections[0]+do+gi*92;stride,n,vo=struct.unpack_from('>3I',source,at+76)
   for pr in mesh['primitives']:
    mat=d['materials'][pr['material']];ex=mat.get('extras',{})
    if ex.get('nativeShader','').lower()!='tarmac' or stride<32:continue
    di=struct.unpack_from('>I',source,at+88)[0];entry=next(e for e in decls[di]if e['usage']==5 and e['index']==2);assert entry['format']==0x002c235f
    uv=[struct.unpack_from('>2e',source,vertexstart+vo+i*stride+entry['offset'])for i in range(n)]
    if not all(math.isfinite(x)for pair in uv for x in pair):continue
    while len(binary)%4:binary.append(0)
    view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':n*8,'target':34962});binary.extend(b''.join(struct.pack('<2f',*x)for x in uv));accessor=len(d['accessors']);d['accessors'].append({'bufferView':view,'componentType':5126,'count':n,'type':'VEC2'});pr.setdefault('extras',{})['nativeTexcoordAccessors']={k:v for k,v in pr['attributes'].items()if k.startswith('TEXCOORD_')};pr['attributes']['TEXCOORD_0']=accessor;changes+=1
  for mat in d['materials']:
   ex=mat.get('extras',{})
   if ex.get('nativeShader','').lower()!='tarmac':continue
   binding=ex.get('nativeTextureBindings',{});tarmac=binding.get('tarmacTexture');markings=binding.get('markingsTexture');texture_dir=out/'textures'/city
   if tarmac is None or not(texture_dir/f'{tarmac}.png').exists():continue
   base=Image.open(texture_dir/f'{tarmac}.png').convert('RGBA');marks=Image.open(texture_dir/f'{markings}.png').convert('RGBA')if markings is not None and(texture_dir/f'{markings}.png').exists()else None
   if marks:
    target=Image.new('RGBA',marks.size)
    for y in range(0,marks.height,base.height):
     for x in range(0,marks.width,base.width):target.paste(base,(x,y))
    marks.putalpha(marks.getchannel('A').point(lambda a:min(255,a*5)));target=Image.alpha_composite(target,marks);filename=f'tarmac-composite-{ex["nativeMaterialId"]}.png';target.save(texture_dir/filename);image=len(d['images']);d['images'].append({'uri':f'textures/{city}/{filename}'});texture=len(d['textures']);d['textures'].append({'source':image});mat['pbrMetallicRoughness']['baseColorTexture']={'index':texture};mat['pbrMetallicRoughness']['baseColorFactor']=[1,1,1,1];mat['alphaMode']='OPAQUE';mat.pop('alphaCutoff',None);mat['pbrMetallicRoughness']['roughnessFactor']=.94;ex['roadTranslation']='Native road UV1; original tarmac/markings static PBR composite, markings alpha gain5 artistic; native lighting/interpolation shader not emulated';materials+=1
  d['buffers'][0]['byteLength']=len(binary);j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;p.write_bytes(result);reports.append(dict(city=city,road_uv_draws=changes,layered_materials=materials));print(city,changes,materials,flush=True)
(ROOT/'artifacts/juiced2-build/native-road-materials.json').write_text(json.dumps(reports,indent=2))
