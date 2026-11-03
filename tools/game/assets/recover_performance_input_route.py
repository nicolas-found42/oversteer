"""Retain bounded original performance state2 challenge routing; no runtime writes."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'artifacts/juiced2-recovery/recompiled-handling'
OUT=ROOT/'artifacts/juiced2-build/native-performance/input-routing-v1'
OUT.mkdir(parents=True,exist_ok=True)
names=['821C9138','821CA528','821CA168','82217870'];functions={};bodies={}
for path in (SOURCE/'generated/default').glob('*recomp*.cpp'):
 text=path.read_text()
 for name in names:
  start=text.find(f'DEFINE_REX_FUNC(sub_{name})')
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end if end>=0 else None]
  (OUT/f'{name}.cpp').write_text(body);bodies[name]=body
  functions[name]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(body.encode()).hexdigest()}
assert len(functions)==4
body=bodies['821C9138']
assert 'case 2:\n\t\tgoto loc_821C9C14;' in body
start=body.index('loc_821C9C14:');end=body.index('loc_821C9C24:',start)
assert 'sub_821CA528' in body[start:end] and 'sub_821CA168' not in body[start:end]
rdata=(SOURCE/'decoded-sections/82000400-.rdata.bin').read_bytes();strings={}
for displacement,expected in [(-4280,'CarChallengeSelect'),(-4260,'mod_tuning_challenge'),(-4336,'click'),(-6692,'no')]:
 address=(((-32252)<<16)+displacement)&0xffffffff;offset=address-0x82000400
 actual=rdata[offset:rdata.index(0,offset)].decode();assert actual==expected
 strings[f'{address:08x}']=actual
# Model only the explicit loop's index arithmetic, not unrelated constructor state.
indices=[]
for index in range(6,96,9):indices.extend([index-6,index-3,index])
assert indices==list(range(0,90,3))
words=[sum(1<<(bit%32) for bit in indices if bit//32==word) for word in range(3)]
report={'schema_version':1,'functions':functions,'addressed_strings':strings,
 'input':{'function':'821C9138','anchor':'821C9AF8..821C9C24','event_guard':'r22==5','state_field':244,'routes':{'1':'confirmation output state240; value1 calls821CA168 at821C9A90','2':'821C9C14 calls821CA528; no cash purchase/installation call in this branch','4':'confirmation output state236; value1 calls821CA168 (direct apply)','3':'confirmation output state236; value1 calls821CA448 (remove)'}},
 'challenge':{'function':'821CA528','ordinary':'Writes category260/item256/league248 into profile2124/2128/2132; calls8234BAE8 with mod_tuning_challenge','scene_lookup':'CarChallengeSelect at821CA6D8','prototype_or_nitro':'If264!=0 or268!=0, checks8221ACB8(league248,category260+flag268); zero result displays no/dialog and returns without normal transition','limits':'Transition payload does not prove sponsor event ordering or the reward bit writer.'},
 'ordinary_license_constructor':{'function':'82217870','anchor':'loc821C79B8 arithmetic must be read in retained original function (address label may differ)','clear':'Clears90 bits in profile base528*4=2112','set_indices':indices,'words_hex':[f'{word:08x}'for word in words],'meaning':'Every third/item0 default-owned, items1/2 not set by this constructor loop; no sponsor reward mapping inferred.'},
 'limits':['Source-only contract; no runtime data, DLL or prior versioned contract changed.','No inferred cash eligibility for state2.','Input event r22 numeric5 retained without inventing controller button name.']}
# Preserve exact source label rather than guessed constructor address.
report['ordinary_license_constructor']['anchor']='Retained82217870 loop initializesr11=6, setsr11-6/r11-3/r11, increments9 until96'
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('Staged exact state2 challenge route and ordinary initial license bit words',report['ordinary_license_constructor']['words_hex'])
