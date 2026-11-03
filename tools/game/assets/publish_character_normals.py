"""Publish the reviewed normal/winding repair while preserving current metadata."""
import hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];SRC=ROOT/'artifacts/juiced2-build/characters';STAGE=SRC/'staged-components';DEST=ROOT/'godot/assets/characters/components';PROOF=SRC/'normal-proof'
checks=json.loads((PROOF/'numerical.json').read_text());assert checks['summary']['components']==111
assert all(checks['summary'][key]is True for key in ['geometry_rig_uv_weights_position_targets_preserved','triangle_winding_only_reversed','all_native_normal_targets_exact'])
assert all(item['geometry_and_rig_unchanged']is True and item['only_triangle_winding_reversed']is True for item in checks['components'])
imported=json.loads((STAGE/'blender-import-proof.json').read_text());assert imported['summary']['imported']==111 and imported['summary']['all_bones86']is True and imported['summary']['head_presets_checked']==2
manifest_path=ROOT/'godot/assets/characters/components.json';old=manifest_path.read_bytes();manifest=json.loads(old);by={s['id']:s for s in manifest['skins']};backup=PROOF/'previous-bundle';backup.mkdir(exist_ok=True)
assert len(by)==111
for item in checks['components']:
 path=DEST/(item['id']+'.glb');staged=STAGE/path.name
 assert hashlib.sha256(path.read_bytes()).hexdigest()==item['old_sha256']
 assert hashlib.sha256(staged.read_bytes()).hexdigest()==item['new_sha256']
 shutil.copyfile(path,backup/path.name)
(backup/'components.json').write_bytes(old)
for item in checks['components']:
 shutil.copyfile(STAGE/(item['id']+'.glb'),DEST/(item['id']+'.glb'))
 by[item['id']]['sha256']=item['new_sha256']
 by[item['id']]['native_normal_binding']=dict(source_float3_offset=32,source_vertex_stride='68or76peroriginalchunk',winding='OriginalCWindicesretained;sourceY/ZreflectionconvertsorientationtoCCW',morphs='OriginalsparseNORMALdeltas100×;existing0.01×nativelevelweightsunchanged',proof='artifacts/juiced2-build/characters/native-normal-winding-audit.json')
manifest['limits']=[limit.replace('garment materials and normals remain explicit adaptations.','garment materials remain explicit adaptations; original normals and winding are retained.')for limit in manifest.get('limits',[])]
manifest['normal_contract']='Originalfloat3unitnormals,sourceindexorderand100sparseheadNORMALtargets;novertexweldingorrecomputedsmoothing. NativeGPUacceptanceofthisbatchseparate.'
encoded=json.dumps(manifest,indent=2,allow_nan=False)+'\n';manifest_path.write_text(encoded);(ROOT/'data/juiced2/native-avatar-components.json').write_text(encoded)
report=dict(previous_manifest_sha256=hashlib.sha256(old).hexdigest(),manifest_sha256=hashlib.sha256(encoded.encode()).hexdigest(),components=checks['components'],backup=str(backup.relative_to(ROOT)),limits=['Source/Blender/numericalverificationcomplete;nativeGodotproofpending.'])
(PROOF/'published.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Published111source-normal/windingrepairs;manifestSHA',report['manifest_sha256'])
