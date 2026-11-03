"""Translate explicit recovered glass/rubber shader classes into native PBR."""
import json,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());report=[]
for c in doc['cars']:
 path=ROOT/'godot/assets/cars'/f"{c['code']}.glb";b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);tail=b[20+n:];glass=[];dark=[]
 for i,m in enumerate(d.get('materials',[])):
  ex=m.get('extras',{});shader=ex.get('sourceShader',ex.get('shader_category',''));pbr=m.setdefault('pbrMetallicRoughness',{})
  if shader in ['CarGlass','car_window','car_window_tinted','colored_glass']:
   m['alphaMode']='BLEND';m.pop('alphaCutoff',None);pbr['baseColorFactor']=[.035,.045,.055,.32];pbr['roughnessFactor']=.12;pbr['metallicFactor']=.05;ex['oversteerTranslation']='Artistic neutral translucent PBR for explicitly recovered native glass shader; native screen-space shader not emulated';m['extras']=ex;glass.append(i)
  elif shader in ['blackmatte','black_matte','Underbody','rubber','CarTire'] and 'baseColorTexture' not in pbr:
   pbr['baseColorFactor']=[.025,.025,.025,1];pbr['roughnessFactor']=.85;pbr['metallicFactor']=0;dark.append(i)
 c['paint_materials']=[m for m in c['paint_materials'] if d['materials'][m['index']].get('alphaMode')!='BLEND']
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);out=struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail;path.write_bytes(out);c['prepared_sha256']=hashlib.sha256(out).hexdigest();report.append(dict(code=c['code'],glass_materials=glass,dark_surface_materials=dark))
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes());(ROOT/'artifacts/juiced2-build/donor-surface-corrections.json').write_text(json.dumps(report,indent=2));print('Appliedexplicitnativeglass/dark-class PBRtranslations')
