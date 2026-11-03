"""Inspect original window-only surface PBR translations on actual donor meshes."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit/window-surfaces'
for code in ['GT4_HOND0019','GT4_TOYT0006','GT4_NISS0021','GT4_LNCA0005']:
 for mode,path in [('before',ROOT/'godot/assets/cars'/f'{code}.glb'),('staged',OUT/f'{code}.glb')]:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  for material in list(bpy.data.materials):
   if material.users==0:bpy.data.materials.remove(material)
  bpy.ops.import_scene.gltf(filepath=str(path))
  bpy.ops.object.camera_add(location=(3,7,2.5));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.7))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.4;bpy.context.scene.camera=camera
  for pos,power in [((3,4,5),1000),((-4,1,4),800)]:
   bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=5;light.rotation_euler=(Vector((0,0,.7))-light.location).to_track_quat('-Z','Y').to_euler()
  scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.world.color=(.18,.18,.18);scene.render.resolution_x=800;scene.render.resolution_y=520;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/f'{code}-{mode}.png');bpy.ops.render.render(write_still=True)
