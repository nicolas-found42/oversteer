"""Stage all33 exact native collision catalogs into core content; --publish applies."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/collision';content_path=ROOT/'data/juiced2/content.json';content=json.loads(content_path.read_text());tracks={t['id']:t for t in json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks']};report=[]
assert len(content['tracks'])==33
for track in content['tracks']:
 path=SOURCE/'track-local'/(track['id']+'.json');collision=json.loads(path.read_text());assert collision['track_id']==track['id'];assert collision['source']['origin_source_units']==tracks[track['id']]['source']['origin_source_units']
 raw_path=SOURCE/collision['source']['path'].replace('/','--');assert hashlib.sha256(raw_path.read_bytes()).hexdigest()==collision['source']['sha256'];n=len(collision['points'])
 for kind in ['triangles','polygons','patches','splines']:
  for primitive in collision[kind]:assert all(0<=i<n for i in primitive['indices'])
 track['collision']=collision;report.append(dict(id=track['id'],source_sha256=collision['source']['sha256'],counts={k:len(collision[k])for k in ['points','triangles','polygons','patches','splines']}))
payload=json.dumps(content,separators=(',',':'),allow_nan=False)+'\n';staged=SOURCE/'staged-game-content.json';staged.write_text(payload)
(SOURCE/'content-binding.json').write_text(json.dumps(dict(track_count=len(report),content_sha256=hashlib.sha256(payload.encode()).hexdigest(),content_bytes=len(payload.encode()),tracks=report,limits=['Exact native controls retained; discrete query tessellation behavior belongs to core and is verified separately.','No claim that explicit source triangles are all nondegenerate; native degenerate IDs remain retained.']),indent=2)+'\n')
if '--publish'in sys.argv:content_path.write_text(payload);(ROOT/'godot/assets/game-content.json').write_text(payload)
print('Published'if'--publish'in sys.argv else'Staged','all33nativecollisionobjects;',len(payload.encode()),'contentbytes')
