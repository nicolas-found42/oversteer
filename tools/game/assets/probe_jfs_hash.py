import json,zlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];rows=json.loads((ROOT/'godot/assets/ui/native/manifest.json').read_text());keys={int(r['key'],16)for r in rows};names={s for r in json.loads((ROOT/'artifacts/juiced2-build/ui/native-ui-definitions.json').read_text())for s in r['strings']if len(s)>4 and'_'in s and' 'not in s};hits=collections.defaultdict(list)
def hashes(s):
 b=s.encode();h=0;fnv=2166136261;java=0;djb=5381;zero=0;sdbm=0;rot=0
 for c in b:
  h=(h+c)&0xffffffff;h=(h+(h<<10))&0xffffffff;h^=h>>6;fnv=((fnv^c)*16777619)&0xffffffff;java=(java*31+c)&0xffffffff;djb=(djb*33+c)&0xffffffff;zero=(zero*33+c)&0xffffffff;sdbm=(sdbm*65599+c)&0xffffffff;rot=(((rot<<5)|(rot>>27))^c)&0xffffffff
 h=(h+(h<<3))&0xffffffff;h^=h>>11;h=(h+(h<<15))&0xffffffff
 return dict(crc=zlib.crc32(b),crc_inv=zlib.crc32(b)^0xffffffff,joaat=h,fnv=fnv,java=java,djb=djb,zero=zero,sdbm=sdbm,rot=rot)
for name in names:
 for ext in ['', '.ddt','.tga','.png']:
  for form in [name+ext,(name+ext).lower(),(name+ext).upper()]:
   for kind,value in hashes(form).items():
    if value in keys:hits[kind].append((form,f'{value:08x}'))
print({k:len(v)for k,v in hits.items()});print({k:v[:15]for k,v in hits.items()});(ROOT/'artifacts/juiced2-build/ui/hash-probe.json').write_text(json.dumps(hits,indent=2))
