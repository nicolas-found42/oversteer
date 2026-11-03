"""Retain source-proven native BTF grid records without changing runtime data."""
import hashlib,json,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'artifacts/juiced2-build/native-ai/starts';OUT.mkdir(parents=True,exist_ok=True)
rows=[]
for track in json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks']:
 path=ROOT/'artifacts/juiced2-build/courses'/f"{track['id']}.btf"
 raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==track['source']['sha256']
 count=struct.unpack_from('>I',raw)[0];assert 0<count<128
 origin=track['source']['origin_source_units'];grid=[]
 for i in range(count):
  p=struct.unpack_from('>4f',raw,4+16*i);assert all(math.isfinite(v)for v in p)
  grid.append(dict(position=[-p[0]/100-origin[0]/100,p[1]/100-origin[1]/100,p[2]/100-origin[2]/100],native_position=list(p[:3]),native_yaw_radians=p[3],source_record_index=i,source_byte_offset=4+16*i))
 rows.append(dict(id=track['id'],start_grid=grid,source=dict(path=track['source']['path'],sha256=track['source']['sha256'],origin_source_units=origin,loader='82140F20',getter='82141CD0',placement_consumer='821046E4 -> 820F2E60',yaw_matrix='82082EC0'),limits=['Native yaw retained verbatim pending core forward-axis conversion; positions use existing reflected-X track-local metre transform.','Original grid index is vehicle632->32; index beyond available count clamps to last record in native getter.']))
(OUT/'all33.json').write_text(json.dumps(dict(tracks=rows),indent=2,allow_nan=False)+'\n')
print('Staged',len(rows),'native grids;',sum(len(r['start_grid'])for r in rows),'exact records; runtime unchanged')
