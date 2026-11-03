"""Cache original avatar archive members and decode source bitmap albedos."""
import struct,zlib
from pathlib import Path
from xenos_texture import decode
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-build/characters'
for bank in ['avatar_lo','componentdefs','player01']:
 h=(source/(bank+'.jfshdr')).read_bytes();a=(source/(bank+'.jfs')).read_bytes();count=struct.unpack_from('>I',h)[0];images=0
 for i in range(count):
  k,o,p,u,_,_=struct.unpack_from('>6I',h,4+i*24);b=a[o:o+p];b=b if p==u else zlib.decompress(b);assert len(b)==u;(source/f'{bank}-{k:08x}.bin').write_bytes(b)
  if len(b)<40:continue
  fmt,w,height=struct.unpack_from('>3I',b)
  if fmt&63 not in [6,18,19,20]or not 1<=w<=4096 or not 1<=height<=4096:continue
  im=decode(b[40:],w,height,fmt)
  if im:im.save(source/f'{bank}-{k:08x}.png');images+=1
 print(bank,count,'members',images,'images')
