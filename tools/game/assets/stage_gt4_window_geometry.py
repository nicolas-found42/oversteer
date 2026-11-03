"""Stage PBR translations for four inspected original window-only surface families."""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit/window-surfaces';OUT.mkdir(parents=True,exist_ok=True);catalog=json.loads((ROOT/'data/juiced2/cars.json').read_text());reports=[]
# Exact source families identified by window-region rays and inspected geometric bounds.
families={'GT4_HOND0019':(38,3,34),'GT4_TOYT0006':(21,9,24),'GT4_NISS0021':(35,4,34),'GT4_LNCA0005':(18,1,24)}
for car in catalog['cars']:
 if car['code']not in families:continue
 code=car['code'];texture,material,triangles=families[code];raw=(ROOT/'godot/assets/cars'/f'{code}.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);tail=raw[20+n:];selected=[]
 for index,m in enumerate(doc['materials']):
  if not re.search(rf'body_set0_tex{texture}_mat{material}_(?:OPAQUE|MASK)_paint\d+$',m['name']):continue
  m['pbrMetallicRoughness']={'baseColorFactor':[.012,.018,.025,.98],'metallicFactor':.05,'roughnessFactor':.12};m['alphaMode']='BLEND';m.pop('alphaCutoff',None);m.setdefault('extras',{})['oversteerWindowGeometryTranslation']='Inspected original window-only geometric surface; authored neutral translucent PBR replaces native auxiliary/framebuffer finish, not native GS shader parity';selected.append(index)
 assert selected,code
 body=next(m for m in doc['meshes']if m['name']=='body');prim=next(p for p in body['primitives']if p['material']==selected[0]);assert doc['accessors'][prim['indices']]['count']==triangles*3
 car['paint_materials']=[m for m in car['paint_materials']if m['index']not in selected]
 encoded=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();encoded+=b' '*(-len(encoded)%4);result=struct.pack('<4sIIII',b'glTF',2,20+len(encoded)+len(tail),len(encoded),0x4e4f534a)+encoded+tail;(OUT/f'{code}.glb').write_bytes(result);car['prepared_sha256']=hashlib.sha256(result).hexdigest();reports.append(dict(code=code,window_materials=selected,source_triangles=triangles,before_sha256=hashlib.sha256(raw).hexdigest(),staged_sha256=car['prepared_sha256'],geometry_binary_unchanged=True))
(OUT/'cars.json').write_text(json.dumps(catalog,indent=2)+'\n');(OUT/'manifest.json').write_text(json.dumps(reports,indent=2)+'\n');print('Staged',len(reports),'verified original window-only surface PBR translations; runtime unchanged')
