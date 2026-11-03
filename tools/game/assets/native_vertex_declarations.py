"""Read original Xbox360 VDL vertex declarations, including semantic indices."""
import struct
def declarations(raw):
 count=struct.unpack_from('>I',raw)[0];cursor=4;result=[]
 for _ in range(count):
  size,n=struct.unpack_from('>2I',raw,cursor);assert size==4+n*12
  rows=[]
  for i in range(n):
   offset,fmt,semantic=struct.unpack_from('>3I',raw,cursor+8+i*12)
   if offset==0x00ff0000:continue
   rows.append(dict(offset=offset,format=fmt,usage=(semantic>>16)&255,index=(semantic>>8)&255))
  result.append(rows);cursor+=size+4
 assert cursor==len(raw);return result
