"""Author atlas paint masks for four FR2 donors, retaining lamps/glass/decals.

Reconstructed masks select connected regions near the dominant factory body hue;
small separate emblems/lamp islands are excluded. These are authored, not native.
"""
import json,struct,io,collections
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];target=ROOT/'godot/assets/paint_masks';target.mkdir(parents=True,exist_ok=True)
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());preview=Image.new('RGB',(1024,600));draw=ImageDraw.Draw(preview);report=[]
for k,code in enumerate(['FOCUS_SVT','MUSTANG_68','LIGHTNING_SVT','F100_1956']):
 b=(ROOT/'godot/assets/cars'/f'{code}.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:];view=d['bufferViews'][d['images'][0]['bufferView']];im=Image.open(io.BytesIO(binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])).convert('RGB');rgb=np.asarray(im);hsv=np.asarray(im.convert('HSV')).astype(int)
 counts=collections.Counter(tuple(x) for x in rgb.reshape(-1,3));dominant=next(col for col,_ in counts.most_common() if max(col)-min(col)>20 and max(col)>70)
 anchor=np.asarray(Image.new('RGB',(1,1),dominant).convert('HSV'))[0,0].astype(int);delta=np.abs(hsv[:,:,0]-anchor[0]);delta=np.minimum(delta,256-delta)
 candidate=(delta<=7)&(np.abs(hsv[:,:,1]-anchor[1])<=45)&(hsv[:,:,2]>35)
 visited=np.zeros(candidate.shape,bool);mask=np.zeros(candidate.shape,np.uint8);height,width=candidate.shape
 for y,x in zip(*np.nonzero(candidate)):
  if visited[y,x]:continue
  stack=[(y,x)];visited[y,x]=True;component=[]
  while stack:
   yy,xx=stack.pop();component.append((yy,xx))
   for ny,nx in [(yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)]:
    if 0<=ny<height and 0<=nx<width and candidate[ny,nx] and not visited[ny,nx]:visited[ny,nx]=True;stack.append((ny,nx))
  if len(component)>=90:
   for yy,xx in component:mask[yy,xx]=255
 if code=='LIGHTNING_SVT':mask[125:256,0:67]=0  # authored rear-light atlas exclusion
 Image.fromarray(mask).save(target/f'{code}.png');overlay=rgb.copy();overlay[mask>0]=[255,0,255];tile=Image.fromarray(overlay);tile.thumbnail((512,270));preview.paste(tile,(k%2*512,k//2*300+20));draw.text((k%2*512,k//2*300),code,fill='white')
 pixels=rgb.astype(float)/255;linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4);linear*=np.array(d['materials'][0].get('pbrMetallicRoughness',{}).get('baseColorFactor',[1]*4)[:3]);luma=float(linear[mask>0].mean(0)@np.array([.2126,.7152,.0722]))
 c=next(c for c in doc['cars'] if c['code']==code);c['paint_materials']=[dict(index=0,name=d['materials'][0]['name'],mask_path=f'res://assets/paint_masks/{code}.png',source='authored atlas mask',factory_rgb=[int(v) for v in dominant],factory_luma_linear=luma)];c['customization_limits']=list(dict.fromkeys(c['customization_limits']+['FR2 body paint mask is reconstructed from dominant atlas hue; factory artwork remains outside the mask.']))
 report.append(dict(code=code,dominant=[int(v) for v in dominant],paint_pixels=int((mask>0).sum()),atlas_pixels=width*height))
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes());preview.save(ROOT/'artifacts/juiced2-build/fr2-paint-mask-review.png');(ROOT/'artifacts/juiced2-build/fr2-paint-mask-report.json').write_text(json.dumps(report,indent=2))
print('Authored four FR2 body atlas masks')
