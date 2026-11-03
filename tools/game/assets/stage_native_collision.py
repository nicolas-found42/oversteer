"""Export exact native CLD controls in current track-local Godot coordinates."""
import json,hashlib
from pathlib import Path
from native_collision import parse
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/collision';OUT=SOURCE/'track-local';OUT.mkdir(exist_ok=True);reports=[];inventory=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());source_files={r['path'].lower():r for r in inventory['files']}
for track in json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks']:
 name=str(Path(track['source']['path']).with_suffix('.cld'));path=SOURCE/name.replace('/','--')
 if not path.exists():
  row=source_files[name.lower()]
  with open(inventory['iso'],'rb')as iso:iso.seek(row['offset']);raw=iso.read(row['size']);assert len(raw)==row['size'];path.write_bytes(raw)
 raw=path.read_bytes();native=parse(raw);origin=[v/100 for v in track['source']['origin_source_units']]
 points=[[-p[0]/100-origin[0],p[1]/100-origin[1],p[2]/100-origin[2]]for p in native['points']]
 triangles=[dict(indices=[r['indices'][0],r['indices'][2],r['indices'][1]],normal=[-r['normal'][0],r['normal'][1],r['normal'][2]],surface_id=r['surface_id'])for r in native['triangles']]
 polygons=[dict(indices=list(reversed(r['indices'])),surface_id=r['surface_id'])for r in native['polygons']]
 patches=[dict(indices=r['metadata'][:16],subdivisions=r['metadata'][16:18],native_tail=r['metadata'][18],surface_id=r['surface_id'])for r in native['patches']]
 for patch in patches:assert len(patch['indices'])==16 and max(patch['indices'])<len(points)
 splines=[dict(indices=r['indices'],surface_id=r['surface_id'],native_planes=r['planes'],native_bounds=r['bounds'])for r in native['splines']]
 doc=dict(track_id=track['id'],coordinate_system='godot-rh-reflect-x; metres; current track-local origin',points=points,point_native_flags=[p[3]for p in native['points']],triangles=triangles,polygons=polygons,patches=patches,splines=splines,spline_rule=dict(top_offset_m=4.0,row_step_m=-1.6666667175292969,native_consumer='8226F810',top_offset_source_address='824AF4C0',row_step_source_address='8204D198',control_order='Four source controls in each of four vertical rows, top-to-bottom; then native bicubic Bernstein evaluation.'),source=dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),native_loader='82270218',native_patch_evaluator='8230AAA0',origin_source_units=track['source']['origin_source_units'],parsed_offset=native['parsed_offset'],spatial_hierarchy_remaining_bytes=native['trailing_bytes']),limits=['Exact original collision primitives/control indices and low7-bit surface IDs retained without shader or orientation exclusion.','The compatibility field subdivisions retains raw serialized metadata16/17; its mapping to native grid resolution is unproven. Native optional cached grids come from separate BCP text overrides; remaining native contacts use continuous bicubic queries.','Cubic Bernstein patch basis and control ordering source-proven; discrete tessellation remains an approximation to native iterative patch intersection.','Spline top/row offsets are original default game data/constant values; surface property physical values remain unresolved.','Raw spline planes/bounds retain original native coordinates and unknown broadphase semantics; they are not presented as transformed track-local planes.'])
 (OUT/(track['id']+'.json')).write_text(json.dumps(doc,separators=(',',':'),allow_nan=False)+'\n');reports.append(dict(id=track['id'],counts={k:len(doc[k])for k in ['points','triangles','polygons','patches','splines']},source=doc['source']))
(OUT/'manifest.json').write_text(json.dumps(reports,indent=2)+'\n');print('Staged',len(reports),'exact native track-local collision control catalogs; runtime unchanged')
