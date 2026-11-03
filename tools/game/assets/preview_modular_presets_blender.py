"""Render two source preset assemblies with original replacement albedos.

Original HSV/overlay/skeletal-scale execution is intentionally not claimed.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters/staged-components';manifest=json.loads((OUT/'components.json').read_text());components={c['id']:c for c in manifest['components']};skins={s['id']:s for s in manifest['skins']};images={r['name'].lower():ROOT/r['path'] for r in json.loads((ROOT/'artifacts/juiced2-build/characters/avatar-materials.json').read_text())['textures']};bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);reports=[]
for pi,gender in enumerate(['M','F']):
 preset=next(p for p in manifest['native_presets']['presets']if p['gender']==gender and p['gender_order']==0);selected=[components[c['component_id']]for c in preset['components']];replacements={row[1].lower():row[2]for c in selected for row in c['native_rows']if row[0]=='texture'and len(row)>=3};seen=set();parts=[]
 for c in selected:
  if not c['native_initial_mesh_enabled']:continue
  for ident in c['skin_ids']:
   skin=skins[ident]
   if skin['gender_tag']!=gender or ident in seen:continue
   seen.add(ident);before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(OUT/(ident+'.glb')));new=set(bpy.data.objects)-before
   for obj in new:
    if obj.parent is None:obj.location.x+=(-.65 if pi==0 else .65)
   meshes=[o for o in new if o.type=='MESH'and any(m.type=='ARMATURE'for m in o.modifiers)]
   for mesh in meshes:
    for slot in skin['materials']:
     base=Path(slot['native_jtd']).stem;target=base
     for _ in range(8):
      updated=replacements.get(target.lower(),target)
      if updated==target:break
      target=updated
     material=next((m for m in mesh.data.materials if m and (m.name==slot['name']or m.name.startswith(slot['name']+'.'))),None)
     if target.lower()in images and material and material.use_nodes:
      tex=next((n for n in material.node_tree.nodes if n.type=='TEX_IMAGE'),None)
      if tex:tex.image=bpy.data.images.load(str(images[target.lower()]),check_existing=True)
    if skin['morph_attributes']:
     keys=mesh.data.shape_keys.key_blocks
     for attribute in skin['morph_attributes']:
      key=next(k for k in keys if k.name.lower()==attribute['name'].lower());key.slider_min=-10;key.slider_max=10;key.value=preset['native_attributes'][attribute['name']]*attribute['native_level_to_render_weight']
   parts.append(dict(component=c['id'],skin=ident))
 reports.append(dict(preset=preset['id'],parts=parts,unapplied_native_attributes={k:v for k,v in preset['native_attributes'].items()if k.startswith(('SKELETON_','SKIN_','HAIR_','PROFILE_'))}))
bpy.ops.object.camera_add(location=(0,-5,1.12));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.95))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=2.9;bpy.context.scene.camera=camera
for position,power,size in [((-3,-4,4),700,5),((3,-1,3),500,4),((0,3,3),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=position);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
for image in bpy.data.images:image.alpha_mode='CHANNEL_PACKED'
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.world.color=(.15,.15,.15);scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'source-preset-albedos.png');bpy.ops.render.render(write_still=True)
(OUT/'source-preset-assembly-proof.json').write_text(json.dumps(dict(presets=reports,limits=['Source albedo replacements and45 geometric head levels applied; native11 other attributes/HSV/facial overlay/cloth shader execution not claimed.','Static bind pose proof; native runtime animation/attachment checks remain separate.']),indent=2)+'\n')
