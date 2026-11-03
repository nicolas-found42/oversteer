"""Bind source-proven BTF starting grids; stage by default, publish explicitly."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/native-ai/starts'
source=json.loads((OUT/'all33.json').read_text());by={row['id']:row for row in source['tracks']};assert len(by)==33
for row in by.values():
 raw=(ROOT/'artifacts/juiced2-build/courses'/f"{row['id']}.btf").read_bytes();assert hashlib.sha256(raw).hexdigest()==row['source']['sha256']
content=json.loads((ROOT/'data/juiced2/content.json').read_text());assert{t['id']for t in content['tracks']}==set(by)
for track in content['tracks']:
 row=by[track['id']];track['start_grid']=row['start_grid'];track.setdefault('source',{})['native_start_grid']=row['source']
payload=json.dumps(content,separators=(',',':'),allow_nan=False)+'\n';(OUT/'staged-game-content.json').write_text(payload)
if '--publish'in sys.argv:
 for path in ['data/juiced2/content.json','godot/assets/game-content.json']:(ROOT/path).write_text(payload)
 tracks=json.loads((ROOT/'data/juiced2/tracks.json').read_text())
 for track in tracks['tracks']:track['start_grid']=by[track['id']]['start_grid'];track['source']['native_start_grid']=by[track['id']]['source']
 (ROOT/'data/juiced2/tracks.json').write_text(json.dumps(tracks,indent=2,allow_nan=False)+'\n')
print('Published'if'--publish'in sys.argv else'Staged',len(by),'native grids;',sum(len(r['start_grid'])for r in by.values()),'source records')
