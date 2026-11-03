"""Bind explicit donor-class adaptations to recovered native restricted contests.

Default stages evidence only. --publish patches fresh content/cars, preserving all
unrelated car prices, physical profiles and event data.
"""
import copy,hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/presentation';REC=ROOT/'artifacts/juiced2-recovery';h=(REC/'scripts.jfshdr').read_bytes();archive=(REC/'scripts.jfs').read_bytes();native=[]
for index in range(struct.unpack_from('>I',h)[0]):
 key,offset,packed,size,*_=struct.unpack_from('>6I',h,4+24*index);raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw)
 if b'[begincar]'not in raw.lower()or not any(x in raw.lower()for x in [b'musclecar',b'supercar']):continue
 start,cursor=struct.unpack_from('>2I',raw,4);rows=[]
 for fmt in raw[start:cursor].split(b'\3')[0].decode().strip().splitlines():
  row=[]
  for kind in fmt:
   value=struct.unpack_from('>f'if kind=='f'else'>i',raw,cursor)[0];cursor+=4
   if kind=='s':value=raw[value:raw.index(0,value)].decode()
   row.append(value)
  rows.append(row)
 assert cursor==len(raw);head=next(r for r in rows if r[0].lower()=='[begincar]');classes=[('MuscleCar'if r[0].lower()=='musclecar'else'SuperCar')for r in rows if r[0].lower()in ['musclecar','supercar']];native.append(dict(native_id=head[1],name=head[2],classes=classes,member=index,key=f'{key:08x}',sha256=hashlib.sha256(raw).hexdigest(),native_rows=rows))
content_path=ROOT/'data/juiced2/content.json';content=json.loads(content_path.read_text());before=copy.deepcopy(content);first={cls:min(e['league']for e in content['events']if e.get('car_class','').casefold()==cls.casefold())for cls in ['MuscleCar','SuperCar']};assert first=={'MuscleCar':3,'SuperCar':5}
muscle={'MUSTANG_68','MCLA_VP_CHV_CAMAROSS_69','MCLA_VP_BUK_GRANDNATIONAL_87'};supercars={'MCLA_VP_AUD_R8_08','MCLA_VP_LAM_GALLARDO_06','MCLA_VP_CHV_CORVETTEZ06_07','GT4_DODG0005','GT4_ASMT0005','MCLA_VP_SLN_S7_06'};mappings=[]
for car in content['cars']:
 cls='MuscleCar'if car['id']in muscle else'SuperCar'if car['id']in supercars else None;classes=[cls]if cls else[];old=car.get('class_availability_source',{}).get('prior_league',car['league']);league=min(old,first[cls])if cls else old
 provenance=dict(status='accepted-donor-replacement adaptation, not original native identity/tune equality',classes=classes,availability='Preserve adapted priorleague exceptmakeclassifieddonorspurchasablebyfirstnativeclasscontest',native_first_class_league=first.get(cls),prior_league=old,adapted_league=league)
 car['classes']=classes;car['league']=league;car['class_availability_source']=provenance;mappings.append(dict(id=car['id'],name=car['name'],classes=classes,league=league,source=provenance))
assert all(a['price']==b['price']for a,b in zip(before['cars'],content['cars']));assert content['events']==before['events'];assert len(content['cars'])==30
proof_functions={};wanted=['821074F8','82107518','8221F988','82100220','82202B10','8221AB58','823DC190']
for path in (REC/'recompiled-handling/generated/default').glob('*.cpp'):
 text=path.read_text()
 for function in wanted:
  token=f'DEFINE_REX_FUNC(sub_{function})'
  if token not in text:continue
  start=text.index(token);end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end];(OUT/f'class-consumer-{function}.cpp').write_text(body);proof_functions[function]=hashlib.sha256(body.encode()).hexdigest()
assert len(proof_functions)==len(wanted)
report=dict(source_functions=proof_functions,native_class_catalog=native,cars=mappings,first_restricted_event_leagues=first,source_consumers=dict(car_flags='MUSCLECAR→821074F8 setsflagsmask0x1cvalue4;SuperCar→82107518 setsvalue8',event_class='CarClass→8221F988 storesenum+64:SuperCar2,82100220MuscleCar1,none0',candidate_filter='82202B10 loc82202BE8:class1 requiresflags&0x1c==4;class2 requires==8;otherwisecandidate skipped',owned_car_count='8221AB58 same4/8filters withleague matching'),adaptations=['Case-fold classmatching normalizes shippedMusclecar/Supercar spellingvariants; native823DC190itselfisCASE-SENSITIVEstrcmp.','Accepted30membership is explicit donor classification adaptation; source flags/catalog retain originalvehicles separately.','No price orphysicalidentity changes; no unrestrictedCivicMuscleentry.'],limits=['Nativecandidate-list/ownedcarfilterproven; finalStartRaceenforcementcallsite remains independenttrace.'])
(OUT/'accepted-car-classes.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');(OUT/'content-with-car-classes.json').write_text(json.dumps(content,indent=2,allow_nan=False)+'\n')
if '--publish'in sys.argv:
 encoded=json.dumps(content,indent=2,allow_nan=False)+'\n';content_path.write_text(encoded);(ROOT/'godot/assets/game-content.json').write_text(encoded)
 cars_path=ROOT/'data/juiced2/cars.json';cars=json.loads(cars_path.read_text());lookup={c['id']:c for c in content['cars']}
 for car in cars['cars']:
  definition=lookup[car['code']]
  for key in ['classes','class_availability_source']:car[key]=definition[key]
 encoded=json.dumps(cars,indent=2,allow_nan=False)+'\n';cars_path.write_text(encoded);(ROOT/'godot/assets/cars.json').write_text(encoded);(ROOT/'data/juiced2/native-car-classes.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('Published'if'--publish'in sys.argv else'Staged',len(native),'nativeflaggedcars;30donors,3MuscleCar/6SuperCar availablebyclasscontests')
print([(r['native_id'],r['classes'])for r in native])
