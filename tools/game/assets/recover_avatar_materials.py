"""Decode exact named avatar component texture bindings from original avatar bank."""
import hashlib,json,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
from xenos_texture import decode
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'avatar-textures';OUT.mkdir(exist_ok=True);inventory=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());files={r['path'].lower():r for r in inventory['files']};components=json.loads((SOURCE/'component-catalog-evidence.json').read_text());names=sorted({r[2]for c in components['components']for r in c['native_rows']if r[0]=='texture'and len(r)>=3});reports=[];unresolved=[]
slots_path=SOURCE/'component-material-slots.json'
if slots_path.exists():
 slots=json.loads(slots_path.read_text());names=sorted(set(names)|{Path(m['native_jtd']).stem for skin in slots['skins'] for m in skin['materials'] if m['native_jtd']})
with open(inventory['iso'],'rb')as iso:
 banks={}
 for bank in ['avatar','player01']:
  row=files[f'skinned/{bank}.jfshdr'];iso.seek(row['offset']);h=iso.read(row['size']);banks[bank]={struct.unpack_from('>I',h,4+24*i)[0]:(i,struct.unpack_from('>6I',h,4+24*i))for i in range(struct.unpack_from('>I',h)[0])}
 for name in names:
  key=filename_hash(name+'.ddt');bank=next((b for b in banks if key in banks[b]),None)
  if bank is None:unresolved.append(dict(name=name,key=f'{key:08x}',reason='exact filename hash absent'));continue
  index,(_,offset,packed,size,_,_)=banks[bank][key];iso.seek(files[f'skinned/{bank}.jfs']['offset']+offset);raw=iso.read(packed);raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size
  fmt,width,height=struct.unpack_from('>3I',raw);image=decode(raw[40:],width,height,fmt)
  if image is None:unresolved.append(dict(name=name,key=f'{key:08x}',reason='unsupported source pixel format',format=hex(fmt)));continue
  path=OUT/f'{key:08x}.png';image.save(path);reports.append(dict(name=name,key=f'{key:08x}',path=str(path.relative_to(ROOT)),width=width,height=height,source=dict(bank=bank+'.jfs',filename=name+'.ddt',member=index,offset=offset,packed_size=packed,decoded_size=size,format=hex(fmt),sha256=hashlib.sha256(raw).hexdigest())))
report=dict(named_component_textures=len(names),textures=reports,unresolved=unresolved,limits=['Exact original component texture art recovered; component/material replacement and original HSV shader execution require separate binding.'])
(SOURCE/'avatar-materials.json').write_text(json.dumps(report,indent=2)+'\n');print('Decoded',len(reports),'of',len(names),'original named avatar textures;',len(unresolved),'unresolved; runtime unchanged')
