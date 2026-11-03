"""Bind recovered offline contests and native route names to the playable content.

Offline banks are distinguished from online banks by Player0-only contestants.
Exact native event-bank filename hashes bind league rank; raw rows are retained.
"""
import json,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];records=json.loads((ROOT/'artifacts/juiced2-build/core-native-gameplay-config.json').read_text())['matched_records'];by={r['key']:r for r in records}
trackp=ROOT/'data/juiced2/tracks.json';trackdoc=json.loads(trackp.read_text());tracks=trackdoc['tracks'];native_routes=[];cur={}
for f in by['be76698b']['fields']:
 if f[0]=='Route':cur={}
 elif f[0]=='EndRoute':native_routes.append(cur)
 else:cur[f[0]]=f[1:]
route_map={}
for r in native_routes:
 directory=(r.get('Directory')or[''])[0];world=(r.get('RouteWorldName')or[''])[0];tag=(r.get('Tag')or[''])[0];wanted=f'tracks/{directory}/{world}.btf'.lower();t=next((t for t in tracks if t['source']['path'].lower()==wanted),None)
 if t:
  t['name']=(r.get('RouteName')or[t['name']])[0];t['native_tag']=tag;t['native_route_fields']=r;t['native_lap_length_km']=(r.get('LapLength')or[0])[0];t['source']['route_definition_key']='be76698b';route_map[tag]=t
if 'SydneyDrift1' in route_map:route_map['SydneyDrift2']=route_map['SydneyDrift1']  # native contest references absent route2; explicit same-venue adaptation
trackp.write_text(json.dumps(trackdoc,indent=2)+'\n');(ROOT/'godot/assets/tracks.json').write_bytes(trackp.read_bytes())
banks=[(0,'Rookie',5000,'28956449'),(1,'League 7',7000,'cba6a787'),(2,'League 6',10000,'ca32970d'),(3,'League 5',12000,'c8c48fc7'),(4,'League 4',18000,'c75c8b79'),(5,'League 3',22000,'c5fa83ff'),(6,'League 2',30000,'c49e734d'),(7,'League 1',40000,'c348536f'),(8,'World Class',55000,'2a1b9dec'),(9,'HIN Elite',75000,'c1c3cb85')]
mode_map={'DriftRace':'DriftObliterator','DriftKing':'DriftKing','DriftEnduro':'DriftEndurance','SoloDrift':'SoloDrift','TwinDrift':'TwinDrift','Eliminator':'Eliminator','LMS':'LastManStanding','LapTimeChallenge':'LapTime','PerfectLapChallenge':'PerfectLap','BeatCarChallenge':'BeatCar','CarBeaterChallenge':'BeatCar','SpeedChallenge':'SpeedChallenge'}
def pairs(values):
 result={};i=0
 while i<len(values):
  result[str(values[i])]=values[i+1] if i+1<len(values) else True;i+=2
 return result
