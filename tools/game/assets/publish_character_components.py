"""Publish a fully imported, reviewed modular-avatar stage in one asset batch."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters/staged-components';manifest=json.loads((SOURCE/'components.json').read_text());proof=json.loads((SOURCE/'blender-import-proof.json').read_text());assembly=json.loads((SOURCE/'source-preset-assembly-proof.json').read_text());assert proof['summary']['imported']==len(manifest['skins'])==111;assert sum(r['mesh_chunks']for r in proof['skins'])==sum(len(r['mesh_nodes'])for r in manifest['skins']);assert proof['summary']['head_presets_checked']==2 and len(assembly['presets'])==2
for skin in manifest['skins']:
 assert hashlib.sha256((ROOT/skin['source']['path']).read_bytes()).hexdigest()==skin['source']['sha256'];assert hashlib.sha256((SOURCE/(skin['id']+'.glb')).read_bytes()).hexdigest()==skin['sha256'];assert skin['bone_count']==86 and skin['weight_sum_max_error']<1e-5
assert len(manifest['native_presets']['presets'])==10 and all(len(p['native_attributes'])==56 and all(c['component_id']for c in p['components'])for p in manifest['native_presets']['presets'])
DEST=ROOT/'godot/assets/characters/components';DEST.mkdir(exist_ok=True);(DEST/'textures').mkdir(exist_ok=True)
for skin in manifest['skins']:shutil.copyfile(SOURCE/(skin['id']+'.glb'),DEST/(skin['id']+'.glb'))
for path in (SOURCE/'textures').glob('*.png'):shutil.copyfile(path,DEST/'textures'/path.name)
# The metadata keeps source and translated/unresolved behavior distinct.
manifest['publication_status']='Published original geometry/rig/albedos with explicit PBR adaptations; native Godot attachment and source HSV/skeletal-scale execution require separate runtime checks.'
manifest['limits']=[limit for limit in manifest['limits'] if limit!='Source-only staging; no runtime publication.']+['Blender source import and static assembly were verified; native Godot modular attachment has not yet been verified.']
encoded=json.dumps(manifest,indent=2,allow_nan=False)+'\n';(ROOT/'godot/assets/characters/components.json').write_text(encoded);(ROOT/'data/juiced2/native-avatar-components.json').write_text(encoded)
for filename,payload in [('native-avatar-presets.json',manifest['native_presets']),('native-avatar-controls.json',manifest['creator_controls'])]:(ROOT/'data/juiced2'/filename).write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
report=dict(skins=len(manifest['skins']),source_mesh_chunks=sum(len(s['mesh_nodes'])for s in manifest['skins']),textures=len(list((SOURCE/'textures').glob('*.png'))),presets=10,native_attributes_per_preset=56,manifest_sha256=hashlib.sha256(encoded.encode()).hexdigest(),limits=manifest['limits']);(SOURCE/'published.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
