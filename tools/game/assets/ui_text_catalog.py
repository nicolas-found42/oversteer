"""Recover original UTF-16 localization and binary UI string tables."""
import json,struct,zlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];src=ROOT/'artifacts/juiced2-build/ui';out=src/'text-catalog';out.mkdir(exist_ok=True);rows=[];binary=[]
for bank in ['ui','ui_frontend','ui_ingame','textures']:
 h=(src/(bank+'.jfshdr')).read_bytes();a=(src/(bank+'.jfs')).read_bytes()
 for i in range(struct.unpack_from('>I',h)[0]):
  key,o,n,u,*_=struct.unpack_from('>6I',h,4+i*24)
  try:b=zlib.decompress(a[o:o+n])
  except:continue
  if b.startswith(b'\0 \0V\0E\0R\0S'):
   text=b.decode('utf-16-be');path=out/f'{bank}-{key:08x}.txt';path.write_text(text);rows.append(dict(bank=bank,member=i,key=f'{key:08x}',path=str(path.relative_to(ROOT)),entries=[dict(id=m[1],text=m[2]) for m in re.finditer(r'(?m)^(\d+)\s*=\s*(.*)',text)]))
  elif b'[BeginUI]'in b:
   path=out/f'{bank}-{key:08x}.bin';path.write_bytes(b);strings=[m.group().decode() for m in re.finditer(rb'[ -~]{3,}',b)];binary.append(dict(bank=bank,member=i,key=f'{key:08x}',path=str(path.relative_to(ROOT)),strings=strings,format='native binary tokenized UI definition; string table and typed values retained'))
(src/'localization.json').write_text(json.dumps(rows,indent=2)+'\n');(src/'native-ui-definitions.json').write_text(json.dumps(binary,indent=2)+'\n');print('Recovered',len(rows),'localization members;',len(binary),'native binary UI definitions')
