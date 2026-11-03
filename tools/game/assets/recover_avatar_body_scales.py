"""Recover original three57-joint skeleton scale datasets and exact consumer."""
import hashlib,json,shlex,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters';REC=ROOT/'artifacts/juiced2-recovery';SECTIONS=REC/'recompiled-handling/decoded-sections';b=(SECTIONS/'824A0000-.data.bin').read_bytes();r=(SECTIONS/'82000400-.rdata.bin').read_bytes()
joints=[]
for i in range(57):
 p=struct.unpack_from('>I',b,0x824af6e8-0x824a0000+i*4)[0];o=p-0x82000400;joints.append(r[o:r.index(0,o)].decode())
inv=json.loads((REC/'xdvdfs-inventory.json').read_text());files={x['path'].lower():x for x in inv['files']};datasets=[]
with open(inv['iso'],'rb')as iso:
 hrow=files['skinned/avatar.jfshdr'];iso.seek(hrow['offset']);h=iso.read(hrow['size']);entries={struct.unpack_from('>I',h,4+24*i)[0]:(i,struct.unpack_from('>6I',h,4+24*i))for i in range(struct.unpack_from('>I',h)[0])}
 for name in ['tall','fat','stocky']:
  key=filename_hash(name+'.def');index,(_,offset,packed,size,*_)=entries[key];iso.seek(files['skinned/avatar.jfs']['offset']+offset);raw=iso.read(packed);raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size;(OUT/(name+'.def')).write_bytes(raw);rows=[shlex.split(line)for line in raw.decode().splitlines()if line.strip()];assert rows[0]==['BoneScales'];scales={row[0]:[float(x)for x in row[1:]]for row in rows[1:]};assert all(len(v)==3 for v in scales.values());effective={joint:scales.get(joint,[1.0,1.0,1.0])for joint in joints};assert all(v==[1.0,1.0,1.0]for v in effective.values());datasets.append(dict(name=name,key=f'{key:08x}',member=index,sha256=hashlib.sha256(raw).hexdigest(),native_rows=rows,effective_scales_by_joint=effective,all_identity=True))
mirrors=[]
with open(inv['iso'],'rb')as iso:
 for bank in ['skinned/avatar_lo','skinned/componentdefs']:
  hrow=files[bank+'.jfshdr'];iso.seek(hrow['offset']);h=iso.read(hrow['size'])
  for index in range(struct.unpack_from('>I',h)[0]):
   key,offset,packed,size,*_=struct.unpack_from('>6I',h,4+24*index);match=next((d for d in datasets if int(d['key'],16)==key),None)
   if match is None:continue
   iso.seek(files[bank+'.jfs']['offset']+offset);raw=iso.read(packed);raw=raw if packed==size else zlib.decompress(raw);digest=hashlib.sha256(raw).hexdigest();assert digest==match['sha256'];mirrors.append(dict(bank=bank+'.jfs',member=index,name=match['name'],sha256=digest))
assert len(mirrors)==6
proof_functions={};wanted=['82238180','82238AE0','82238E68','82251228']
for path in (REC/'recompiled-handling/generated/default').glob('*.cpp'):
 text=path.read_text()
 for function in wanted:
  token=f'DEFINE_REX_FUNC(sub_{function})'
  if token not in text:continue
  start=text.index(token);end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end];(OUT/f'attribute-consumer-{function}.cpp').write_text(body);proof_functions[function]=hashlib.sha256(body.encode()).hexdigest()
assert len(proof_functions)==len(wanted)
report=dict(bank_mirrors=mirrors,source_functions=proof_functions,joints=joints,datasets=datasets,consumer='82238AE0 initializes tall/fat/stocky by82238180 indices0/1/2;82238E68 applies3weights fromdescription+520/+524/+528',weight_scale=struct.unpack_from('>f',r,0x82030000-2104-0x82000400)[0],arithmetic='start currentXYZ=(1,1,1) perjoint; for each tall/fat/stocky in order: t=rawlevel*.01; currentXYZ=currentXYZ*(datasetXYZ*t+currentXYZ*(1-t)), withfloat32 intermediates andnativefmadds',binding='82238E68 matches57exactnames through82253360 then82251228 per-joint scale; no uniformbodyScale substitute',limits=['Native control-space57jointdataset is mapped by exact bone names to prepared86joint rig.','Originalnative scale application space/order downstream82251228 still toverify before renderer execution.','Skin/hair/profile attributes remain separate source consumers; this report coversonlythe3skeletonattributes.'])
report['prepared_rig_mapping']={}
for gender in ['male','female']:
 path=ROOT/'godot/assets/characters'/('native_male_baggy_t.glb'if gender=='male'else'native_female_zip.glb');raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);names={doc['nodes'][i]['name']for i in doc['skins'][0]['joints']};report['prepared_rig_mapping'][gender]=dict(matched=[name for name in joints if name in names],missing=[name for name in joints if name not in names],missing_policy='Native82238E68 skipsnegativebone-lookupresults; no inventedsubstitution',sha256=hashlib.sha256(raw).hexdigest())
report['shipped_effect']='All3shippeddatasets containonlyidentityscales;57jointmissingentriesdefaultidentity. ThereforeeveryfinitepresetweightincludingFMPreset3FAT100 evaluatesidentity underthisconsumer.'
(OUT/'native-body-scales.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
