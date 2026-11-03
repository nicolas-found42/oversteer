"""Bounded original goal-label filename-hash probe; evidence only."""
import itertools,json
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3]
by={r['key']:r for r in json.loads((ROOT/'godot/assets/ui/native/manifest.json').read_text())}
kinds=['PlaceInRace','WinRace','WinDriverBet','BeatDriver','DriftPoints','AirTime','TrashCar','SpeedBarrier','CloseFinish','VictoryMargin','ClassQual','ClassQualifier','PerfectLap','LapTime','WinRaceBet','PinkSlip','WinPinkSlip','Bet','Money','Car','Prototype','ExtremeNOS']
disciplines=['Circuit','Drift','Any','TeamRace','DriftKing','DriftObliterator','DriftEnduro','LastManStanding','Eliminator','SoloDrift','TwinDrift','Tournament','Championship']
labels=set()
for a,b in itertools.product(kinds,disciplines):labels.update([f'GoalIcons_{a}_{b}',f'GoalIcons_{b}_{a}'])
rows=[]
for label in sorted(labels):
 path='Textures\\'+label+'.ddt';key=f'{filename_hash(path):08x}'
 if key in by:rows.append(dict(label=label,native_path=path,key=key,texture=by[key]))
(ROOT/'artifacts/juiced2-build/ui/goal-icon-bindings.json').write_text(json.dumps(dict(candidate_count=len(labels),matched=rows),indent=2)+'\n')
print(len(rows),'exact named source textures from',len(labels),'bounded candidates; runtime unchanged')

# Source-backed native builder string fragments (82220250, .rdata literals).
rdata=(ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin').read_bytes()
offsets=[16180,16188,16200,16212,16224,16236,16248,16260,16280,16296,16312,16328,16344,16356,16368,16380,16396,16412,16424,16440,16456,16468,16484,16496,16512,16524,16536,6856,6868,6880,6908,6920]
fragments=[]
for offset in offsets:
 i=0x82040000+offset-0x82000400;fragments.append(rdata[i:rdata.index(0,i)].decode())
matched=[]
for a,b in itertools.product(fragments,fragments):
 label='GoalIcons'+a+b;key=f'{filename_hash("Textures"+chr(92)+label+".ddt"):08x}'
 if key in by:matched.append(dict(label=label,key=key,path=by[key]['path']))
(ROOT/'artifacts/juiced2-build/ui/native-goal-icon-matches.json').write_text(json.dumps(dict(native_consumer='82220250',suffixes=fragments,matched=matched),indent=2)+'\n')
print(len(matched),'exact source-builder goal icon textures; runtime unchanged')