runtime=[];native=[];leagues=[];unresolved=[]
for league,label,base,key in banks:
 record=by[key];global_endurance=next((f[1]for f in record['fields']if f and f[0]=='Endurance'),30);contests=[];contest=None
 for fi,f in enumerate(record['fields']):
  if f[0]=='[Contest]':
   if contest is not None:contests.append(contest)
   contest=dict(header=pairs(f[1:]),rows=[],stages=[],field_index=fi)
  elif f[0]=='[EndContest]':
   if contest is not None:contests.append(contest);contest=None
  elif contest is not None:
   contest['rows'].append(f)
   if f[0]=='[Event]':contest['stages'].append(pairs(f[1:]))
   elif f[0].lower()in ['challengedata','challengedaya'] and len(f)>1:
    if contest['stages']:contest['stages'][-1]['ChallengeData']=f[1]
 for ci,c in enumerate(contests):
  header=c['header'];fields={str(r[0]).lower():r[1:] for r in c['rows']if r};sub=str(header.get('SubType','None'));discipline=header.get('Discipline','Circuit');ctype=str(header.get('Type','None'));crew=int(header.get('DriversPerCrew',1));mode=mode_map.get(sub,'SoloDrift'if discipline=='Drift' else 'Circuit')
  if discipline=='Circuit' and ctype in ['Tournament','Championship']:mode='CircuitTournament'
  elif discipline=='Circuit' and crew>1:mode='TeamRace'
  stages=[]
  for s in c['stages']:
   route=str(s.get('Route',''));track=route_map.get(route)
   if track is None:unresolved.append(dict(bank=key,contest=ci,route=route));continue
   laps=max(1,int(min(25,global_endurance)/track['native_lap_length_km'])) if 'Endurance' in s else int(s.get('Laps',1));target=float(s.get('ChallengeData',0));stages.append(dict(track_id=track['id'],laps=laps,target=target,native_route=route,native_fields=s))
  if not stages:continue
  contestants=[r for r in c['rows']if r[0]=='Contestant'];opponents=max(0,len(contestants)-1);first=stages[0];target=float(first['target']);sponsor=fields.get('sponsordata',[0]);cash=fields.get('prizecash');reward=base*int(cash[0] if cash and isinstance(cash[0],(int,float))else 1)if cash is not None else 0;prize='Pinks' if 'prizepinks'in fields else'Cash'if cash is not None else'None';qualifier='classqualifier'in fields
  ident=f'native_{key}_{ci:03d}';name=f"{route_map[first['native_route']]['name']} · {re.sub(r'(?<!^)(?=[A-Z])',' ',mode)}";title=' '.join(str(x)for x in fields.get('title',[])).strip('" ')
  if title:name=title
  event=dict(id=ident,name=name,track_id=first['track_id'],mode=mode,league=league,laps=first['laps'],reward=reward,target=target,opponents=opponents,stages=[{k:s[k]for k in ['track_id','laps','target']}for s in stages],drivers_per_crew=crew,contest_type=ctype,challenge_data=target,prize_type=prize,endurance=min(25,global_endurance) if any('Endurance'in s['native_fields']for s in stages)else 0,qualifier=qualifier,rounds=len(stages),lives=0,time_limit=target if mode in ['DriftKing','LapTime','PerfectLap']else 0,entrance_fee=0,target_car=next((str(r[2])for r in contestants if len(r)>2 and r[1]=='Stig'),None))
  event['contestants']=[dict(tag=str(r[1]),car_id='',team=int(r[3])if len(r)>3 and isinstance(r[3],(int,float))else 0,native_car=str(r[2])if len(r)>2 else '')for r in contestants]
  event['native_discipline']=discipline;event['native_discipline_index']=['Circuit','Drift','TestDrive','Solo'].index(discipline);event['prototype']='prototype' in fields;event['extreme_nos']='extremenos' in fields;event['car_class']=str(fields.get('carclass',[''])[0]);event['native_subtype']=sub;event['prizes']=[reward] if reward else []
  runtime.append(event);native.append(dict(id=ident,league=league,source_key=key,source_member=record['index'],source_sha256=record['sha256'],source_field_index=c['field_index'],native_header=header,native_rows=c['rows'],native_stages=stages,adaptations=['League association verified against master903ab5c5 and exact native Goals\\Goals\\... filename hashes.','Native vehicle IDs/opponent roster adapted to accepted30donor identities.','Native unnamed contests receive route/mode display labels.','NativeTIP_DRIFTENDURO inEnglishStrings9108c6c7 confirmscontinuousdriftbank/crashend; no invented lives.','SydneyDrift2 missing native route/geometry: same-venue SydneyDrift1 alias used where referenced.']))
 leagues.append(dict(id=league,name=label,source_key=key,base_cash_prize=base,event_ids=[e['id']for e in runtime if e['league']==league],qualifier_ids=[e['id']for e in runtime if e['league']==league and e['qualifier']],binding='exact master903ab5c5 and native filename hash; offlinebank Player0-only verified'))
p=ROOT/'data/juiced2/content.json';content=json.loads(p.read_text());content['tracks']=[{k:t[k]for k in ['id','name','points','road_width','surface_points','surface_half_widths','wall_half_widths','location']if k in t}for t in tracks];content['events']=runtime;content['leagues']=leagues;p.write_text(json.dumps(content,indent=2)+'\n');(ROOT/'godot/assets/game-content.json').write_text(json.dumps(content,separators=(',',':'))+'\n');(ROOT/'data/juiced2/native-career.json').write_text(json.dumps(dict(leagues=leagues,contests=native,unresolved=unresolved,route_record_key='be76698b'),indent=2)+'\n');print('Bound',len(runtime),'nativeofflinecontests /',len(leagues),'leagues; unresolvedstages',len(unresolved));print(collections.Counter(e['mode']for e in runtime))
