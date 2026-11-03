"""Retain original JSM material slots and component texture-replacement bindings.

This inventories source references; JTD shader execution and component export are
separate work. It never writes runtime assets.
"""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'artifacts/juiced2-build/characters'
catalog=json.loads((SOURCE/'component-catalog-evidence.json').read_text())
textures=json.loads((SOURCE/'avatar-materials.json').read_text())
by_texture={r['name'].lower():r for r in textures['textures']}
slots={}
for skin in catalog['skins']:
 path=ROOT/skin['path'];raw=path.read_bytes();at=raw.rfind(struct.pack('<I',0x70000004));assert at>=0
 count=struct.unpack_from('<I',raw,at+4)[0];cursor=at+8;materials=[]
 for i in range(count):
  kind,length=struct.unpack_from('<2I',raw,cursor);assert kind==3 and 0<=length<512
  data=raw[cursor+8:cursor+8+length];assert raw[cursor+8+length]==0
  name=data.decode();cursor=(cursor+8+length+1+3)&~3
  materials.append(dict(slot=i,native_jtd=name))
 assert struct.unpack_from('<I',raw,cursor)[0]==0x70000009
 slots[skin['key']]=dict(native_skin=skin['native_name'],source=skin['path'],sha256=hashlib.sha256(raw).hexdigest(),materials=materials)
components=[]
for row in catalog['components']:
 replacements={r[1].lower():r[2] for r in row['native_rows'] if r[0]=='texture' and len(r)>=3}
 resolved=[]
 for skin in row['skin_bindings']:
  for material in slots[skin['key']]['materials']:
   base=Path(material['native_jtd']).stem;target=replacements.get(base.lower(),base);image=by_texture.get(target.lower())
   resolved.append(dict(skin_key=skin['key'],slot=material['slot'],native_jtd=material['native_jtd'],replacement_name=target,texture_path=image['path'] if image else None,texture_source=image['source'] if image else None))
 components.append(dict(component_id=row['id'],name=row['name'],category=row['category'],materials=resolved))
report=dict(skins=list(slots.values()),components=components,summary=dict(skins=len(slots),component_material_slots=sum(len(c['materials']) for c in components),resolved_original_images=sum(bool(m['texture_path']) for c in components for m in c['materials'])),limits=['Material list order is exact serialized JSM order; draw-group index base remains to be verified before binding.','JTD stem to same-name DDT and component replacement resolution are candidate image bindings, not recovered native JTD shader execution.','Original HSV modification and normal-map execution remain separate.'])
(SOURCE/'component-material-slots.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(report['summary'])
