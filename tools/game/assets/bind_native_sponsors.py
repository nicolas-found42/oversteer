"""Bind unique original sponsor challenges; original unlock mapping unresolved."""
import json,hashlib,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
from native_scripts import record_for_filename
bases=['L8_Rookie','L7','L6','L5','L4','L3','L2','L1','L0_WC','L00_Elite']
records=[]
for league,base in enumerate(bases):
 record=record_for_filename(f'Goals\\Goals\\{base}_Sponsor.txt')
 if record:record['league']=league;records.append(record)
contentp=ROOT/'data/juiced2/content.json';content=json.loads(contentp.read_text());content['events']=[e for e in content['events']if not e.get('is_sponsor')];tracks={t['native_tag']:t for t in json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks']};seen={};native=[]
def pairs(row):return {str(row[i]):row[i+1]for i in range(0,len(row)-1,2)}
for r in records:
 if not any(f and f[0]=='SponsorType'for f in r['fields']):continue
 contests=[];c=None
 for fi,f in enumerate(r['fields']):
  if f[0]=='[Contest]':c={'header':pairs(f[1:]),'rows':[],'start_field':fi}
  elif f[0]=='[EndContest]':
   if c:contests.append(c);c=None
  elif c is not None:c['rows'].append(f)
 for ci,c in enumerate(contests):
  fingerprint=hashlib.sha256(json.dumps([r['filename'],c['header'],c['rows']],sort_keys=True).encode()).hexdigest()
  if fingerprint in seen:seen[fingerprint]['source_duplicates'].append(dict(key=r['key'],member=r['index'],contest_index=ci));continue
  f={str(f[0]).lower():f[1:]for f in c['rows']if f};route=next((pairs(row[1:])for row in c['rows']if row[0]=='[Event]'),{});tag=route.get('Route');track=tracks.get(tag)
  if not track:continue
  mode={'LapTimeChallenge':'LapTime','PerfectLapChallenge':'PerfectLap','BeatCarChallenge':'BeatCar','CarBeaterChallenge':'BeatCar','SpeedChallenge':'SpeedChallenge','DriftEnduro':'DriftEndurance'}.get(c['header'].get('SubType'),'Circuit');target=float(f.get('sponsordata',[0])[0]);sponsor=str(f.get('sponsortype',[''])[0]);contestants=[row for row in c['rows']if row[0]=='Contestant'];ident=f'sponsor_{r["key"]}_{ci:02d}';name=f'{sponsor} Sponsor · {track["name"]} · {mode}'
  event=dict(id=ident,name=name,track_id=track['id'],mode=mode,league=r['league'],laps=int(route.get('Laps',1)),reward=0,target=target,opponents=max(0,len(contestants)-1),stages=[dict(track_id=track['id'],laps=int(route.get('Laps',1)),target=target)],drivers_per_crew=1,contest_type='Sponsor',challenge_data=target,prize_type='SponsorUpgrade',endurance=0,qualifier=False,rounds=1,lives=0,time_limit=target if mode in ['LapTime','PerfectLap','SpeedChallenge']else 0,entrance_fee=0,target_car=next((str(row[2])for row in contestants if len(row)>2 and row[1]=='Stig'),None),sponsor_type=sponsor,is_sponsor=True,contestants=[dict(tag=str(row[1]),car_id='',team=0,native_car=str(row[2])if len(row)>2 else'')for row in contestants]);event['native_discipline']=c['header']['Discipline'];event['native_discipline_index']=['Circuit','Drift','TestDrive','Solo'].index(event['native_discipline']);event['native_subtype']=str(c['header'].get('SubType','None'));event['prizes']=[];content['events'].append(event);source=dict(id=ident,source_key=r['key'],source_member=r['index'],source_sha256=r['sha256'],source_field_index=c['start_field'],native_header=c['header'],native_rows=c['rows'],source_duplicates=[],source_filename=r['filename'],league=r['league'],unlock_status='exact native league association via filename hash and mastercatalog903ab5c5');native.append(source);seen[fingerprint]=source
contentp.write_text(json.dumps(content,indent=2)+'\n');(ROOT/'godot/assets/game-content.json').write_text(json.dumps(content,separators=(',',':'))+'\n');(ROOT/'data/juiced2/native-sponsors.json').write_text(json.dumps(native,indent=2)+'\n');print('Bound',len(native),'unique native sponsor challenges;',len(content['events']),'total native contests');print(collections.Counter(e['mode']for e in content['events']))
