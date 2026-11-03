"""Retain exact original head JSM morph vectors; runtime application not claimed."""
import hashlib,json,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';path=SOURCE/'avatar_lo-cc0ee14d.bin';raw=path.read_bytes();cursor=raw.find(struct.pack('<I',0x7000000c));assert cursor>0;targets=[]
while struct.unpack_from('<I',raw,cursor)[0]==0x7000000c:
 start=cursor;length=struct.unpack_from('<I',raw,cursor+4)[0];cursor+=8;name=raw[cursor:cursor+length].decode();assert raw[cursor+length]==0;cursor=(cursor+length+1+3)&~3
 first,count=struct.unpack_from('<2I',raw,cursor);cursor=(cursor+8+15)&~15;position_offset=cursor;positions=[list(struct.unpack_from('<3f',raw,cursor+i*12))for i in range(count)];cursor=(cursor+count*12+4+15)&~15;normal_offset=cursor;normals=[list(struct.unpack_from('<3f',raw,cursor+i*12))for i in range(count)];cursor+=count*12
 assert all(math.isfinite(v)for values in positions+normals for v in values)
 targets.append(dict(name=name,first_vertex=first,vertex_count=count,source_chunk_offset=start,position_offset=position_offset,normal_offset=normal_offset,position_vectors=positions,normal_vectors=normals))
report=dict(source=dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),loader='8223E568',target_constructor='822513D8'),targets=targets,limits=['Vectors and sparse contiguous vertex spans are exact source data; additive/delta application and default player appearance weights require native consumer proof before runtime binding.','MRP named time curves are separate from these original geometric shape targets.'])
(SOURCE/'decoded-head-morphs.json').write_text(json.dumps(report,separators=(',',':'),allow_nan=False)+'\n');(SOURCE/'head-morph-inventory.json').write_text(json.dumps(dict(source=report['source'],targets=[{k:v for k,v in t.items()if k not in['position_vectors','normal_vectors']}for t in targets],limits=report['limits']),indent=2)+'\n');print('Recovered',len(targets),'exact source geometric morph targets; runtime unchanged')
# Original56-entry attribute-name table; the first45 bind head geometry.
sections=ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections';data=(sections/'824A0000-.data.bin').read_bytes();rdata=(sections/'82000400-.rdata.bin').read_bytes();attributes=[]
for index in range(56):
 pointer=struct.unpack_from('>I',data,0x824af608-0x824a0000+index*4)[0];offset=pointer-0x82000400;name=rdata[offset:rdata.index(0,offset)].decode();attributes.append(dict(index=index,name=name,kind='geometry'if index<45 else'skeleton_or_material_or_profile',default_weight=0))
assert all(any(t['name'].lower()==a['name'].lower()for t in targets)for a in attributes[:45])
(SOURCE/'native-morph-attributes.json').write_text(json.dumps(dict(source_table='824AF608',constructor='82237C10',composition='82239018 -> 8223B298 -> 82257450',position_rule='base_position + sum(weight * sparse_target_position_delta)',attributes=attributes,limits=['Zero constructor levels are not actualcreator defaultappearance; recover_avatar_presets.py retains all10source .def presets/all56levels andoriginal controlramps.','The11 non-head attributes need their ownsourceconsumers; native-body-scales.json proves shipped3skeletondatasetsidentity.']),indent=2,allow_nan=False)+'\n')
