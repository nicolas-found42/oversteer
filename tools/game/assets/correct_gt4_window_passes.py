"""Translate verified Evo native window-only framebuffer passes to neutral PBR.

The 86-triangle window primitive and its identical reflection pass cover the
windscreen, side and rear glass. Their native texture is an auxiliary body atlas,
not directly usable static windscreen RGB. Preserve their exact geometry and
factory mappings; translate only these identified window material families.
"""
import json,struct,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];p=ROOT/'godot/assets/cars/GT4_MITS0001.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);tail=raw[20+n:];windows=[];aux=[]
for i,m in enumerate(d['materials']):
 if re.search(r'body_set0_tex35_mat1_OPAQUE_paint\d+$',m['name']):
  m['pbrMetallicRoughness']={'baseColorFactor':[.012,.018,.025,.98],'metallicFactor':.05,'roughnessFactor':.12};m['alphaMode']='BLEND';m.pop('alphaCutoff',None);m.setdefault('extras',{})['oversteerTranslation']='Verified original86trianglewindow-only pass: neutral translucent PBR substitutes native framebuffer/auxiliary atlas shader';windows.append(i)
 elif re.search(r'body_set0_tex36_mat-1_BLEND_paint\d+$',m['name']):
  m['pbrMetallicRoughness']={'baseColorFactor':[0,0,0,0],'metallicFactor':0,'roughnessFactor':.12};m['alphaMode']='BLEND';m.setdefault('extras',{})['oversteerTranslation']='Native identical86trianglewindow reflection/ID pass suppressed in static PBR; original window surface retained in tex35 pass';aux.append(i)
assert len(windows)==len(aux)==6
# Both source passes use exactly the same original86triangle window surface.
body=next(m for m in d['meshes']if m['name']=='body');wp=next(pr for pr in body['primitives']if pr['material']==windows[0]);ap=next(pr for pr in body['primitives']if pr['material']==aux[0]);assert d['accessors'][wp['indices']]['count']==d['accessors'][ap['indices']]['count']==258
j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);result=struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail;p.write_bytes(result)
cp=ROOT/'data/juiced2/cars.json';cars=json.loads(cp.read_text());car=next(c for c in cars['cars']if c['code']=='GT4_MITS0001');car['paint_materials']=[m for m in car['paint_materials']if m['index']not in windows+aux];car['prepared_sha256']=hashlib.sha256(result).hexdigest();cp.write_text(json.dumps(cars,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(cp.read_bytes());(ROOT/'artifacts/juiced2-build/evo-window-pass-verification.json').write_text(json.dumps(dict(window_materials=windows,auxiliary_materials=aux,source_triangles=86,geometry_status='original source triangle topology retained',translation='authored neutral PBR window finish; native framebuffer shader execution not asserted'),indent=2)+'\n');print('Translated6factorywindow passes, excluded from arbitrary paint')
