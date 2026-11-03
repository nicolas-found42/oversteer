"""Translate additional explicit flat GT4 glass/semantic marker atlases to PBR.

Native GS framebuffer shader semantics are not reproduced. This authored preview
translation preserves geometry/UVs and ordinary texture art; flat cyan/blue glass
markers become neutral transparent texels, and red ID texels in the same blue
semantic atlas are suppressed to reveal the existing native body underlayer.
"""
import json,struct,io,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[3];path=ROOT/'data/juiced2/cars.json';cars=json.loads(path.read_text());report=[]
for car in cars['cars']:
 if car['game']!='gran-turismo-4':continue
 p=ROOT/'godot/assets/cars'/f"{car['code']}.glb";raw=p.read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);binary=bytearray(raw[28+size:]);images={};changed=[]
 original=(ROOT/'artifacts/carmodels-research/models'/f"{car['code']}.glb").read_bytes();on=struct.unpack_from('<I',original,12)[0];od=json.loads(original[20:20+on]);ob=original[28+on:]
 for mid,m in enumerate(d['materials']):
  if m.get('alphaMode')!='BLEND':continue
  ti=m.get('pbrMetallicRoughness',{}).get('baseColorTexture',{}).get('index')
  if ti is None:continue
  image=d['textures'][ti]['source']
  if image in images:continue
  images[image]=True;view=od['bufferViews'][od['images'][image]['bufferView']];start=view.get('byteOffset',0);im=Image.open(io.BytesIO(ob[start:start+view['byteLength']])).convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype(int);cyan=(rgb[:,:,0]<=12)&(rgb[:,:,1]>=150)&(rgb[:,:,1]<=170)&(abs(rgb[:,:,1]-rgb[:,:,2])<5)&(a[:,:,3]>200);blue=(rgb[:,:,0]<12)&(rgb[:,:,1]>=30)&(rgb[:,:,1]<=48)&(rgb[:,:,2]>245)&(a[:,:,3]>200)
  prior_semantic=any(r['image']==image and r.get('suppressed_semantic_red_pixels',0)>0 for r in d.get('extras',{}).get('oversteerMarkerGlassTranslation',[]))
  iscyan=cyan.sum()>a.shape[0]*a.shape[1]*.20;isblue=blue.sum()>a.shape[0]*a.shape[1]*.20
  if not(iscyan or isblue or prior_semantic):continue
  mask=cyan if iscyan else blue;a[mask]=[8,12,16,235]
  red=(rgb[:,:,0]>100)&(rgb[:,:,1]<80)&(rgb[:,:,2]<80)if isblue else np.zeros(mask.shape,dtype=bool);a[red,3]=0
  if isblue or prior_semantic:a[:,:,:3]=0;a[:,:,3]=0;a[blue]=[8,12,16,235]
  result=Image.fromarray(a);buffer=io.BytesIO();result.save(buffer,format='PNG');data=buffer.getvalue()
  while len(binary)%4:binary.append(0)
  d['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(data)));binary.extend(data);d['images'][image]['bufferView']=len(d['bufferViews'])-1;d['images'][image].setdefault('extras',{})['oversteerMarkerTranslation']='Authored neutral PBR glass for explicit original uniform cyan/blue marker; native GS semantic red pass suppressed only when blue-ID atlas present';changed.append(dict(image=image,first_material=mid,glass_pixels=int(mask.sum()),suppressed_semantic_red_pixels=int(red.sum())if not prior_semantic else im.width*im.height,semantic_id_pass_suppressed=bool(isblue or prior_semantic)))
 if not changed:continue
 d['buffers'][0]['byteLength']=len(binary);d.setdefault('extras',{})['oversteerMarkerGlassTranslation']=changed;j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4)
 while len(binary)%4:binary.append(0)
 result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;p.write_bytes(result);car['prepared_sha256']=hashlib.sha256(result).hexdigest();report.append(dict(code=car['code'],changes=changed));print(car['code'],len(changed),flush=True)
path.write_text(json.dumps(cars,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(path.read_bytes());(ROOT/'artifacts/juiced2-build/gt4-marker-glass-verification.json').write_text(json.dumps(report,indent=2)+'\n')
