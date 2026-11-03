"""Recover exact native creator preset order, .def fields and source provenance."""
import hashlib,json,shlex,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'presets';OUT.mkdir(exist_ok=True)
inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());files={r['path'].lower():r for r in inv['files']};header=(ROOT/'artifacts/juiced2-recovery/scripts.jfshdr').read_bytes();archive=(ROOT/'artifacts/juiced2-recovery/scripts.jfs').read_bytes();entry=struct.unpack_from('>6I',header,4+24*708);key,offset,packed,size,*_=entry;raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw);assert key==0xa3b71a33 and len(raw)==size
start,cursor=struct.unpack_from('>2I',raw,4);rows=[]
for fmt in raw[start:cursor].split(b'\3')[0].decode().strip().splitlines():
 row=[]
 for kind in fmt:
  value=struct.unpack_from('>f'if kind=='f'else'>i',raw,cursor)[0];cursor+=4
  if kind=='s':value=raw[value:raw.index(0,value)].decode()
  row.append(value)
 rows.append(row)
assert cursor==len(raw);names=[r[1]for r in rows if r[0]=='[BeginAvatarDesc]'];presets=[]
with open(inv['iso'],'rb')as iso:
 hrow=files['skinned/avatar_lo.jfshdr'];iso.seek(hrow['offset']);h=iso.read(hrow['size']);entries={struct.unpack_from('>I',h,4+24*i)[0]:(i,struct.unpack_from('>6I',h,4+24*i))for i in range(struct.unpack_from('>I',h)[0])}
 for order,name in enumerate(names):
  filename=name+'.def';key=filename_hash(filename);index,(_,offset,packed,size,*_)=entries[key];iso.seek(files['skinned/avatar_lo.jfs']['offset']+offset);b=iso.read(packed);b=b if packed==size else zlib.decompress(b);assert len(b)==size;(OUT/filename).write_bytes(b);lines=[shlex.split(line)for line in b.decode().splitlines()if line.strip()];gender=lines[0][0];morph_at=next(i for i,r in enumerate(lines)if r[0]=='MORPH_ATTRIBUTES');count=int(lines[morph_at][1]);morph_rows=lines[morph_at+1:morph_at+1+count];assert count==56 and all(len(r)==2 for r in morph_rows);comp_at=next(i for i,r in enumerate(lines)if r[0]=='Components');comp_count=int(lines[comp_at][1]);components=lines[comp_at+1:];assert len(components)==comp_count
  presets.append(dict(id=name,gender=gender,source_order=order,gender_order=sum(p['gender']==gender for p in presets),skeleton=next(r[1]for r in lines if r[0]=='skeleton'),sound_bank=next(r[1]for r in lines if r[0]=='SOUND_BANK'),morph_levels={r[0]:float(r[1])for r in morph_rows},components=[dict(category=r[0],native_component_name=r[1])for r in components],native_rows=lines,source=dict(bank='skinned/avatar_lo.jfs',filename=filename,key=f'{key:08x}',member=index,sha256=hashlib.sha256(b).hexdigest())))
report=dict(list_source=dict(bank='scripts.jfs',member=708,key='a3b71a33',sha256=hashlib.sha256(raw).hexdigest(),native_rows=rows),presets=presets,consumers=dict(definition_loader='822385C8 appends .def, reads all56 raw float levels',preset_vector_writer='821A72A8 appends712byte entry to gender vector+68 male/+84 female and copies full description',selection='821A3678 copies gender vector[index].description at+16 into player+328',creator_branch='821A8008 calls821A3678 index0 after selecting male gender in observed branch'),limits=['Exact original preset data and gender ordering retained; complete creator lifecycle/first-ever profile default not asserted solely from this branch.','Raw native levels multiply source deltas directly (82239018→8223B298→82257450); do not divide preset levels by100 unless exported deltas are correspondingly multiplied100.','Component references are exact source strings; obsolete/unresolved references must not be silently substituted.'])
(SOURCE/'native-avatar-presets.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Recovered',len(presets),'original presets; male/female first',[(g,next(p['id']for p in presets if p['gender']==g))for g in ['MALE','FEMALE']])
for source,func in [('51','822385C8'),('57','821A72A8'),('38','821A3678'),('35','821A8008')]:
 text=(ROOT/f'artifacts/juiced2-recovery/recompiled-handling/generated/default/juiced2_recomp.{source}.cpp').read_text();start=text.index(f'DEFINE_REX_FUNC(sub_{func})');end=text.find('\nDEFINE_REX_FUNC(',start+1);(SOURCE/f'preset-consumer-{func}.cpp').write_text(text[start:end])
