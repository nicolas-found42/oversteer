"""Derive GT4 paint masks from actual factory-variant texture/color differences.

Static lamp, chrome and trim texels do not enter the mask merely because they
have a specular material. Mask generation is a documented adaptation of source
factory palette variation, not a recovered arbitrary-paint shader.
"""
import json,struct,io,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];path=ROOT/'data/juiced2/cars.json';catalog=json.loads(path.read_text());staged='--stage'in sys.argv;out=ROOT/('artifacts/juiced2-build/donor-pass-audit/paint_masks'if staged else'godot/assets/paint_masks');out.mkdir(exist_ok=True,parents=True);report=[]
for car in catalog['cars']:
 if car['game']!='gran-turismo-4':continue
 raw=(ROOT/'godot/assets/cars'/f"{car['code']}.glb").read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);binary=raw[28+size:];selected={};families=[]
 def image_for(mid,linear=False):
  m=d['materials'][mid];p=m.get('pbrMetallicRoughness',{});ti=p.get('baseColorTexture',{}).get('index')
  if ti is None:return np.ones((1,1,4),dtype=np.float32)*np.asarray(p.get('baseColorFactor',[1]*4))
  im=d['images'][d['textures'][ti]['source']];v=d['bufferViews'][im['bufferView']];im=Image.open(io.BytesIO(binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])).convert('RGBA');pixels=np.asarray(im,dtype=np.float32)/255
  if linear:pixels[:,:,:3]=np.where(pixels[:,:,:3]<=.04045,pixels[:,:,:3]/12.92,((pixels[:,:,:3]+.055)/1.055)**2.4)
  return pixels*np.asarray(p.get('baseColorFactor',[1]*4))
 for mesh in d['meshes']:
  if mesh.get('name')!='body':continue
  for prim in mesh['primitives']:
   mids=sorted(set([prim['material']]+[m['material']for m in prim.get('extensions',{}).get('KHR_materials_variants',{}).get('mappings',[])]));mids=[i for i in mids if d['materials'][i].get('alphaMode')!='BLEND']
   if len(mids)<2:continue
   ims=[image_for(i)for i in mids]
   if len({im.shape for im in ims})!=1:continue
   # Native finish-bearing paint alpha is not opacity. The pinned material
   # repair keeps every nonzero texel (cutoff 1/255); .5 discarded valid hood,
   # roof and bumper paint even though their factory chroma clearly changes.
   stack=np.stack(ims);delta=np.ptp(stack[:,:,:,:3],axis=0).max(axis=2);mask=(delta>.10)&(stack[:,:,:,3].min(axis=0)>0)
   if mask.sum()<max(1,mask.size*.005):continue
   # Discard monochrome intensity-only differences (e.g. headlight/specular palettes).
   chroma=np.ptp(stack[:,:,:,:3]-stack[:,:,:,:3].mean(axis=3,keepdims=True),axis=0).max(axis=2)
   mask&=chroma>.045
   if mask.sum()<max(1,mask.size*.005):continue
   name=f"{car['code']}-family-{mids[0]}.png";Image.fromarray((mask*255).astype('uint8')).save(out/name)
   for mid,im in zip(mids,ims):selected[mid]=dict(index=mid,name=d['materials'][mid]['name'],mask_path=f'res://assets/paint_masks/{name}',factory_rgb=np.mean(im[:,:,:3][mask],axis=0).tolist(),factory_luma_linear=float(np.mean(image_for(mid,True)[:,:,:3][mask],axis=0)@np.array([.2126,.7152,.0722])),mask_source='GT4 original factory texture/color palette differences; static texels excluded')
   families.append(dict(materials=mids,masked_pixels=int(mask.sum()),pixels=int(mask.size)))
 car['paint_materials']=list(selected.values());car['paint_isolation']='Original factory-variant palette difference masks; specular strength alone is not paint evidence';report.append(dict(code=car['code'],paint_materials=len(selected),families=families));print(car['code'],len(selected),flush=True)
if staged:
 (out.parent/'staged-paint-cars.json').write_text(json.dumps(catalog,indent=2)+'\n');(out.parent/'staged-paint-mask-verification.json').write_text(json.dumps(report,indent=2)+'\n')
else:
 path.write_text(json.dumps(catalog,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(path.read_bytes());(ROOT/'artifacts/juiced2-build/gt4-paint-mask-verification.json').write_text(json.dumps(report,indent=2)+'\n')
