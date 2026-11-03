"""Export bounded original ColourChart controls and exact texture bindings."""
import hashlib,json
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/ui';path=SOURCE/'layout-fields/ui-17099544.json';doc=json.loads(path.read_text());rows=doc['fields'];images=json.loads((ROOT/'godot/assets/ui/native/manifest.json').read_text());by={}
for image in images:by.setdefault(image['key'],[]).append(image)
controls=[];globals=[];current=None
for index,row in enumerate(rows):
 if row[0]in['BeginBox','BeginText','BeginSlider','BeginColourChart']:
  current=dict(kind=row[0][5:],name=row[1],rect_normalized=row[2:6],source_row=index,native_rows=[]);controls.append(current)
 elif current is not None and row[0]in['EndBox','EndText','EndSlider','EndColourChart']:current=None
 elif current is not None:current['native_rows'].append(row)
 elif row[0]in['GADGETPOS','GADGETCOL','GADGETICON','UBERBOXPOS','UBERBOXORIGIN','Prompt']:globals.append(row)
for control in controls:
 control['textures']=[]
 for row in control['native_rows']:
  if row[0]!='Texture':continue
  label=row[1];key=f'{filename_hash("Textures"+chr(92)+label+".ddt"):08x}';control['textures'].append(dict(native_label=label,key=key,paths=[r['path']for r in by.get(key,[])]))
report=dict(source=dict(path=str(path.relative_to(ROOT)),key=doc['key'],member=doc['source_member'],sha256=hashlib.sha256(path.read_bytes()).hexdigest()),globals=globals,controls=controls,limits=['Exact original typed UI rows; dynamic per-mode hiding/visibility and generic gadget wheel/ring diameter require consumer proof.','Prompt0/1 IDs retained without inventing platform glyph bindings.'])
report['localization_candidates']=[]
for table in json.loads((SOURCE/'localization.json').read_text()):
 entries={int(row['id']):row['text'].rstrip('\r\n') for row in table['entries']}
 if set(entries)!={0,1,68,72,74,75,76,78}:continue
 source_path=ROOT/table['path'];report['localization_candidates'].append(dict(bank=table['bank'],key=table['key'],member=table['member'],path=table['path'],sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),entries=entries))
report['limits'].append('Localization candidates have the exact eight local caption/prompt IDs; original filename/bank-loader binding and runtime per-mode caption replacement remain unverified.')
report['prompt_art']=[]
for label in ['BUT_SELECT','BUT_BACK','BUT_SELECT2','BUT_SELECT3','BUT_SELECT_LB','BUT_SELECT_RB']:
 key=f'{filename_hash('Textures'+chr(92)+label+'.ddt'):08x}';report['prompt_art'].append(dict(native_label=label,key=key,paths=[r['path']for r in by.get(key,[])]))
(SOURCE/'native-palette-layout.json').write_text(json.dumps(report,indent=2)+'\n');print(len(controls),'original bounded controls; runtime unchanged')
