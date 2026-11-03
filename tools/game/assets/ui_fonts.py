"""Recover native A8L8 font atlases/metrics into Godot-compatible BMFont."""
import sys,json,struct,zlib,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.game.assets.xenos_texture import untile
source=ROOT/'artifacts/juiced2-build/ui';out=ROOT/'godot/assets/ui/native/fonts';out.mkdir(parents=True,exist_ok=True);rows=[]
for bank in ['ui','ui_frontend','ui_ingame','textures']:
 h=(source/(bank+'.jfshdr')).read_bytes();archive=(source/(bank+'.jfs')).read_bytes()
 for member in range(struct.unpack_from('>I',h)[0]):
  key,o,n,u,*_=struct.unpack_from('>6I',h,4+member*24)
  try:b=zlib.decompress(archive[o:o+n])
  except zlib.error:continue
  if len(b)<32:continue
  count=struct.unpack_from('>I',b)[0];at=12+count*48
  if not 16<=count<=2048 or at+12>len(b):continue
  pages=struct.unpack_from('>I',b,at)[0]
  if not 1<=pages<=128:continue
  glyphs=[struct.unpack_from('>2H6i4fI',b,12+i*48) for i in range(count)];cursor=at+4;images=[];valid=True
  for page in range(pages):
   if cursor+8>len(b):valid=False;break
   w,height=struct.unpack_from('>2I',b,cursor);cursor+=8
   if not 16<=w<=2048 or not 16<=height<=2048 or cursor+w*height*2>len(b):valid=False;break
   raw=untile(b[cursor:cursor+w*height*2],w,height,2,1);cursor+=w*height*2;im=Image.new('RGBA',(w,height),'white');im.putalpha(Image.frombytes('L',(w,height),raw[0::2]));images.append(im)
  if not valid or cursor!=len(b):continue
  name=f'{bank}-{key:08x}';baseline=max(-g[5] for g in glyphs);lineheight=max(g[3] for g in glyphs)+2;w,height=images[0].size
  for i,im in enumerate(images):im.save(out/f'{name}-{i}.png')
  lines=[f'info face="Juiced2 {name}" size={lineheight} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0',f'common lineHeight={lineheight} base={baseline} scaleW={w} scaleH={height} pages={pages} packed=0']
  lines.extend(f'page id={i} file="{name}-{i}.png"' for i in range(pages));lines.append(f'chars count={len(glyphs)+(0 if any(g[0]==32 for g in glyphs) else 1)}')
  for g in glyphs:
   code,page,gw,gh,xoff,yoff,advance,unknown,u0,v0,u1,v1,unused=g;page=unused;assert 0<=page<pages;w,height=images[page].size;x=round(u0*w);y=round(v0*height);width=round((u1-u0)*w);hh=round((v1-v0)*height)
   lines.append(f'char id={code} x={x} y={y} width={max(0,width)} height={max(0,hh)} xoffset={xoff} yoffset={baseline+yoff} xadvance={advance} page={page} chnl=15')
  if not any(g[0]==32 for g in glyphs):
   space_advance=next((g[6] for g in glyphs if g[0]==160),max(1,round(lineheight*.25)));lines.append(f'char id=32 x=0 y=0 width=0 height=0 xoffset=0 yoffset=0 xadvance={space_advance} page=0 chnl=15')
  (out/f'{name}.fnt').write_text('\n'.join(lines)+'\n');rows.append(dict(bank=bank,member=member,key=f'{key:08x}',path=f'res://assets/ui/native/fonts/{name}.fnt',glyphs=count,pages=pages,line_height=lineheight,baseline=baseline,source_offset=o,decoded_size=len(b)))
# Exact original namespace/extension recovered from native font loader 822C69E0.
from jfs_hash import filename_hash
names=['MainMenu','MainMenu_Selected','HIN_Text','HIN_Text_Small','HIN_Text_Small_NoOutline','HIN_Text_Small_Plain','HUDSpeed_Large','HUDSpeed_Small','Menu_Font','Menu_Font_Select','PromptFont','Title_HorizontalMenu','lplate','lplate_select']
bindings=[]
for label in names:
 for resolution in [480,720,1080]:
  filename=f'fonts\\{label}_{resolution}.xef';key=f'{filename_hash(filename):08x}';row=next((r for r in rows if r['key']==key and r['bank']=='ui_frontend'),next((r for r in rows if r['key']==key),None))
  if row:
   alias=out/f'{label}-{resolution}.fnt';alias.write_bytes((out/Path(row['path']).name).read_bytes());bindings.append(dict(name=label,resolution=resolution,filename=filename,key=key,path=f'res://assets/ui/native/fonts/{alias.name}'))
for alias,label in [('menu','MainMenu'),('menu-selected','MainMenu_Selected'),('hud','HIN_Text')]:
 match=next((r for r in bindings if r['name']==label and r['resolution']==1080),None)
 if match:(out/(alias+'.fnt')).write_bytes((ROOT/'godot'/match['path'].replace('res://','')).read_bytes())
(out/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'named-fonts.json').write_text(json.dumps(bindings,indent=2)+'\n');print('Recovered',len(rows),'native bitmap fonts;',len(bindings),'exact named bindings')
