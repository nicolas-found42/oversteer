"""Bind original symbolic UI Texture labels to exact JFS keys via native hash."""
import json,re
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];base=ROOT/'godot/assets/ui/native';images=json.loads((base/'manifest.json').read_text());by={}
for row in images:by.setdefault(row['key'],[]).append(row)
paths=json.loads((ROOT/'artifacts/juiced2-build/ui/layout-fields-manifest.json').read_text())['records'];labels=set()
for row in paths:
 fields=json.loads((ROOT/row['path']).read_text())['fields']
 for f in fields:
  if f and f[0]in ['Texture','MeterTexture','NeedleTexture']and len(f)>1 and isinstance(f[1],str):labels.add(f[1])
dest=base/'named';dest.mkdir(exist_ok=True);named=[];unresolved=[]
for label in sorted(labels):
 native_path='Textures\\'+label+'.ddt';key=f'{filename_hash(native_path):08x}';candidates=by.get(key,[])
 if not candidates:unresolved.append(dict(label=label,native_path=native_path,key=key));continue
 record=next((r for r in candidates if r['bank']=='ui'),candidates[0]);filename=re.sub('[^A-Za-z0-9_-]+','_',label)+'.png';(dest/filename).write_bytes((ROOT/'godot'/record['path'][6:]).read_bytes());named.append(dict(label=label,native_path=native_path,key=key,path=f'res://assets/ui/native/named/{filename}',source_bank=record['bank'],width=record['width'],height=record['height'],binding='exact original filename hash verified against native JFS member'))
(base/'named-assets.json').write_text(json.dumps(dict(assets=named,unresolved=unresolved),indent=2)+'\n');aliases={'tachometer':'HUD_Dial','gauge-background':'HUD_Dial_BG','gauge-reflect':'HUD_Dial_Reflect','needle':'HUD_Needle','minimap-ring':'HUD_MapFrame','nitrous-meter':'NOS_Meter','nitrous-meter-bg':'NOS_MeterBG','nitrous-meter-arrow':'NOS_Meter_Arrow','nitrous-bottle':'HUD_NOS_Glow'};manifest=json.loads((base/'aliases/manifest.json').read_text());manifest=[r for r in manifest if r['alias']not in aliases]
for alias,label in aliases.items():
 row=next((r for r in named if r['label']==label),None)
 if row:(base/'aliases'/f'{alias}.png').write_bytes((ROOT/'godot'/row['path'][6:]).read_bytes());manifest.append(dict(alias=alias,path=f'res://assets/ui/native/aliases/{alias}.png',native_label=label,source_key=row['key'],source_bank=row['source_bank'],selection='exact native symbolic texture filename hash'))
(base/'aliases/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Exact native named bindings:',len(named),'unresolved',len(unresolved))
for key in ['0024319d','08c1bed3','039cb1ba']:
 print(key,[r['label']for r in named if r['key']==key])
