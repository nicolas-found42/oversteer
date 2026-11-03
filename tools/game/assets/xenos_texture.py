"""Decode native BDL top-mip DXT textures (Xenos tiled blocks, 16-bit byte swap)."""
import struct,io
from PIL import Image
def untile(data,w,h,pitch,block=4):
 width=max(1,(w+block-1)//block);height=max(1,(h+block-1)//block);aligned=(width+31)&~31;log=(pitch>>2)+((pitch>>1)>>(pitch>>2));out=bytearray(width*height*pitch)
 for offset in range(len(data)//pitch):
  ob=offset<<log;ot=((ob&~4095)>>3)+((ob&1792)>>2)+(ob&63);om=ot>>(7+log)
  mx=(om%(aligned>>5))<<2;tile=(((ot>>(5+log))&2)+(ob>>6))&3;x=((mx+tile)<<3)+((((ot>>1)&~15)+(ot&15))&((pitch<<3)-1))//pitch
  my=(om//(aligned>>5))<<2;tile=((ot>>(6+log))&1)+((ob&2048)>>10);micro=(((ot&(((pitch<<6)-1)&~31))+((ot&15)<<1))>>(3+log))&~1;y=((my+tile)<<3)+micro+((ot&16)>>4)
  if x<width and y<height:out[(y*width+x)*pitch:(y*width+x+1)*pitch]=data[offset*pitch:(offset+1)*pitch]
 return bytes(out)
def decode(data,w,h,fmt):
 kind=fmt&63
 if kind==6:
  raw=untile(data,w,h,4,1);im=Image.frombytes('RGBA',(w,h),raw);a,r,g,b=im.split();return Image.merge('RGBA',(r,g,b,a))
 if kind not in (18,19,20):return None
 pitch=8 if kind==18 else 16
 data=bytes(v for pair in zip(data[1::2],data[0::2]) for v in pair)
 raw=untile(data,w,h,pitch);fourcc=b'DXT1' if kind==18 else b'DXT3' if kind==19 else b'DXT5'
 header=struct.pack('<7I',124,0x81007,h,w,len(raw),0,1)+b'\0'*44+struct.pack('<II4s5I',32,4,fourcc,0,0,0,0,0)+struct.pack('<5I',0x1000,0,0,0,0)
 return Image.open(io.BytesIO(b'DDS '+header+raw)).convert('RGBA')
