"""Recover original tunnel atmosphere members from the read-only supplied ISO."""
import hashlib,json,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'artifacts/juiced2-build/tunnel-shaders/lighting';OUT.mkdir(parents=True,exist_ok=True)
inventory=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text())
entries={item['path'].lower():item for item in inventory['files']}
with Path(inventory['iso']).open('rb') as iso:
 def read(path):
  entry=entries[path];iso.seek(entry['offset']);raw=iso.read(entry['size']);assert len(raw)==entry['size'];return raw
 header=read('tracks/tunnel.jfshdr');archive=read('tracks/tunnel.jfs')
assert len(header)==220
names={filename_hash(name):name for name in ['profile.atm','profile22.atm','split_screen.atm','DNA_LAB.atm']}
rows=[]
for index in range(9):
 key,offset,packed,size,*rest=struct.unpack_from('>6I',header,4+24*index)
 raw=archive[offset:offset+packed];assert len(raw)==packed
 raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size and raw.startswith(b'[BeginAtmosphere]')
 path=OUT/f'tunnel-{index}-{key:08x}.bin';path.write_bytes(raw)
 rows.append(dict(index=index,key=f'{key:08x}',offset=offset,packed_size=packed,size=size,header_unknown=rest,filename=names.get(key),sha256=hashlib.sha256(raw).hexdigest()))
report=dict(source_archive='tracks/tunnel.jfs',archive_sha256=hashlib.sha256(archive).hexdigest(),header_sha256=hashlib.sha256(header).hexdigest(),members=rows,limits=['Filename bindings use exact original hash, not phase selection evidence.','Other five filenames and active creator/main camera atmosphere remain unresolved.'])
(OUT/'inventory.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('Recovered nine original atmosphere members; four exact filename hashes')
