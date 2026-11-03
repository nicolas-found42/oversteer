"""Stage exact per-course auxiliary file provenance, without changing query geometry."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/collision/auxiliary';doc=json.loads((SOURCE/'manifest.json').read_text());tracks=json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks'];normalize=lambda value:re.sub('[^a-z0-9]','',value.lower());banks={normalize(Path(b['bank']).stem):b for b in doc['banks']};types=['TARMAC_DRY','SAND_DRY','GRASS_DRY','TARMAC_WET','SAND_WET','GRASS_WET','CONCRETE','METAL','WOOD','GLASS','SNOW','ICE','COBBLE','THRUM'];rows=[]
for track in tracks:
 bank=banks[normalize(Path(track['source']['path']).parts[1])];properties=next((m for m in bank['members']if m['kind']=='surface_properties'),None);bcp=next((m for m in bank['members']if m['kind']=='bcp'and m['filename'].lower()==Path(track['source']['path']).stem.lower()+'.bcp'),None);groups=[];current=None
 if properties:
  for line in properties['text'].splitlines():
   fields=line.split()
   if not fields:continue
   if fields[0]=='[BeginSurfaceProperties]':current=dict(group_index=len(groups),materials=[]);groups.append(current)
   elif fields[0]=='[End]':current=None
   elif current is not None:
    if fields[0]=='Materials':current['materials']=fields[1:]
    elif fields[0]=='Type':current['surface_type']=fields[1];current['surface_type_enum']=types.index(fields[1])
    else:current[fields[0]]=float(fields[1])
 overrides=[]
 if bcp:
  for line in bcp['text'].splitlines():
   fields=line.split()
   if not fields:continue
   assert len(fields)==3;index,u,v=map(int,fields);overrides.append(dict(patch_index=index,u_steps=max(1,u),v_steps=max(1,v),native_values=[index,u,v]))
 rows.append(dict(track_id=track['id'],bank=bank['bank'],surface_properties=dict(source={k:properties[k]for k in['filename','key','member','path','sha256']},groups=groups)if properties else None,bcp=dict(source={k:bcp[k]for k in['filename','key','member','path','sha256']},overrides=overrides)if bcp else None,limits=['Raw CLD surface group index is separate from native SurfaceType enum.','Contact-material combination remains unresolved; these original friction/restitution values are not silently substituted for tyre coefficients.','Missing bank-local property/BCP files are retained as absent; no inherited file binding is guessed.']))
(SOURCE/'track-bindings.json').write_text(json.dumps(dict(surface_type_enum_table='824AF488',native_bcp_loader='82270218 -> 8226FE58',tracks=rows),indent=2)+'\n');print('Staged33source auxiliary bindings; runtime unchanged')
