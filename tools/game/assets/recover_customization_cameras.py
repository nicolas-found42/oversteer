"""Retain source customization camera rows without inventing garage room anchors."""
import hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-recovery';header=(source/'scripts.jfshdr').read_bytes();archive=(source/'scripts.jfs').read_bytes();key=0xb7cf5263
for index in range(struct.unpack_from('>I',header)[0]):
 entry=struct.unpack_from('>6I',header,4+24*index)
 if entry[0]==key:break
else:raise ValueError('source customization camera member absent')
_,offset,packed,size,_,_=entry;raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size;start,cursor=struct.unpack_from('>2I',raw,4);formats=raw[start:cursor].split(b'\3')[0].decode().strip().splitlines();rows=[]
for fmt in formats:
 values=[]
 for kind in fmt:
  assert kind in'sif';value=struct.unpack_from('>f'if kind=='f'else'>i',raw,cursor)[0];cursor+=4
  if kind=='s':value=raw[value:raw.index(0,value)].decode()
  values.append(value)
 rows.append(values)
assert cursor==len(raw);cameras=[];current=None
for row in rows:
 if row[0]=='[Cam]':current=dict(name=row[1],native_rows=[]);cameras.append(current)
 elif row[0]=='[EndCam]':current=None
 elif current is not None:current['native_rows'].append(row)
report=dict(source=dict(bank='scripts.jfs',member=index,key=f'{key:08x}',sha256=hashlib.sha256(raw).hexdigest()),cameras=cameras,limits=['Camera component-relative offsets retained verbatim; garage room/car world anchors and original camera offset basis need separate consumer proof.'])
out=ROOT/'artifacts/juiced2-build/presentation';(out/'customization-cameras.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(len(cameras),'exact customization cameras; runtime unchanged')
