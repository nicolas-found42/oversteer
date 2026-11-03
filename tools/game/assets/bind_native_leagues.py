"""Bind the exact native ten-league goal catalog by filename/hash evidence."""
import json
from pathlib import Path
from native_scripts import record_for_filename
ROOT=Path(__file__).resolve().parents[3];cp=ROOT/'data/juiced2/content.json';content=json.loads(cp.read_text());league_names=['Rookie','League 7','League 6','League 5','League 4','League 3','League 2','League 1','World Class','HIN Elite'];bases=['L8_Rookie','L7','L6','L5','L4','L3','L2','L1','L0_WC','L00_Elite'];leagues=[];evidence=[]
for number,(name,base)in enumerate(zip(league_names,bases)):
 filename=f'Goals\\Goals\\{base}_Goal.txt';record=record_for_filename(filename);assert record;required=next(f[1]for f in record['fields']if f[0]=='NumOptionalGoalsRequired');goals=[];current=None
 for row in record['fields']:
  if row[0]=='[Goal]':current=[]
  elif row[0]=='[EndGoal]':
   fields={str(f[0]).lower():f[1:]for f in current if f};type_field=fields.get('type',['Unknown']);goal=dict(id=f'goal_{record["key"]}_{len(goals):02d}',description=' '.join(str(s)for s in fields.get('description',[])),kind=str(type_field[0]),args=type_field[1:],discipline=str(fields.get('discipline',['Any'])[0]),subtype=str(fields.get('subtype',[''])[0]),location=str(fields.get('location',[''])[0]),route=str(fields.get('route',[''])[0]),contest_type=str(fields.get('contesttype',[''])[0]),car_class=str(fields.get('carclass',[''])[0]),prototype='prototype'in fields,extreme_nos='extremenos'in fields,team_race='teamrace'in fields,endurance='endurance'in fields,prize_type=str(fields.get('prizetype',[''])[0]),qualifier='classqualifier'in fields,vis_unlock='visunlock'in fields,prot_unlock='protunlock'in fields,native_rows=current);goals.append(goal);current=None
  elif current is not None:current.append(row)
 league=dict(league=number,name=name,optional_goals_required=int(required),goals=goals,source_filename=filename,source_key=record['key'],source_member=record['index'],source_sha256=record['sha256'],event_source_filename=f'Goals\\Goals\\{base}_Evt.txt',sponsor_source_filename=f'Goals\\Goals\\{base}_Sponsor.txt');leagues.append(league);evidence.append(record)
content['leagues']=leagues;tracks=json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks'];by={t['id']:t for t in tracks}
for t in content['tracks']:
 t['location']=str((by[t['id']].get('native_route_fields',{}).get('LocationName')or[''])[0]);t['native_route']=by[t['id']]['native_tag']
cp.write_text(json.dumps(content,indent=2)+'\n');(ROOT/'godot/assets/game-content.json').write_text(json.dumps(content,separators=(',',':'))+'\n');(ROOT/'data/juiced2/leagues.json').write_text(json.dumps(dict(leagues=leagues,master_filename='Goals\\SinglePlayGoals.txt',master_catalog_source_key='903ab5c5'),indent=2)+'\n');(ROOT/'artifacts/juiced2-build/native-league-goal-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');print('Bound',len(leagues),'exact native leagues;',sum(len(l['goals'])for l in leagues),'native goals')
