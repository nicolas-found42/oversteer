"""Render bounded current/staged head comparison under identical neutral light."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters/normal-proof';OUT.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'godot/assets/characters/components.json').read_text())
for gender,preset_id in [('male','MPreset1'),('female','FMPreset1')]:
 skin=next(s for s in manifest['skins']if s['id']=='cc0ee14d_'+gender);preset=next(p for p in manifest['native_presets']['presets']if p['id']==preset_id)
 for state,base in [('current','godot/assets/characters/components'),('staged','artifacts/juiced2-build/characters/staged-components')]:
  for morph in ['neutral',preset_id]:
   bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
   for blocks in [bpy.data.meshes,bpy.data.armatures,bpy.data.materials,bpy.data.images]:
    for block in list(blocks):
     if block.users==0:blocks.remove(block)
   bpy.ops.import_scene.gltf(filepath=str(ROOT/base/('cc0ee14d_'+gender+'.glb')))
   objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE'for m in o.modifiers)]
   for obj in bpy.context.scene.objects:
    if obj.type=='MESH'and obj not in objects:obj.hide_render=True
   if morph!='neutral':
    for obj in objects:
     if obj.data.shape_keys is None:continue
     for attribute in skin['morph_attributes']:
      key=obj.data.shape_keys.key_blocks[attribute['target_index']+1];key.slider_min=-10;key.slider_max=10;key.value=preset['native_attributes'][attribute['name']]*.01
      assert abs(key.value-preset['native_attributes'][attribute['name']]*.01)<1e-5
   mat=bpy.data.materials.new('neutral_debug');mat.diffuse_color=(.45,.45,.45,1);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.45,.45,.45,1);shader.inputs['Roughness'].default_value=.7
   for obj in objects:
    for i in range(len(obj.data.materials)):obj.data.materials[i]=mat
   bpy.context.view_layer.update();coords=[obj.matrix_world@v.co for obj in objects for v in obj.data.vertices];center=sum(coords,Vector())/len(coords)
   scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
   world=bpy.data.worlds.new('neutral_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.3,.3,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;scene.world=world
   bpy.ops.object.camera_add(location=(center.x,center.y-.65,center.z));camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=65;scene.camera=camera
   bpy.ops.object.light_add(type='AREA',location=(center.x-.5,center.y-.5,center.z+.4));light=bpy.context.object;light.data.energy=30;light.data.shape='DISK';light.data.size=.5;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
   scene.view_settings.view_transform='Standard';scene.render.filepath=str(OUT/f'{gender}-{state}-{morph}.png');bpy.ops.render.render(write_still=True)
   print('PROOF',state,morph,flush=True)
