"""Bind only source-proven accepted model/engine identities to native car tunes."""
import json,re
from pathlib import Path
from native_scripts import record_for_filename
ROOT=Path(__file__).resolve().parents[3];p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());matches={'FOCUS_SVT':('FOCUS_SVT','Accepted2002SVTFocus2.0L170BHP matches original native FocusSVT model/engine configuration.'),'GT4_DODG0005':('VIPER_SRT','AcceptedGT4ViperSRT10\'03 8.0L500BHP matches native VIPER_SRT, distinct from native older ViperGTS profile.')};reports=[]
for car in doc['cars']:
 h=car['handling'];h.update(body_length=car['length_m'],body_width=car['width_m'],body_height=car['model_car_spec']['body.height_overall'],inertia_scalar=1,max_steer=0.7799999713897705)
 car['native_common_controls']={'max_steer':0.7799999713897705,'source':'Original FRONT MaxSteerAngle common to all 93 filename-bound native physics profiles.','scope':'Shared recovered game control baseline; not a manufacturer specification or exact donor tune identity.'}
 if car['code']not in matches:continue
 tag,reason=matches[car['code']];record=record_for_filename('physics\\'+tag+'.txt');assert record;globals={};wheels={};section=None
 for row in record['fields']:
  if row[0]=='[BeginWheel]':section={}
  elif row[0]=='[End]':
   if section is not None:wheels[section['Location'][0]]=section;section=None
  elif section is not None:section[row[0]]=row[1:]
  else:globals[row[0]]=row[1:]
 front=wheels['FRONT'];rear=wheels['REAR']
 for target,key in [('mass','Mass'),('front_weight','FrontWeightDistribution'),('peak_torque','PeakTorque'),('peak_bhp','PeakBhp'),('redline','Redline'),('engine_size','EngineSize'),('final_drive','FinalDrive'),('clutch_time','ClutchTime')]:h[target]=globals[key][0]
 h['peak_torque_rpm']=globals['PeakTorque'][2];h['peak_bhp_rpm']=globals['PeakBhp'][2];h['gears']=globals['GearRatios'];h['layout']=next(k.title()for k in ['FWD','RWD','AWD']if k in globals);h['abs']='ABS'in globals
 for target,key in [('front_diff_slip','FrontDiffSlip'),('rear_diff_slip','RearDiffSlip'),('centre_diff_slip','CentreDiffSlip')]:h[target]=globals.get(key,[1])[0]
 for native,prefix in [(front,''),(rear,'rear_')]:
  for target,key in [('spring_rate','SpringRate'),('damping_ratio','DampingRatio'),('tyre_mu','TyreMu'),('max_spring_compression','MaxSpringCompression')]:h[prefix+target]=native[key][0]
  width,aspect,rim=map(float,re.fullmatch(r'(\d+)/(\d+)R(\d+)',native['TyreCode'][0]).groups());h[prefix+'wheel_radius']=width/1000*aspect/100+rim*.0254/2
 h['max_steer']=front['MaxSteerAngle'][0];h['footbrake_mu']=front['FootbrakeMu'][0];h['handbrake_mu']=rear['HandbrakeMu'][0];h['axle_mu']=rear['AxleMu'][0];h['provenance']='Exact original native game model/engine identity binding; PeakTorque retains original game units consumed by recovered engine/global TorqueScalar, not asserted SI Nm. Geometry dimensions/wheelbase/track/drag remain accepted donor physical adaptations.'
 evidence=dict(car=car['code'],native_tag=tag,match_reason=reason,source_filename=record['filename'],source_key=record['key'],source_member=record['index'],source_sha256=record['sha256'],native_rows=record['fields'],limits=['Nativegame-tuned values are preserved, not replaced by published manufacturer specifications.','TractionControl flag retained in raw rows; target enforcement requires matching recovered controller.','Body dimensions/wheelbase/track and drag remain adapted accepted donor geometry/profiles.']);car['native_physics']=evidence;reports.append(evidence)
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes())
by={c['code']:c for c in doc['cars']}
for p in [ROOT/'data/juiced2/content.json',ROOT/'godot/assets/game-content.json']:
 content=json.loads(p.read_text())
 for car in content['cars']:car['handling']=by[car['id']]['handling']
 p.write_text(json.dumps(content,indent=2)+'\n')
(ROOT/'data/juiced2/native-physics-bindings.json').write_text(json.dumps(reports,indent=2)+'\n');print('Bound2exactmodel/engine native profiles; acceptedbodyinertia dimensions30')
