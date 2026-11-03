"""Stage original performance catalog and exact native consumers; no runtime edits."""
import hashlib,json,re,struct,zlib
from jfs_hash import filename_hash
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
REC=ROOT/'artifacts/juiced2-recovery'
OUT=ROOT/'artifacts/juiced2-build/native-performance'
OUT.mkdir(exist_ok=True)
h=(REC/'scripts.jfshdr').read_bytes();archive=(REC/'scripts.jfs').read_bytes()
index=267
key,offset,packed,size,*_=struct.unpack_from('>6I',h,4+24*index)
assert key==0x3b3b0e75==filename_hash('ModCarInfo.txt')
raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw)
assert len(raw)==size and raw[:4]==b'\2'*4
start,cursor=struct.unpack_from('>II',raw,4);rows=[]
for fmt in raw[start:cursor].split(b'\3')[0].decode().strip().splitlines():
 row=[]
 for kind in fmt:
  assert kind in 'sif'
  value=struct.unpack_from('>f'if kind=='f'else'>i',raw,cursor)[0];cursor+=4
  row.append(raw[value:raw.index(0,value)].decode()if kind=='s'else value)
 rows.append(row)
assert cursor==len(raw)
(OUT/'scripts-267-3b3b0e75.bin').write_bytes(raw)
wanted=['821088B0','821089E8','82108B98','82108CB8','82108DB8','82108EB8','821064C8','8210C558','8210D0E8','821092A8','8221FB90','8221FA50','8221FA68','82225350','82225368','82224F10','82225BB0','82186A48','82223A78','82223B58','821DAA98','8210ABF0','821D3508','821D3678','821C7510','821D64B0','8210D988','8210AB70','8210A968','822192F0','8221ADF0','8220EED0','821DA8D8']
functions={}
for path in (REC/'recompiled-handling/generated/default').glob('*.cpp'):
 text=path.read_text()
 for address in wanted:
  token=f'DEFINE_REX_FUNC(sub_{address})';begin=text.find(token)
  if begin<0:continue
  end=text.find('\nDEFINE_REX_FUNC',begin+1);body=text[begin:end]
  (OUT/f'{address}.cpp').write_text(body)
  functions[address]=dict(sha256=hashlib.sha256(body.encode()).hexdigest(),source=str(path.relative_to(ROOT)))
assert len(functions)==len(wanted)
packs=[dict(league=r[1],threshold=r[2],steps=r[3],native_price_operands=r[4:],native_row=r,runtime_struct_offsets=dict(league=0,threshold=4,steps=8,price_operand_offsets=[12,24,16,28,20,32]))for r in rows if r[0]=='PackData']
cars=[dict(native_id=str(r[1]),stock_power=r[2],stock_weight=r[3],max_power=r[4],min_weight=r[5],brake_factor=r[6],tyre_factor=r[7],suspension_factor=r[8],turbo_factor=r[9],cost_modifier=r[10],native_row=r,parser='821089E8: resolvesnativecarbyname;writes116..148f32')for r in rows if r[0]=='CarModInfo']
base=next(r[1:]for r in rows if r[0]=='PerBase');maximum=next(r[1:]for r in rows if r[0]=='PerMax')
assert len(packs)==10 and len(base)==len(maximum)==8
fields=[dict(catalog_base_offset=368+8*i,catalog_max_offset=372+8*i,base=a,maximum=b)for i,(a,b)in enumerate(zip(base,maximum))]
report=dict(source=dict(archive='scripts.jfs',filename='ModCarInfo.txt',filename_rdata_address='8203886c',index=index,key=f'{key:08x}',offset=offset,packed_size=packed,decoded_size=size,sha256=hashlib.sha256(raw).hexdigest()),native_rows=rows,packages=packs,cars=cars,engine_endpoints=fields,gear_ratios={r[0]:r[1:]for r in rows if r[0].startswith('Gear')},suppliers={r[1]:r[2:]for r in rows if r[0]=='ModSupplier'},functions=functions,
 source_bindings=dict(PackData='rdata82037b78→table824b85b0→821088B0;36bytesperleague',CarModInfo='82037b6c→824b85b8→821089E8',PerBase='82037b58→824b85c8→82108CB8',PerMax='82037b50→824b85d0→82108DB8',performance_categories='824b0ba0 isTHREEnamepointers:Power/Handling/Weight,NOTcallbackpairs',prototype_car='821092A8 setsnativecar+24=1;8210ABF0propagatesto9668bit31.BUT821D3508/3678consumersuseitforlambo/normdoorstyle8500—notprovenengineprototypeupgrade',prototype_goal='8221FB90 ORsgoal+48 with0x04000000'),
 spawn=dict(function='8210C558',engine_interpolation='t=f31;u=1-t;P300=lerp(catalog368,372,t);P304=lerp376,380;P308=lerp384,388;P312=lerp392,396;P316=lerp400,404;8225CA98refreshafterwrites',other_writes='Furthercatalog408..428→P348/352/356,tyres/diff/brakes andgear-map360. Detailedscalarbindingrequiresindependentreview.',nitrous_followup='8210D0E8 follows8210C558: carinstance9636scalestorquecurve;9640controlscapacity;P416=1andP420/P424overwritten'),
 limits=['Originalnativecatalog—notidentity-equivalenttoall30donors; donotbindambiguousvariantsbynamealone.','Packpriceoperandmappingretainedparseroffsets; category-specificcostconsumerstillneedsproof.','Prototypecarflag+24 andgoalbit0x04000000areprovenwrites; packageunlock/prizeandactiveraceconfigassemblynotyetproven.','Eventactiveflagsprovenseparately; prototypeperformancepackage/unlockconsumerstillunresolved.','No core/frontend/runtimeassets modified.'])
