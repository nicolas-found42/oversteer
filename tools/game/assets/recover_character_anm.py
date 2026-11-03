"""Bounded original ANM channel inventory from recovered native consumers.

No semantic clip labels are invented and no runtime assets are written. Native
quaternions are WXYZ; packed positions use the exact native scale constant.
"""
import json,struct,zlib,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters'
POSITION_SCALE=0.003906369209289551
def parse(raw):
 version,flags,count=struct.unpack_from('>3I',raw);assert version==1 and count<512
 cursor=12;tracks=[]
 for _ in range(count):
  length=struct.unpack_from('>I',raw,cursor)[0];cursor+=4;assert 0<length<1024
  name=raw[cursor:cursor+length].decode('ascii');assert raw[cursor+length]==0;cursor=(cursor+length+1+3)&~3
  keys,duration,channels,begin,end=struct.unpack_from('>2I3H',raw,cursor);cursor=(cursor+14+3)&~3
  assert begin<=end<=keys and channels&~255==0,(name,cursor,keys,duration,channels,begin,end)
  constants={}
  for bit,key,n in [(32,'translation',3),(64,'rotation_wxyz',4)]:
   if channels&bit:constants[key]=list(struct.unpack_from('>'+str(n)+'f',raw,cursor));cursor+=n*4
  stride=sum(size for bit,size in [(1,4),(2,12),(4,16),(8,6),(16,8)]if channels&bit);start=cursor;cursor+=(end-begin)*stride;assert cursor<=len(raw)
  decoded=[]
  for index in range(end-begin):
   offset=start+index*stride;key={}
   for bit,label,n,fmt,scale in [(1,'time',1,'f',1),(2,'translation',3,'f',1),(4,'rotation_wxyz',4,'f',1),(8,'translation',3,'h',POSITION_SCALE),(16,'rotation_wxyz',4,'h',1)]:
    if channels&bit:
     values=struct.unpack_from('>'+str(n)+fmt,raw,offset);offset+=n*struct.calcsize(fmt);values=[v*scale for v in values];assert all(math.isfinite(v)for v in values)
     if bit==16:
      norm=math.sqrt(sum(v*v for v in values))+1.1920928955078125e-7;values=[v/norm for v in values]
     key[label]=values[0]if n==1 else values
   decoded.append(key)
  tracks.append(dict(name=name,key_count=keys,duration_ms=duration,flags=channels,begin_key=begin,end_key=end,stride=stride,constants=constants,keys=decoded))
 return dict(version=version,flags=flags,bone_count=count,tracks=tracks,trailing_offset=cursor,trailing_bytes=len(raw)-cursor,trailing_sha256=hashlib.sha256(raw[cursor:]).hexdigest())
reports=[];failures=[];out=SOURCE/'decoded-anm';out.mkdir(exist_ok=True)
for bank in ['FE_CommonMale_amf','anm']:
 header=(SOURCE/(bank+'.jfshdr')).read_bytes();archive=(SOURCE/(bank+'.jfs')).read_bytes();count=struct.unpack_from('>I',header)[0]
 for index in range(count):
  key,offset,packed,size,_,_=struct.unpack_from('>6I',header,4+24*index);raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size
  if raw[:4]!=b'\0\0\0\1':continue
  try:
   clip=parse(raw);clip.update(source_bank=bank,source_member=index,source_key=f'{key:08x}',source_sha256=hashlib.sha256(raw).hexdigest());path=out/f'{bank}-{key:08x}.json';path.write_text(json.dumps(clip,separators=(',',':'),allow_nan=False)+'\n');reports.append({k:clip[k]for k in ['source_bank','source_member','source_key','bone_count','trailing_bytes']})
  except Exception as error:failures.append(dict(bank=bank,index=index,key=f'{key:08x}',error=str(error)))
result=dict(clips=reports,failures=failures,native_consumers=['82242C40 loader','822422A8 stride','82242308 channel storage','82242608 key getter','82242808 interpolation','82308498 quaternion WXYZ matrix'],position_scale=POSITION_SCALE,limits=['Clip filename/semantic binding unresolved; unknown clips are not relabeled idle or celebration.','No runtime animation or native interpolation parity claim from this inventory.'])
(SOURCE/'anm-channel-inventory.json').write_text(json.dumps(result,indent=2)+'\n');print('Decoded',len(reports),'original ANM clips;',len(failures),'bounded parse failures')
