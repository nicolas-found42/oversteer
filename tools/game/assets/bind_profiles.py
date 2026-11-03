"""Bind existing donor profiles to the runtime; preserve proxy provenance."""
import json,re,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());roster={c['code']:c for c in json.loads((ROOT/'data/juiced2/accepted-roster.json').read_text())['cars']}
specs={}
for sp in [ROOT/'data/juiced2/accepted-specs.jsonl']:
 for line in sp.read_text().splitlines():
  try:
   record=json.loads(line);specs[record['id']]=record
  except (ValueError,KeyError):pass
for c in doc['cars']:
 path=ROOT/'data/carmodels/profiles'/f"{c['code']}.txt";raw=path.read_bytes();s={}
 for line in raw.decode().splitlines():
  if '=' in line and not line.startswith('#'):
   k,v=line.split('=',1)
   try:s[k.strip()]=float(v.strip())
   except ValueError:pass
 layout=roster[c['code']]['profile_layout'];name=c['name'].lower()
 if 'r34' in name or 'integrale' in name:layout='AWD'
 if 'gnx' in name or 'elise' in name:layout='RWD'
 c['model_car_spec']=s;c['drive_layout']=layout;c['profile_source']={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'status':'existing research profile with documented priors/proxies; not native Juiced2 tune','accepted_match':roster[c['code']].get('match')}
 c['wheelbase_m']=s.get('body.wheelbase',c['wheelbase_m'])
 mass=sum(s.get('mass.'+k,0) for k in ['engine','gearbox','fuel','driver','chassis']);torques=[s.get(f'engine.torque_p{i}',0) for i in range(7)];idle=s.get('engine.idle_rpm',900);redline=s.get('engine.redline_rpm',7000);rpms=[idle+(redline-idle)*i/6 for i in range(7)];peak=max(range(7),key=lambda i:torques[i]);bhp=max(range(7),key=lambda i:torques[i]*rpms[i]);gears=[s[f'drive.gear{i}'] for i in range(1,9) if s.get(f'drive.gear{i}',0)>0]
 c['handling']=dict(mass=mass,wheelbase=c['wheelbase_m'],track_width=(s['body.track_front']+s['body.track_rear'])/2,wheel_radius=s['tire.rim_diameter_front']*.0254/2+s['tire.section_width_front']/1000*s['tire.aspect_front']/100,front_weight=.55,peak_torque=torques[peak],peak_torque_rpm=rpms[peak],peak_bhp=torques[bhp]*rpms[bhp]/7120.75586,peak_bhp_rpm=rpms[bhp],redline=redline,engine_size=s.get('engine.displacement',2)*1000,gears=gears,final_drive=s['drive.final'],layout=layout.title(),max_steer=s['steer.max_angle'],tyre_mu=(s['tire.lat_front.mu']+s['tire.lat_rear.mu'])/2,spring_rate=(s['susp.wheel_rate_front']+s['susp.wheel_rate_rear'])/2,damping_ratio=.6,drag=s['body.drag_coefficient'],abs=True,provenance='Adapted existing donor profile; equal-spaced torque RPM knots/front_weight/damping/ABS assumptions; original Juiced2 tune not asserted. '+str(path.relative_to(ROOT)))
 spec=specs.get(roster[c['code']].get('match',{}).get('sourceId'))
 if spec:
  h=c['handling'];values=spec.get('values',{});derived=spec.get('derived',{});bound={}
  for target,group,key,scale in [('mass',values,'curbWeightKg',1),('wheelbase',values,'wheelbaseMm',.001),('peak_torque',values,'torqueNm',1),('peak_torque_rpm',derived,'torqueRpm',1),('peak_bhp',derived,'powerBhp',1),('peak_bhp_rpm',derived,'powerRpm',1),('engine_size',values,'displacementCc',1)]:
   if isinstance(group.get(key),(int,float)) and group[key]>0:h[target]=group[key]*scale;bound[target]=key
  c['profile_source']['matched_spec']=dict(id=spec['id'],source_url=spec.get('sourceUrl'),bound_fields=bound,manufacturer_verified=spec.get('manufacturerVerified',False))
 c['handling']['front_weight']={'FWD':.6,'AWD':.55,'RWD':.5}[layout]
p.write_text(json.dumps(doc,indent=2)+'\n')
content_path=ROOT/'data/juiced2/content.json';content=json.loads(content_path.read_text());by={c['code']:c for c in doc['cars']}
for c in content['cars']:c['handling']=by[c['id']]['handling']
content_path.write_text(json.dumps(content,indent=2)+'\n');(ROOT/'godot/assets/game-content.json').write_text(json.dumps(content,separators=(',',':'))+'\n')
print('Bound',len(doc['cars']),'donor profiles')