# Creator controls have independent M/F ramps; retain whole actions, not45 invented sliders.
entry=struct.unpack_from('>6I',header,4+24*354);key,offset,packed,size,*_=entry;menu_raw=archive[offset:offset+packed];menu_raw=menu_raw if packed==size else zlib.decompress(menu_raw);assert key==filename_hash('AvatarMenu.txt') and len(menu_raw)==size
start,cursor=struct.unpack_from('>2I',menu_raw,4);menu_rows=[]
for fmt in menu_raw[start:cursor].split(b'\3')[0].decode().strip().splitlines():
 row=[]
 for kind in fmt:
  value=struct.unpack_from('>f'if kind=='f'else'>i',menu_raw,cursor)[0];cursor+=4
  if kind=='s':value=menu_raw[value:menu_raw.index(0,value)].decode()
  row.append(value)
 menu_rows.append(row)
assert cursor==len(menu_raw);actions=[];current=None
for row in menu_rows:
 if row[0]=='[BeginMenuAction]':current=dict(id=row[1],native_rows=[],morph_channels={'M':[],'F':[]});actions.append(current)
 elif row[0]=='[EndMenuAction]':current=None
 elif current is not None:
  current['native_rows'].append(row)
  for prefix,gender in [('MALEMORPH','M'),('FEMALEMORPH','F')]:
   if not row[0].startswith(prefix):continue
   suffix=row[0][len(prefix):]
   if suffix=='NAME':current['morph_channels'][gender].append(dict(name=row[1]))
   else:
    assert current['morph_channels'][gender];field={'START':'control_start','FINISH':'control_finish','RAMPSTART':'native_ramp_start','RAMPFINISH':'native_ramp_finish'}[suffix];current['morph_channels'][gender][-1][field]=row[1]
controls=dict(ramp_consumer=dict(address='821A3120',active_interval='control_start <= input <= control_finish; outside interval the channel is unchanged',arithmetic='t=(input-start)/(finish-start); p=(1-t)*start+t*finish; native_level=ramp_start+p*(ramp_finish-ramp_start)',limits=['Partial intervals must not be silently renormalized to0..1; native arithmetic is retained.','Native callback also has component-dependent special handling for attribute26; not generalized here.']),source=dict(bank='scripts.jfs',filename='AvatarMenu.txt',member=354,key=f'{key:08x}',sha256=hashlib.sha256(menu_raw).hexdigest()),actions=actions,limits=['Exact original M/F control and native ramp endpoints; native ramp arithmetic is retained separately; active control visibility and component-dependent special cases remain separate.','Several controls can affect multiple attributes or partial intervals; do not replace with45 uniform sliders.'])
(SOURCE/'native-avatar-controls.json').write_text(json.dumps(controls,indent=2,allow_nan=False)+'\n');print('Recovered',len(actions),'creator actions;',sum(bool(a['morph_channels']['M']or a['morph_channels']['F'])for a in actions),'with native morph ramps')

text=(ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default/juiced2_recomp.2.cpp').read_text();start=text.index('DEFINE_REX_FUNC(sub_821A3120)');end=text.find('\nDEFINE_REX_FUNC(',start+1);(SOURCE/'creator-ramp-821A3120.cpp').write_text(text[start:end])
