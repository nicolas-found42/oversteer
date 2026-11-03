"""Stage filename-bound original podium/crew/betting motion on source rigs.

Unique01/04 betting clips are explicitly retargeted to common M/F assemblies;
the assemblies are not claimed to be Tyrone/Keiko's recovered character presets.
"""
import json,struct,shutil,hashlib,sys
from pathlib import Path
from jfs_hash import filename_hash
from character_animation import append_source_clip
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'staged-actions';OUT.mkdir(exist_ok=True);reports=[]
for actor,prefix,unique,tag in [('native_male_baggy_t','CommonMale','Unique01','Char01'),('native_female_zip','CommonFemale','Unique04','Char04')]:
 roles={'idle':prefix+'_AvatarIdle01','crew_idle':prefix+'_CrewIdle01','podium_happy':prefix+'_PodiumCelebrateHappy01','podium_disappointed':prefix+'_PodiumCelebrateDisapointed01','podium_extatic':prefix+'_PodiumCelebrateExtatic01','bet_positive':unique+'_BetAcceptedPositive01','bet_grudge':unique+'_BetAcceptedGrudge01'}
 path=(SOURCE/'staged-complete'if'--complete'in sys.argv else ROOT/'godot/assets/characters')/(actor+'.glb');raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=bytearray(raw[28+size:]);doc['animations']=[];bindings=[]
 for role,label in roles.items():
  key=f'{filename_hash(label+".anm"):08x}';clip=json.loads((SOURCE/'decoded-anm'/('anm-'+key+'.json')).read_text());animation,evidence=append_source_clip(doc,binary,clip,label,key);evidence['runtime_role']=role
  if role.startswith('bet_'):evidence['retargeting']='Original '+tag+'/'+unique+' local motion applied by exact bone names to the common '+prefix+' assembly; adapted actor identity, not an original character preset.'
  doc['animations'].append(animation);bindings.append(evidence)
 for image in doc.get('images',[]):
  if 'uri'in image:
   destination=OUT/image['uri'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path.parent/image['uri'],destination)
 doc.setdefault('extras',{})['nativeActionBindings']=bindings;doc['extras']['nativeIdleAnimation']=next(x for x in bindings if x['runtime_role']=='idle');doc['extras']['limits']=[x for x in doc['extras'].get('limits',[])if'ANM'not in x]+['Original filename-bound motion exported; native quaternion interpolation represented by glTF LINEAR interpolation. Gender facial morphs and cloth albedo bindings remain incomplete.'];doc['buffers'][0]['byteLength']=len(binary)
 while len(binary)%4:binary.append(0)
 j=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;(OUT/path.name).write_bytes(result);reports.append(dict(actor=actor,roles=roles,bindings=bindings,sha256=hashlib.sha256(result).hexdigest()))
 if '--publish'in sys.argv:shutil.copyfile(OUT/path.name,ROOT/'godot/assets/characters'/path.name)
(OUT/'actions.json').write_text(json.dumps(reports,indent=2)+'\n')
if '--publish'in sys.argv:
 base=SOURCE/'staged-complete'if'--complete'in sys.argv else ROOT/'godot/assets/characters';manifest=json.loads((base/'avatars.json').read_text());by={r['actor']:r for r in reports}
 if '--complete'in sys.argv:
  shutil.copyfile(base/'skinning.json',ROOT/'godot/assets/characters/skinning.json');shutil.copyfile(base/'skinning.json',ROOT/'artifacts/juiced2-build/native-character-skinning.json');shutil.copyfile(base/'verification.json',ROOT/'artifacts/juiced2-build/native-character-verification.json')
 for actor in manifest['characters']:
  if actor['id']not in by:continue
  row=by[actor['id']];actor['idle_animation']=row['roles']['idle'];actor['animation_roles']=row['roles'];actor['animation_sources']=row['bindings'];actor['source_status']='Original component geometry including original hair/scalp, source rig/weights and exact filename-bound native motions; common head, clothing combination, shader finishes and Unique betting retarget are explicit adaptations.'
 (ROOT/'godot/assets/characters/avatars.json').write_text(json.dumps(manifest,indent=2)+'\n')
if '--proof'in sys.argv:
 proof=OUT/'proof';proof.mkdir(exist_ok=True);shutil.copytree(OUT/'textures',proof/'textures',dirs_exist_ok=True)
 for path in OUT.glob('*.glb'):
  raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);tail=raw[20+size:];doc['animations']=[a for a in doc['animations']if'PodiumCelebrateHappy01'in a['name']];assert len(doc['animations'])==1;j=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);(proof/path.name).write_bytes(struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail)
print('Published'if'--publish'in sys.argv else'Staged','14 original clips on2 source assemblies')
