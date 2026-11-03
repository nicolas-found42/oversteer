"""Retain original creator cameras, markers and bounded placement-consumer proof."""
import hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'artifacts/juiced2-build/presentation'
REC=ROOT/'artifacts/juiced2-recovery'
h=(REC/'scripts.jfshdr').read_bytes();archive=(REC/'scripts.jfs').read_bytes()
def read(index,key):
 actual,offset,packed,size,*_=struct.unpack_from('>6I',h,4+24*index);assert actual==key
 raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size
 start,cursor=struct.unpack_from('>2I',raw,4);rows=[]
 for fmt in raw[start:cursor].split(b'\3')[0].decode().strip().splitlines():
  row=[]
  for kind in fmt:
   value=struct.unpack_from('>f'if kind=='f'else'>i',raw,cursor)[0];cursor+=4
   if kind=='s':value=raw[value:raw.index(0,value)].decode()
   row.append(value)
  rows.append(row)
 assert cursor==len(raw)
 return rows,dict(bank='scripts.jfs',member=index,key=f'{key:08x}',sha256=hashlib.sha256(raw).hexdigest())
rows,camera_source=read(255,0x37810b3b);cameras=[];current=None
for row in rows:
 if row[0]=='[Cam]':current=dict(name=row[1],native_rows=[]);cameras.append(current)
 elif current is not None:current['native_rows'].append(row)
marker_rows,marker_source=read(769,0xb12b1711)
rdata=(REC/'recompiled-handling/decoded-sections/82000400-.rdata.bin').read_bytes();scale=struct.unpack_from('>f',rdata,0x8204d188-0x82000400)[0];assert abs(scale-0.01745329252)<1e-9
markers=[]
for row in marker_rows:
 assert row[0]=='Marker'and len(row)==8
 xyz=row[2:5];euler=row[5:8]
 markers.append(dict(name=row[1],native_position_cm=xyz,position_rh_m=[-xyz[0]/100,xyz[1]/100,xyz[2]/100],native_rotation_degrees=euler,native_yaw_radians=euler[1]*scale,reflected_yaw_radians=-euler[1]*scale,native_rows=[row]))
assert len(cameras)==14 and len(markers)==20
report=dict(camera_source=camera_source,cameras=cameras,marker_source=marker_source,markers=markers,consumers=dict(actor_marker='821A74D0 /821A9050 /821A9DA8 query TunnelCharacter_CreateAvatar using8207EB50 position and8207EC40 rotation',actor_rotation='821A74D0 multiplies returned Y by float8204D188 (pi/180) then calls82082EC0; yaw-only reflected conversion retained',car_marker='8219C008 queries CreateAvatar_Car position/rotation then calls820F2A50',marker_getters='8207EB50/8207EC40 return raw XYZ/rotation from72byte named entries'),rotation_scale=dict(address='8204D188',degrees_to_radians=scale),limits=['Source control SelectDriver does not exactly match camera AvatarSelectDriver; no alias silently introduced.','Final CamFOV projection aspect convention is traced separately; raw original fields retained.','Creator components use NativeAvatar normalized root and face+Z; marker/actor normalization composition must be applied once.','Marker venue coordinates do not prove unconditional visibility or native shader translation of every tunnel object.'])
(OUT/'creator-presentation.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('Creator source cameras',len(cameras),'markers',len(markers),'rotation scale',scale)
