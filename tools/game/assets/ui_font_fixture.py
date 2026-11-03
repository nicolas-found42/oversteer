"""Render a known alphabet fixture from original glyph records and atlas pages."""
import json,struct,zlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-build/ui';out=source/'font-fixture.png';h=(source/'ui_frontend.jfshdr').read_bytes();a=(source/'ui_frontend.jfs').read_bytes();key=0x58a52e7d
entry=next(struct.unpack_from('>6I',h,4+i*24)for i in range(struct.unpack_from('>I',h)[0])if struct.unpack_from('>I',h,4+i*24)[0]==key);_,offset,p,u,*_=entry;b=zlib.decompress(a[offset:offset+p]);count=struct.unpack_from('>I',b)[0];glyphs={g[0]:g for g in [struct.unpack_from('>2H6i4fI',b,12+i*48)for i in range(count)]};canvas=Image.new('RGBA',(1150,330),(25,35,50,255));draw=ImageDraw.Draw(canvas);baseline=max(-g[5]for g in glyphs.values())
for line,text in enumerate(['ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz','0123456789 Oversteer Quick Race']):
 x=20;y=10+line*100
 for char in text:
  if char==' ':x+=20;continue
  g=glyphs[ord(char)];code,unused,gw,gh,xoff,yoff,advance,unknown,u0,v0,u1,v1,page=g;im=Image.open(ROOT/'godot/assets/ui/native/fonts'/f'ui_frontend-{key:08x}-{page}.png').convert('RGBA');w,h=im.size;crop=im.crop((round(u0*w),round(v0*h),round(u1*w),round(v1*h)));canvas.alpha_composite(crop,(x+xoff,y+baseline+yoff));x+=advance
canvas.convert('RGB').save(out);print(out)
