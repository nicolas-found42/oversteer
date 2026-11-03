"""Translate original goal icon builder 82220250 for the retained career goals."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/ui'
art=json.loads((SOURCE/'native-goal-icon-matches.json').read_text());by={r['label']:r for r in art['matched']};content=json.loads((ROOT/'data/juiced2/content.json').read_text());rows=[]
for league in content['leagues']:
 for goal in league['goals']:
  kind=goal['kind'].lower();discipline=goal['discipline'];subtype=goal['subtype'];contest=goal['contest_type'];suffix={'Championship':'Champ','Tournament':'Tourn'}.get(contest,'')
  prefix={'windriverbet':'DriverBet','winspectatorbet':'SpecBet','beatcar':'BeatCar','beatdriver':'BeatDriver','victorymargin':'VictoryMargin','closefinish':'VictoryMargin','speedbarrier':'SpeedBarrier','airtime':'AirTime','driftpoints':'DriftPoints','trashcar':'TrashACar','trashallcars':'TrashAllCar'}.get(kind)
  if kind in ['winrace','placeinrace']:
   if discipline=='Circuit':prefix=('LMS'+suffix if subtype=='LMS'else'Eliminator'+('Champ'if contest=='Championship'else'')if subtype=='Eliminator'else'Circuit'+suffix)
   elif discipline=='Drift':prefix=('DriftKing'+suffix if subtype=='DriftKing'else'TwinDrift'if subtype=='TwinDrift'else'SoloDrift'if subtype=='SoloDrift'else'DriftRace'+suffix)
  if goal['prize_type']=='Pinks':prefix='PinkSlip'
  if goal['qualifier']:context='ClassQual'
  elif kind in ['windriverbet','winspectatorbet']:context='Betting'
  else:context={'Circuit':'Circuit','Drift':'Drift'}.get(discipline,'Misc')
  label='GoalIcons_'+str(prefix)+'_'+context
  match=by.get(label)
  rows.append(dict(goal_id=goal['id'],league=league['league'],kind=goal['kind'],native_label=label,texture_path=match['path']if match else None,source_consumer='82220250'))
report=dict(source_consumer='82220250',native_goal_enum_table='824AF8EC..824AF91C',goals=rows,unresolved=[r for r in rows if r['texture_path']is None],limits=['Exact source builder string/context translation; underlying PBR/UI texture decoding remains separately verified.'])
(SOURCE/'native-goal-icon-map.json').write_text(json.dumps(report,indent=2)+'\n');print(len(rows),'goals;',len(report['unresolved']),'unresolved')
