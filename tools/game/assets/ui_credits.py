"""Recover original credit payloads without substituting invented staff."""
import struct,zlib,re,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];src=ROOT/'artifacts/juiced2-build/ui';hits=[];out=src/'credits';out.mkdir(exist_ok=True)
banks=[(name,src)for name in ['ui','ui_frontend','ui_ingame','textures']]+[('scripts',ROOT/'artifacts/juiced2-recovery')]
for bank,directory in banks:
 h=(directory/(bank+'.jfshdr')).read_bytes();a=(directory/(bank+'.jfs')).read_bytes()
 for i in range(struct.unpack_from('>I',h)[0]):
  key,o,n,u,*_=struct.unpack_from('>6I',h,4+i*24);packed=a[o:o+n]
  try:b=packed if n==u else zlib.decompress(packed)
  except:continue
  terms=['executive producer','lead programmer','studio manager','credits.txt','[begincredits]','production manager','executive producers']
  if any(term.encode(enc)in b.lower()for term in terms for enc in ['ascii','utf-16-le','utf-16-be']):
   filename=out/f'{bank}-{key:08x}.bin';filename.write_bytes(b);strings=[m.group().decode(errors='replace')for m in re.finditer(rb'[ -~]{4,}',b)];hits.append(dict(bank=bank,member=i,key=f'{key:08x}',sha256=hashlib.sha256(b).hexdigest(),path=str(filename.relative_to(ROOT)),strings=strings));print(bank,i,hex(key),len(b),strings[:12])
(src/'credits-evidence.json').write_text(json.dumps(hits,indent=2)+'\n');print('creditcandidates',len(hits))
