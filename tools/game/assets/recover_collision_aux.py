"""Recover original per-world collision properties, BCP overrides and atmosphere text."""
import hashlib,json,re,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/collision/auxiliary';SOURCE.mkdir(exist_ok=True);inventory=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());files={r['path'].lower():r for r in inventory['files']};tracks=json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks'];candidates={'Surface_Properties.txt'}
for track in tracks:
 path=Path(track['source']['path']);candidates.update([path.stem+'.bcp',path.parent.name+'.bcp',str(path.with_suffix('.bcp')).replace('/','\\')])
bindings={filename_hash(name):name for name in candidates};reports=[]
with open(inventory['iso'],'rb')as iso:
 for key,row in files.items():
  if not key.startswith('tracks/')or key.count('/')!=1 or not key.endswith('.jfs'):continue
  header=files[key+'hdr'];iso.seek(header['offset']);h=iso.read(header['size']);members=[]
  for index in range(struct.unpack_from('>I',h)[0]):
   native_key,offset,packed,size,_,_=struct.unpack_from('>6I',h,4+24*index);iso.seek(row['offset']+offset);raw=iso.read(packed);raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size;name=bindings.get(native_key);text=raw.decode(errors='replace');kind='surface_properties'if'[BeginSurfaceProperties]'in text else'atmosphere'if'[BeginAtmosphere]'in text else'bcp'if name and name.endswith('.bcp')else'other'
   if kind=='other':continue
   stem=Path(row['path']).stem;path=SOURCE/f'{stem}-{native_key:08x}.txt';path.write_bytes(raw);members.append(dict(kind=kind,filename=name,key=f'{native_key:08x}',member=index,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),text=text))
  reports.append(dict(bank=row['path'],members=members))
(SOURCE/'manifest.json').write_text(json.dumps(dict(banks=reports,limits=['Exact filename-hash bindings only; anonymous atmosphere members retain keys without invented day/night labels.','BCP overrides are explicit per-patch grid counts; serialized CLD tail metadata is not assumed to be universal tessellation resolution.']),indent=2)+'\n');print(len(reports),'world banks;',sum(len(r['members'])for r in reports),'source auxiliary members; runtime unchanged')
