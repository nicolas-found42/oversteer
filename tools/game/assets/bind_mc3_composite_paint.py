"""Bind source-selected carpaint composite children omitted by direct-class lookup."""
import json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];path=ROOT/'data/juiced2/cars.json';catalog=json.loads(path.read_text());report=[];OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit'
for car in catalog['cars']:
 if car['game']!='midnight-club-3-remix':continue
 raw=(ROOT/'godot/assets/cars'/(car['code']+'.glb')).read_bytes();d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);selected={r['index']for r in car['paint_materials']};added=[]
 for index,material in enumerate(d['materials']):
  ex=material.get('extras',{});graph=ex.get('native_material',{});root=graph.get('root',{})
  if root.get('kind')!='composite':continue
  choice=root.get('selected');children=root.get('children',[])
  if not isinstance(choice,int)or not 0<=choice<len(children):continue
  child=children[choice]
  if child.get('template')!='carpaint.shadert'or not child.get('paint_input_indices'):continue
  evidence=dict(kind='Original static-selected native composite child',source_carrier_sha256=graph['source_carrier_sha256'],root_source_offset=root['source_offset'],selected_child=choice,template=child['template'],paint_input_indices=child['paint_input_indices'],limits=['Original selected child is used for this static prepared model; runtime composite selector switching is not emulated.','Neutral source preview factors remain a renderer adaptation, not recovered native paint RGB.'])
  if index not in selected:
   factor=material['pbrMetallicRoughness'].get('baseColorFactor',[1]*4);car['paint_materials'].append(dict(index=index,name=material['name'],factory_luma_linear=sum(a*b for a,b in zip(factor[:3],[.2126,.7152,.0722])),source=evidence));selected.add(index)
  added.append(dict(material=index,name=material['name'],source=evidence))
 report.append(dict(code=car['code'],selected_carpaint_composites=added))
(OUT/'staged-composite-paint-cars.json').write_text(json.dumps(catalog,indent=2)+'\n');(OUT/'mc3-composite-paint-bindings.json').write_text(json.dumps(report,indent=2)+'\n')
if '--publish'in sys.argv:path.write_text(json.dumps(catalog,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(path.read_bytes())
print('Published'if'--publish'in sys.argv else'Staged',sum(len(r['selected_carpaint_composites'])for r in report),'source-selected MC3 carpaint composite bindings')
