"""Stage exact native route predicates without rebuilding unrelated production data."""
import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
content=json.loads((ROOT/'data/juiced2/content.json').read_text())
tracks={t['id']:t for t in json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks']}
for track in content['tracks']:
 track['native_route']=tracks[track['id']]['native_tag']
goals=[]
for league in content['leagues']:
 for goal in league['goals']:
  rows=[row for row in goal['native_rows']if row and str(row[0]).lower()=='route']
  assert len(rows)<=1
  goal['route']=str(rows[0][1])if rows else''
  if rows:goals.append(dict(id=goal['id'],league=league['league'],route=goal['route'],native_row=rows[0]))
assert len(content['tracks'])==33 and len(goals)==7
career=json.loads((ROOT/'data/juiced2/native-career.json').read_text())['contests']
sponsors=json.loads((ROOT/'data/juiced2/native-sponsors.json').read_text())
source_by={e['id']:e for e in career+sponsors};disciplines=[]
for event in content['events']:
 source=source_by[event['id']];token=source['native_header']['Discipline'];assert token in ['Circuit','Drift','TestDrive','Solo']
 event['native_discipline']=token;event['native_discipline_index']=['Circuit','Drift','TestDrive','Solo'].index(token)
 event['native_discipline_source']={k:source[k]for k in ['source_key','source_member','source_sha256','source_field_index']}
 disciplines.append(dict(id=event['id'],native_discipline=token,index=event['native_discipline_index']))
assert len(disciplines)==463
out=ROOT/'artifacts/juiced2-build/presentation'
(out/'native-goal-routes.json').write_text(json.dumps(dict(event_disciplines=disciplines,goals=goals,tracks=[dict(id=t['id'],native_route=t['native_route'])for t in content['tracks']],source='Native route catalog be76698b Tag/Directory/RouteWorldName bindings; exact goal Route rows',limits=['Parser/consumer route predicate independently traced by core; no route-ID guessing']),indent=2)+'\n')
encoded=json.dumps(content,indent=2,allow_nan=False)+'\n'
(out/'content-with-native-goal-routes.json').write_text(encoded)
if '--publish'in sys.argv:
 (ROOT/'data/juiced2/content.json').write_text(encoded)
 (ROOT/'godot/assets/game-content.json').write_text(encoded)
print('Published'if'--publish'in sys.argv else'Staged',len(goals),'goal route predicates,33native route tags and463original disciplines')
