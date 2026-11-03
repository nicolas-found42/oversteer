"""Stage exact filename-bound original M/F idle clips on recovered source rigs."""
import json,struct,hashlib,sys,shutil
from pathlib import Path
from jfs_hash import filename_hash
from character_animation import append_source_clip
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'staged';OUT.mkdir(exist_ok=True);reports=[]
for actor,label,key in [('native_male_baggy_t','CommonMale_AvatarIdle01','9ef95b69'),('native_female_zip','CommonFemale_AvatarIdle01','64edb483')]:
 assert filename_hash(label+'.anm')==int(key,16)
 clip=json.loads((SOURCE/'decoded-anm'/('anm-'+key+'.json')).read_text());path=ROOT/'godot/assets/characters'/(actor+'.glb');raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=bytearray(raw[28+size:])
 for image in doc.get('images',[]):
  if 'uri'in image:
   destination=OUT/image['uri'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path.parent/image['uri'],destination)
 animation,evidence=append_source_clip(doc,binary,clip,label,key)
 doc['animations']=[animation];doc.setdefault('extras',{})['nativeIdleAnimation']=evidence;doc['buffers'][0]['byteLength']=len(binary)
 while len(binary)%4:binary.append(0)
 payload=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();payload+=b' '*((-len(payload))%4);(OUT/path.name).write_bytes(struct.pack('<4sII',b'glTF',2,28+len(payload)+len(binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(binary),0x004e4942)+binary);reports.append(dict(actor=actor,**evidence))
 if '--publish'in sys.argv:shutil.copyfile(OUT/path.name,path)
if '--publish'in sys.argv:
 p=ROOT/'godot/assets/characters/avatars.json';manifest=json.loads(p.read_text());by={r['actor']:r for r in reports}
 for actor in manifest['characters']:
  if actor['id']in by:actor['idle_animation']=by[actor['id']]['name'];actor['idle_animation_source']=by[actor['id']];actor['source_status']='Original component geometry, source rig/weights and exact filename-bound native idle; assembled clothes, common head and shader finishes remain adaptations, not exact recovered presets/morphs.'
 p.write_text(json.dumps(manifest,indent=2)+'\n')
(SOURCE/'native-idle-bindings.json').write_text(json.dumps(reports,indent=2)+'\n');print('Published'if'--publish'in sys.argv else'Staged','2 exact original native idle clips')
