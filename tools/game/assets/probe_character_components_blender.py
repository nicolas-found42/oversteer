"""Import every staged source component and measure original preset head motion."""
import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters/staged-components';manifest=json.loads((OUT/'components.json').read_text());reports=[]
for skin in manifest['skins']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for blocks in [bpy.data.meshes,bpy.data.armatures,bpy.data.materials,bpy.data.images]:
  for block in list(blocks):
   if block.users==0:blocks.remove(block)
 bpy.ops.import_scene.gltf(filepath=str(OUT/(skin['id']+'.glb')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)];rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(meshes)==len(skin['mesh_nodes']) and len(rigs)==1 and len(rigs[0].data.bones)>=86
 assert all(any(m.type=='ARMATURE'and m.object==rigs[0]for m in mesh.modifiers)for mesh in meshes);assert sum(len(mesh.data.vertices)for mesh in meshes)==skin['used_vertices'];assert all(math.isfinite(x)for mesh in meshes for v in mesh.data.vertices for x in v.co);mesh=meshes[0]
 report=dict(id=skin['id'],bones=len(rigs[0].data.bones),mesh_chunks=len(meshes),vertices=sum(len(mesh.data.vertices)for mesh in meshes),triangles=sum(len(p.vertices)-2 for mesh in meshes for p in mesh.data.polygons),materials=sum(len(mesh.data.materials)for mesh in meshes),morph_targets=len(mesh.data.shape_keys.key_blocks)-1 if mesh.data.shape_keys else 0)
 if skin['morph_attributes']:
  assert report['morph_targets']==100;keys=mesh.data.shape_keys.key_blocks;neutral=[v.co.copy()for v in mesh.data.vertices];preset=next(p for p in manifest['native_presets']['presets']if p['native_gender']==skin['rig'].upper()and p['gender_order']==0)
  for attribute in skin['morph_attributes']:
   key=next(k for k in keys if k.name.lower()==attribute['name'].lower());key.slider_min=-10;key.slider_max=10;key.value=preset['morph_levels'][attribute['name']]*attribute['native_level_to_render_weight']
  bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps);data=evaluated.to_mesh();assert all(math.isfinite(x)for v in data.vertices for x in v.co);report['preset_id']=preset['id'];report['preset_head_bounds']={k:[f(v.co[i]for v in data.vertices)for i in range(3)]for k,f in [('min',min),('max',max)]};report['preset_position_delta_max_m']=max((v.co-neutral[i]).length for i,v in enumerate(data.vertices));assert 0<report['preset_position_delta_max_m']<.5;evaluated.to_mesh_clear()
 reports.append(report);print('PROBE',skin['id'],report['vertices'],report['morph_targets'],flush=True)
(OUT/'blender-import-proof.json').write_text(json.dumps(dict(skins=reports,summary=dict(imported=len(reports),all_bones86=True,head_presets_checked=sum('preset_id'in r for r in reports)),limits=['Blender import/bind/head-deformation check; native Godot renderer and original shader/HSV/skeletal-scale fidelity are separate checks.']),indent=2)+'\n')
