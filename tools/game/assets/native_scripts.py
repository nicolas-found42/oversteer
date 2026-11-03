"""Exact original script lookup by recovered native filename hash."""
from pathlib import Path
import json,struct,zlib,hashlib
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-recovery';header=(source/'scripts.jfshdr').read_bytes();archive=(source/'scripts.jfs').read_bytes();lookup={struct.unpack_from('>I',header,4+i*24)[0]:(i,struct.unpack_from('>6I',header,4+i*24))for i in range(struct.unpack_from('>I',header)[0])}
def record_for_filename(filename):
 key=filename_hash(filename)
 if key not in lookup:return None
 index,(_,offset,packed,size,_,_)=lookup[key];raw=archive[offset:offset+packed];b=raw if packed==size else zlib.decompress(raw);assert len(b)==size
 if b[:4]==b'\x02'*4:
  start,cursor=struct.unpack_from('>2I',b,4);formats=b[start:cursor].split(b'\x03')[0].decode().strip().splitlines();rows=[]
  for row in formats:
   values=[]
   for kind in row:
    assert kind in 'sif';value=struct.unpack_from('>f'if kind=='f'else'>i',b,cursor)[0];cursor+=4
    if kind=='s':value=b[value:b.index(0,value)].decode()
    values.append(value)
   rows.append(values)
  assert cursor==len(b)
 else:
  rows=[]
  for line in b.decode(errors='replace').splitlines():
   line=line.split(';',1)[0].strip()
   if not line:continue
   values=[]
   for token in line.split():
    try:value=float(token)if'.'in token else int(token)
    except ValueError:value=token
    values.append(value)
   rows.append(values)
 return dict(index=index,key=f'{key:08x}',filename=filename,sha256=hashlib.sha256(b).hexdigest(),offset=offset,decoded_size=size,fields=rows)
