"""Extract original JFS UI bitmap members and retain source/layout anchors."""
import sys,json,struct,zlib,hashlib,re
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.game.assets.xenos_texture import decode
src=ROOT/'artifacts/juiced2-build/ui';out=ROOT/'godot/assets/ui/native';rows=[];texts=[];errors=[]
for bank in ['ui','ui_frontend','ui_ingame','textures']:
 h=(src/(bank+'.jfshdr')).read_bytes();archive=(src/(bank+'.jfs')).read_bytes();dest=out/bank;dest.mkdir(parents=True,exist_ok=True)
 for i in range(struct.unpack_from('>I',h)[0]):
  key,o,n,u,*_=struct.unpack_from('>6I',h,4+i*24)
  try:b=zlib.decompress(archive[o:o+n]);assert len(b)==u
  except Exception:continue
  if b.startswith(b'[Begin') or b.startswith(b'<?xml') or b.startswith(b'UI.'):
   text=b.decode(errors='replace');tp=src/'typed-layouts'/bank;tp.mkdir(parents=True,exist_ok=True);(tp/f'{key:08x}.txt').write_text(text);texts.append(dict(bank=bank,member=i,key=f'{key:08x}',path=str((tp/f'{key:08x}.txt').relative_to(ROOT)),labels=re.findall(r'(?im)^.*(?:text|texture|image|font|position|size|button|screen).*$' ,text)[:100]));continue
  if len(b)<40:continue
  fmt,w,height=struct.unpack_from('>3I',b)
  if fmt&63 not in [6,18,19,20] or not 1<=w<=4096 or not 1<=height<=4096:continue
  try:im=decode(b[40:],w,height,fmt)
  except Exception as e:errors.append(dict(bank=bank,key=f'{key:08x}',error=str(e)));continue
  if im is None:continue
  path=dest/f'{key:08x}.png';im.save(path);rows.append(dict(bank=bank,member=i,key=f'{key:08x}',path=f'res://assets/ui/native/{bank}/{key:08x}.png',width=w,height=height,format=hex(fmt),source_offset=o,source_decoded_sha256=hashlib.sha256(b).hexdigest(),interpretation='native top-mip texture; Xenos tiling/endian translated'))
 print(bank,len([r for r in rows if r['bank']==bank]),flush=True)
(out/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n');(src/'typed-layouts.json').write_text(json.dumps(texts,indent=2)+'\n');(src/'texture-errors.json').write_text(json.dumps(errors,indent=2)+'\n')
for kind,chosen in [('wide',[r for r in rows if r['width']>=r['height']*3 and r['width']>=128]),('icons',[r for r in rows if .5<=r['width']/r['height']<=2 and 24<=r['width']<=256])]:
 for batch in range((len(chosen)+159)//160):
  subset=chosen[batch*160:(batch+1)*160];sheet=Image.new('RGB',(1280,((len(subset)+9)//10)*110),(30,35,45));draw=ImageDraw.Draw(sheet)
  for j,r in enumerate(subset):
   im=Image.open(ROOT/'godot'/r['path'].replace('res://',''));im.thumbnail((120,80));x=j%10*128;y=j//10*110;sheet.paste(im,(x,y),im);draw.text((x,y+82),r['bank'][:3]+' '+r['key'],fill='white')
  sheet.save(src/f'{kind}-contact-{batch:02d}.png')
print('Recovered',len(rows),'native UI textures;',len(texts),'typed layout members;',len(errors),'decode errors')
