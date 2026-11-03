"""Stage exact native tree texture bindings omitted by lowercase base selection."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORLD=ROOT/'godot/assets/worlds';OUT=ROOT/'artifacts/juiced2-build/tree-materials';OUT.mkdir(exist_ok=True);reports=[]
for path in sorted(WORLD.glob('*.glb')):
 raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);tail=raw[20+length:];changes=[]
 for material in doc.get('materials',[]):
  extra=material.get('extras',{});shader=extra.get('nativeShader');parameter={'TreeBark':'BarkTexture','TreeFrond':'FrondTexture','TreeLeaves':'LeafTexture'}.get(shader)
  if parameter is None:continue
  tid=extra.get('nativeTextureBindings',{}).get(parameter)
  if tid is None:continue
  # Existing texture URI proves the city library; tree bindings were already decoded.
  city=path.stem.split('_')[0]
  catalog=json.loads((WORLD/'render-contract.json').read_text())['worlds'].get(path.name,city)
  uri=f'textures/{catalog}/{tid}.png';assert(WORLD/uri).exists(),uri
  source=next((i for i,image in enumerate(doc.get('images',[]))if image.get('uri')==uri),None)
  if source is None:source=len(doc.setdefault('images',[]));doc['images'].append({'uri':uri})
  texture=next((i for i,row in enumerate(doc.get('textures',[]))if row.get('source')==source),None)
  if texture is None:texture=len(doc.setdefault('textures',[]));doc['textures'].append({'source':source})
  before=dict(material.get('pbrMetallicRoughness',{}));material.setdefault('pbrMetallicRoughness',{}).update(baseColorTexture={'index':texture},baseColorFactor=[1,1,1,1]);material['alphaMode']='MASK';material['alphaCutoff']=.3
  extra['baseTextureId']=tid;extra['translation']='Exact native '+parameter+' RGBA binding; MASK0.3 remains reconstructed PBR pass.'
  changes.append(dict(material=material['name'],shader=shader,native_parameter=parameter,texture_id=tid,texture_uri=uri,before=before))
 if not changes:continue
 doc.setdefault('extras',{})['oversteerTreeTextureBinding']={'source':'native exact BarkTexture/FrondTexture/LeafTexture parameters','limits':['MASK0.3 follows existing PBR fallback; native SpeedTree wind/billboard/pass state remains unresolved.']}
 payload=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();payload+=b' '*(-len(payload)%4);result=struct.pack('<4sIIII',b'glTF',2,20+len(payload)+len(tail),len(payload),0x4e4f534a)+payload+tail;(OUT/path.name).write_bytes(result)
 reports.append(dict(file=path.name,before_sha256=hashlib.sha256(raw).hexdigest(),staged_sha256=hashlib.sha256(result).hexdigest(),changes=changes))
(OUT/'manifest.json').write_text(json.dumps(reports,indent=2)+'\n');print('Staged',len(reports),'worlds;',sum(len(r['changes'])for r in reports),'exact native tree material bindings; runtime unchanged')
