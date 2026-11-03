"""Stage original selected-Nitro-league eligibility consumers, without physics inference."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-recovery/recompiled-handling';OUT=ROOT/'artifacts/juiced2-build/native-performance/extreme-nitro-eligibility-v1';OUT.mkdir(parents=True,exist_ok=True)
names=['8210AB20','8210D988','821DCB68','82202B10','821D64B0','8221AB58','821DAA98','82223A78','82223B58','8210D0E8'];functions={};bodies={}
for path in (SOURCE/'generated/default').glob('*recomp*.cpp'):
 text=path.read_text()
 for name in names:
  start=text.find(f'DEFINE_REX_FUNC(sub_{name})')
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end if end>=0 else None];bodies[name]=body
  (OUT/f'{name}.cpp').write_text(body);functions[name]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(body.encode()).hexdigest()}
assert len(functions)==len(names)
address=(((-32179)<<16)-3932)&0xffffffff;assert address==0x824cf0a4
assert '9640'not in bodies['8210D988'] and '9644(r28)'in bodies['8210D988']
assert '9644'not in bodies['8210D0E8']
for name in ['821DCB68','82202B10']:
 assert '12(r28)'in bodies[name] and 'sub_8210AB20'in bodies[name] and 'compare<int32_t>(ctx.r3.s32, ctx.r7.s32' in bodies[name]
report={'schema_version':1,'functions':functions,'global_pointer':{'address':f'{address:08x}','address_arithmetic':'u32((−32179<<16)−3932)','role':'active race config pointer; same alias as activation821DAA98 retained below'},
 'event_flag_provenance':{'existing_contract':'artifacts/juiced2-build/native-performance/catalog.json active_race_flag_binding','path':'82225350 parser scratch48 →82225BB0 scratch+32 →82186A48 264byte copy →82223A78/82223B58 stored+4 →821DAA98 72byte copy','equation':'48−32−4=12','token':'ExtremeNos'},
 'eligibility':[{'function':'821DCB68','anchor':'821DCBB4..821DCC0C','guards':['caller r5!=0','activeconfig12!=0'],'predicate':'8210AB20(car)==activeconfig0 league','failure':'return0 via821DCBD4','notes':'Other source checks include car/league membership, prototype and class; this is not a replacement for those checks.'},{'function':'82202B10','anchor':'82202B90..82202BCC','predicate':'When activeconfig12!=0, keep candidate only if8210AB20(candidate)==activeconfig0 league','failure':'candidate rejected via82202CD0','guards':'Existing source UI/session alternate branches retained; no universal predicate claim outside normal branch.'},{'function':'821D64B0','anchor':'821D6BB0..821D6BD4','predicate':'Candidate branch uses same config12→AB20==config0 test'}],
 'getter':{'function':'8210AB20','normal':'returns car9644','override':'Ifsession manager+36→+76 nonzero, returns selected profile field0, selection controlledbyglobalmanager1076','meaning':'Comparison is active event league, NOT a direct maxpotential comparison'},
 'ai_setup':{'function':'8210D988','entry_args':{'r3':'car','r4':'selectedleague copiedr26','r7':'enableflag copiedr18'},'anchor':'8210DCB0..8210DCBC','operation':'if r18!=0, car9644=r26','caller_example':'821D64B0 loc821D72D8 passesr7=config12,r4=config0','no_capacity_write':'Entirefunction contains no9640 read/write; doesnot itself set9640=−2'},
 'separate_capacity':{'reader':'8210D0E8 reads9640, not9644','limits':'No9644→9640 conversion, capacity multiplier, force or refill policy inferred here.'},
 'independent_review_leads':['Read full821DCB68 normalbranch, verifyr7loadedconfig0 andreturn0 mismatch.','Read full8210AB20 tocheck volatile r7 remains unchanged across leaf getter.','Check all8210D988 stores andcall args; no9640 occurrence.'],
 'limits':['Static source-only recovery; no PowerPC runtime claim.','Caller filter may disable entry restrictions; alternate session branches preserved.','Do not equate eventleague with carmaxpotential merely because UI availability may constrain selections.','No runtime assets/DLL/core/frontend files changed.']}
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Staged ExtremeNos selectedleague==activeeventleague eligibility; no9640 conversion')
rows=[]
for path in (SOURCE/'generated/default').glob('*recomp*.cpp'):
 lines=path.read_text().splitlines();function=None
 for index,line in enumerate(lines):
  if line.startswith('DEFINE_REX_FUNC'):function=line[len('DEFINE_REX_FUNC('):].split(')')[0]
  if '\tsub_8210AB20(ctx' in line:
   rows.append({'caller':function,'path':str(path.relative_to(ROOT)),'line':index+1,'excerpt':'\n'.join(lines[max(0,index-20):index+15])})
assert len(rows)==8
(OUT/'all-ab20-direct-callers.json').write_text(json.dumps({'schema_version':1,'callee':'8210AB20','count':len(rows),'callers':rows,'limits':'Exact static direct-call inventory; indirect/vtable calls not excluded.'},indent=2)+'\n')
