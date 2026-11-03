"""Inspect original standalone car geometry strips and native vertex declarations."""
import json,struct,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-build/kits';rows=[]
for p in source.glob('350z-*.bin'):
 b=p.read_bytes()
 try:
  ni=struct.unpack_from('>I',b)[0]
  if not 3<ni<100000 or 4+ni*2+4>=len(b):continue
  indices=struct.unpack_from('>'+str(ni)+'H',b,4);o=4+ni*2;ng=struct.unpack_from('>I',b,o)[0];o+=4
  if not 0<ng<40:continue
  groups=[]
  for gi in range(ng):
   name=b[o:o+32].split(b'\0')[0].decode('ascii');assert name and all(32<=ord(x)<127 for x in name)
   count=struct.unpack_from('>I',b,o+104)[0];assert 0<count<15
   stride,nv=struct.unpack_from('>2I',b,o+108+12*count);start=o+116+12*count;assert 12<=stride<=64 and 0<nv<65536 and start+stride*nv<=len(b)
   ps=[struct.unpack_from('>3f',b,start+i*stride)for i in range(nv)];assert all(math.isfinite(x)for v in ps for x in v)
   groups.append(dict(material=name,vertices=nv,stride=stride,vertex_start=start,descriptor_start=o,bounds=[[min(v[i]for v in ps)for i in range(3)],[max(v[i]for v in ps)for i in range(3)]]));o=start+stride*nv
  rows.append(dict(key=p.stem[5:],indices=ni,groups=groups,trailing=len(b)-o,size=len(b)))
 except (ValueError,UnicodeDecodeError,struct.error,AssertionError):pass
(source/'350z-geometry-inventory.json').write_text(json.dumps(rows,indent=2));print('decoded',len(rows))
for r in rows:
 lo=[min(g['bounds'][0][i]for g in r['groups'])for i in range(3)];hi=[max(g['bounds'][1][i]for g in r['groups'])for i in range(3)]
 if hi[2]<-140 and lo[1]>70:print(r['key'],lo,hi,[g['material']for g in r['groups']])
