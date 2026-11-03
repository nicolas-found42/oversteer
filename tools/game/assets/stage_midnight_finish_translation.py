"""Stage explicit native shader-class PBR translations; never publish implicitly.

The donor preview exports static diffuse colors but does not emulate native
reflection/glass. Finishes below are documented renderer adaptations, not shader
recovery. Unknown lamps/interiors and their colors remain unchanged.
"""
import json,struct,sys,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit/midnight';OUT.mkdir(exist_ok=True)
report=[];catalog_path=ROOT/'data/juiced2/cars.json';catalog=json.loads(catalog_path.read_text())
for car in catalog['cars']:
 if car['game']not in ['midnight-club-los-angeles','midnight-club-3-remix']:continue
 path=ROOT/'godot/assets/cars'/f"{car['code']}.glb";raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);tail=raw[20+size:];changes=[]
 for index,material in enumerate(doc['materials']):
  ex=material.get('extras',{});shader=ex.get('sourceShader',ex.get('shader_category',''));p=material['pbrMetallicRoughness'];rule=None
  if shader in ['WheelRubber','rubber','CarTire']and'baseColorTexture'not in p:
   p.update(baseColorFactor=[.025,.025,.025,1],roughnessFactor=.85,metallicFactor=0);rule='Explicit rubber shader class; neutral dark matte PBR adaptation'
  elif shader=='BlackOpaqueGlass':
   p.update(baseColorFactor=[.012,.015,.018,1],roughnessFactor=.12,metallicFactor=.05);rule='Explicit black opaque glass class; neutral dark glossy PBR adaptation'
  elif shader in ['Chrome','chrome','aa_chrome','masked_chrome','BumpedAlphaChrome']:
   p.update(roughnessFactor=.14,metallicFactor=1);rule='Explicit chrome shader class; reflective PBR finish adaptation, original albedo retained'
  elif shader in ['BrushedMetal','WheelBrakeRotor']:
   p.update(roughnessFactor=.4,metallicFactor=1);rule='Explicit metal shader class; rough metallic PBR adaptation, original albedo retained'
  elif shader=='RimMain':
   p.update(roughnessFactor=.24,metallicFactor=.85);rule='Explicit wheel rim shader class; metallic PBR adaptation, original albedo retained'
  if rule:ex['oversteerStagedFinishTranslation']=rule;material['extras']=ex;changes.append({'index':index,'shader':shader,'rule':rule})
 doc.setdefault('extras',{})['oversteerStagedFinishLimits']=['PBR renderer adaptations from explicit source shader classes; native reflection/glass shader execution is not recovered.','Unresolved white lamp/interior diffuse bindings remain unchanged.']
 payload=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();payload+=b' '*((-len(payload))%4);result=struct.pack('<4sIIII',b'glTF',2,20+len(payload)+len(tail),len(payload),0x4e4f534a)+payload+tail;(OUT/path.name).write_bytes(result);report.append({'code':car['code'],'changes':changes,'source_sha256':hashlib.sha256(raw).hexdigest(),'prepared_sha256':hashlib.sha256(result).hexdigest()})
 if '--publish'in sys.argv:path.write_bytes(result);car['prepared_sha256']=hashlib.sha256(result).hexdigest();car['midnight_finish_translation']=report[-1]
if '--publish'in sys.argv:catalog_path.write_text(json.dumps(catalog,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(catalog_path.read_bytes())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Published'if'--publish'in sys.argv else'Staged',len(report),'Midnight donor finish translations')
