"""Retain active original avatar component rules and exact skin-file bindings."""
import hashlib,json,re,shlex
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';rows=[];skins={}
category_names=['skin','top','head','hair','bottom','hand','feet','eye','accessory','facialhair','lips','eyebrows','topcolour','bottomcolour','blemish','haircolour','facialhaircolour','hat','hatcolour','celeAnim']
category_by_key={f'{filename_hash(name+"ComponentDef.txt"):08x}':name for name in category_names}
for path in sorted(SOURCE.glob('componentdefs-*.txt')):
 raw=path.read_bytes();text=re.sub(r'/\*.*?\*/','',raw.decode(),flags=re.S);text=re.sub(r'//[^\n]*','',text)
 for index,match in enumerate(re.finditer(r'\[BeginComponent\](.*?)\[EndComponent\]',text,re.S)):
  native_rows=[shlex.split(line)for line in match[1].splitlines()if line.strip()];name=next((r[1]for r in native_rows if r[0]=='name'),None)
  row=dict(id=path.stem+'_'+str(index),name=name,category=category_by_key.get(path.stem.split('-')[-1]),native_rows=native_rows,gender=[r[0]for r in native_rows if r[0]in['male','female']],skin_bindings=[],source=dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),component_index=index))
  for r in native_rows:
   if r[0]!='skin':continue
   key=f'{filename_hash(r[1]+".jsm"):08x}';mesh=SOURCE/f'avatar_lo-{key}.bin';binding=dict(native_name=r[1],key=key,path=str(mesh.relative_to(ROOT))if mesh.exists()else None)
   if mesh.exists():binding['sha256']=hashlib.sha256(mesh.read_bytes()).hexdigest()
   row['skin_bindings'].append(binding);skins[r[1]]=binding
  rows.append(row)
report=dict(category_source=dict(table='824AF7F8',filename_consumer='8223A7A0',pattern='<category>ComponentDef.txt',categories=category_names),components=rows,skins=list(skins.values()),summary=dict(active_components=len(rows),unique_skins=len(skins),resolved_skin_meshes=sum(bool(r['path'])for r in skins.values())),limits=['Original rules retained including texture replacement, HSV labels, unlock/cost and gender; not all NPC/unlocked components are player-selectable.','Bindings prove source geometry identity only; cloth texture/material execution and facial morph application remain separate work.'])
(SOURCE/'component-catalog-evidence.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['summary'])
player_rows=[]
for row in rows:
 subname=next((r[1] for r in row['native_rows'] if r[0]=='subname'),'unnamed')
 if not row['gender'] or subname=='unnamed':continue
 player_rows.append(dict(component_id=row['id'],category=row['category'],name=row['name'],subname=subname,gender=row['gender'],hidden=any(r[0]=='hidden' for r in row['native_rows']),unlock_rows=[r for r in row['native_rows'] if r[0]=='unlock'],skin_bindings=row['skin_bindings']))
player_report=dict(source_consumers=['821A40F8','821A3E60'],filters=dict(gender='component flags +200 bit1 male / bit2 female',grouping='subname +64 unequal to literal unnamed (8203D770); unique subnames form category list, matching component indices form variants',hidden_unlock='Neither examined in these two list-building consumers; purchase/lock consumer not yet recovered'),components=player_rows,counts=dict(total=len(player_rows),by_category={category:sum(r['category']==category for r in player_rows) for category in category_names if any(r['category']==category for r in player_rows)}),limits=['Source list candidates do not prove all components are unlocked or exposed in every player screen.','No runtime publication or player selector is implied.'])
(SOURCE/'player-component-candidates.json').write_text(json.dumps(player_report,indent=2,allow_nan=False)+'\n');print(player_report['counts'])
