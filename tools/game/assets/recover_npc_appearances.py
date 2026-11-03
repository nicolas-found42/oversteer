"""Stage original character identity -> .def appearance bindings, no runtime writes."""
import hashlib,json,shlex,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'npc-appearances';OUT.mkdir(parents=True,exist_ok=True)
configs=json.loads((ROOT/'artifacts/juiced2-build/core-native-gameplay-config.json').read_text());record=next(r for r in configs['matched_records']if r['index']==268);characters=[];current=None
archive=(ROOT/'artifacts/juiced2-recovery/scripts.jfs').read_bytes();packed=archive[record['offset']:record['offset']+record['packed_size']];raw=zlib.decompress(packed)if record['packed_size']!=record['decoded_size']else packed;assert len(raw)==record['decoded_size']and hashlib.sha256(raw).hexdigest()==record['sha256']
for row in record['fields']:
 if row[0]=='[StartCharacter]':current=dict(native_rows=[]);characters.append(current)
 elif row[0]=='[EndCharacter]':current=None
 elif current is not None:current['native_rows'].append(row)
inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());files={r['path'].lower():r for r in inv['files']};catalog=json.loads((SOURCE/'component-catalog-evidence.json').read_text());manifest=json.loads((ROOT/'godot/assets/characters/components.json').read_text());runtime={c['id']:c for c in manifest['components']};definitions={}
def one(rows,key):return next((row[1]for row in rows if row[0]==key and len(row)>1),None)
with open(inv['iso'],'rb')as iso:
 banks={}
 for bank in [r['path'][8:-7].lower() for r in inv['files'] if r['path'].startswith('skinned/')and r['path'].endswith('.jfshdr')]:
  hrow=files[f'skinned/{bank}.jfshdr'];iso.seek(hrow['offset']);h=iso.read(hrow['size']);banks[bank]={struct.unpack_from('>I',h,4+24*i)[0]:(i,struct.unpack_from('>6I',h,4+24*i))for i in range(struct.unpack_from('>I',h)[0])}
 for character in characters:
  rows=character['native_rows'];tag=one(rows,'Tag');name=one(rows,'CharFile');character.update(tag=tag,display_name=' '.join(str(one(rows,k)or'')for k in ['FirstName','LastName']).strip(),character_type=one(rows,'Type'),native_sex=one(rows,'Sex'),animation_prefix=one(rows,'AnimPreFix'),char_file=name)
  if not name:character['appearance_status']='CharFile not supplied';continue
  filename=name+'.def';key=filename_hash(filename);found=[]
  for bank,entries in banks.items():
   if key not in entries:continue
   index,(_,offset,packed,size,*_)=entries[key];iso.seek(files[f'skinned/{bank}.jfs']['offset']+offset);raw=iso.read(packed);raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size
   path=OUT/f'{bank}-{filename}';path.write_bytes(raw);found.append(dict(bank=f'skinned/{bank}.jfs',filename=filename,key=f'{key:08x}',member=index,offset=offset,packed_size=packed,size=size,sha256=hashlib.sha256(raw).hexdigest(),path=str(path.relative_to(ROOT))))
   if name not in definitions:
    lines=[shlex.split(line)for line in raw.decode().splitlines()if line.strip()];gender=lines[0][0];attributes={};components=[]
    if any(row[0]=='MORPH_ATTRIBUTES'for row in lines):
     at=next(i for i,row in enumerate(lines)if row[0]=='MORPH_ATTRIBUTES');count=int(lines[at][1]);attributes={r[0]:float(r[1])for r in lines[at+1:at+1+count]};assert len(attributes)==count
    at=next(i for i,row in enumerate(lines)if row[0]=='Components');count=int(lines[at][1]);selected=lines[at+1:at+1+count];assert len(selected)==count
    for row in selected:
     category,component_name=row[:2];matches=[c for c in catalog['components']if c['category']==category and str(c['name']).lower()==component_name.lower()]
     components.append(dict(category=category,native_name=component_name,component_matching='823DC190 ASCII case-insensitive full equality',raw_operands=row[2:],exact_component_ids=[c['id']for c in matches],prepared_skin_ids=sorted({skin for c in matches for skin in runtime.get(c['id'],{}).get('skin_ids',[])})))
    definitions[name]=dict(id=name,gender=gender,skeleton=one(lines,'skeleton'),sound_bank=one(lines,'SOUND_BANK'),native_attributes=attributes,components=components,native_rows=lines)
  character['definition_sources']=found;character['appearance_status']='Original .def recovered'if found else'Original .def hash absent from examined avatar/avatar_lo/player01 banks'
functions={};wanted=['821D7D68','821D7E48','821D8090','821EBC98','822385C8','82239FC0','823DC190']
for path in (ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default').glob('*recomp*.cpp'):
 text=path.read_text()
 for address in wanted:
  marker=f'DEFINE_REX_FUNC(sub_{address})';start=text.find(marker)
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end if end>=0 else None];(OUT/f'{address}.cpp').write_text(body);functions[address]=dict(source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(body.encode()).hexdigest())
assert len(functions)==len(wanted)
rdata_path=ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin';data_path=rdata_path.parent/'824A0000-.data.bin';rdata=rdata_path.read_bytes();data=data_path.read_bytes();callbacks=[]
for address,name,table,callback in [(0x82040144,'CharFile',0x824b0a28,0x821d7d68),(0x820400e8,'AnimPreFix',0x824b0a58,0x821d7e48),(0x820400e4,'Sex',0x824b0a60,0x821d8090)]:
 assert rdata[address-0x82000400:].split(b'\0',1)[0].decode()==name and struct.unpack_from('>2I',data,table-0x824a0000)==(address,callback);callbacks.append(dict(name=name,string_address=f'{address:08x}',table_address=f'{table:08x}',callback=f'{callback:08x}'))
report=dict(schema_version=2,identity_source={k:record[k]for k in ['index','key','sha256','offset','packed_size','decoded_size']},callbacks=callbacks,functions=functions,characters=characters,definitions=list(definitions.values()),consumer=dict(char_file='821D7D68 copies CharFile operand into native character profile+16',animation_prefix='821D7E48 copies AnimPreFix to profile+4',appearance_load='821EBC98 reads profile+16 and calls822385C8 into description+328, unless cached/custom-player or alternate-variant branches apply',component_equality='822385C8 calls82239FC0, which uses823DC190 ASCIIcase-insensitive equality; raw spellings retained',definition_loader='822385C8 appends.def and reads original gender/skeleton/components/raw morph values',variant_boundary='821EBC98 also has player/fallback and821EBB38 alternate-name branches; canonical CharFile.def is proven source data, not a claim every scene uses the same LOD or variation.'),summary=dict(characters=len(characters),resolved=sum(bool(c.get('definition_sources'))for c in characters),unique_definitions=len(definitions),driver_identities=sum(c['character_type']=='Driver'for c in characters),resolved_driver_identities=sum(c['character_type']=='Driver'and bool(c.get('definition_sources'))for c in characters),component_rows=sum(len(d['components'])for d in definitions.values()),unresolved_component_rows=sum(not c['exact_component_ids']for d in definitions.values()for c in d['components'])),limits=['Identity Type/Tag and nativeSex retained separately from .def gender; conflicting source fields are not silently corrected.','NPC/rival definitions are not player-selectable presets or a crowd likeness claim.','Raw56 levels and complete component operands retained; no invented resemblance or generic preset substitution.','Prepared-skin lists are existing assets only; missing source definitions/components remain explicit.','No runtime assets or player profile data changed.'])
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['summary'])
