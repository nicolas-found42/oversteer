"""Decode native tokenized UI definitions into exact typed layout rows."""
import json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];src=ROOT/'artifacts/juiced2-build/ui';rows=json.loads((src/'native-ui-definitions.json').read_text());out=src/'layout-fields';out.mkdir(exist_ok=True);manifest=[];errors=[]
for record in rows:
 b=(ROOT/record['path']).read_bytes()
 if b[:4]!=b'\x02'*4:continue
 try:
  start,cursor=struct.unpack_from('>2I',b,4);formats=b[start:cursor].split(b'\x03')[0].decode().strip().splitlines();fields=[]
  for format_row in formats:
   values=[]
   for field in format_row:
    if field not in 'sif':raise ValueError('unknown field '+field)
    value=struct.unpack_from('>f'if field=='f'else'>i',b,cursor)[0];cursor+=4
    if field=='s':value=b[value:b.index(0,value)].decode()
    values.append(value)
   fields.append(values)
  assert cursor==len(b)
  item=dict(bank=record['bank'],key=record['key'],source_member=record['member'],fields=fields);name=record['bank']+'-'+record['key']+'.json';(out/name).write_text(json.dumps(item,indent=2)+'\n');manifest.append(dict(bank=record['bank'],key=record['key'],path=str((out/name).relative_to(ROOT)),row_count=len(fields)))
 except Exception as e:errors.append(dict(bank=record['bank'],key=record['key'],error=str(e)))
(src/'layout-fields-manifest.json').write_text(json.dumps(dict(records=manifest,errors=errors),indent=2)+'\n');print('Decoded',len(manifest),'exact layouts;',len(errors),'errors')