report['active_race_flag_binding']=dict(parser_fields={'ExtremeNos':dict(callback='82225350',scratch_offset=48),'Prototype':dict(callback='82225368',scratch_offset=52)},offline_storage='82225BB0passesparserScratch+32to82186A48,whichcopies264bytesunchangedintocontestvector',activation='82223A78/82223B58passstoredContest+4to821DAA98,whichcopies72bytestoglobal824CF0A4',offset_equation='active_offset=scratch_offset-32-4',active_fields={'ExtremeNos':12,'Prototype':16},goal_flags='8221FA50and8221FA68areSEPARATEgoalflagsat48,0x40000000and0x20000000—notcontestboolwriters',verification='Retainedcopyfunctionsandimmediates;noPowerPCruntimeexecution')
report['active_race_flag_binding']['discipline']=dict(parser='82224F10 passesDiscipline to821DA8D8 andstoresatscratch64;64-32-4=active28',enum_table='824B0B18',indices={'Circuit':0,'Drift':1,'TestDrive':2,'Solo':3},nitrous='820F39E0 setsNOS-enabledcar96=!(active28==1),thusDriftdisablesNOS')
report['prototype_package']=dict(packed_car_fields={'Power':76,'Handling':80,'Weight':84},encoding='0x40000000 | ((league&31)<<25) | (itemIndex&0x01ffffff); top2nonzero=installed; signed5bitleague;25bitindex',eligibility='8210AB70:ANYof3installedfieldsleague==8210A968(carmaxPotentialLeague)ANDitemIndex==3',max_potential_league='8210A968 usesnativecar.maxPower124/minWeight128 andPackData thresholds;NOTcurrentlytunedpowerweight',ai_assignment='821D64B0passesactivePrototype16asr6to8210D988;prototypebranchselectsmax-potentialleagueandwritesHandling80itemmin(3,steps-1)',unlock_goal='822192F0checksgoalflags32&0x04000000,profileBYTE2036+=1,profile2048dirty=1;8221ADF0checks40packagebits2040/2044andclearsrewardwhenallunlocked',unlock_selection='8220EED0setsbit=((menuSelection144+3)*4)+category140inprofile2040/2044;decrementsprofileBYTE2036',limits=['Selection144andcategory140needfullUIenumcontextbeforelabelingall40slots.','GoalProtUnlockawardsONEchoicecurrency—notallpackages.','CarDefPrototype+24→lambo/normdoorflagisdistinct.'])
(OUT/'catalog.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('Staged',len(packs),'packages,',len(cars),'nativecarperformanceprofiles,',len(report['suppliers']),'suppliercategories')
