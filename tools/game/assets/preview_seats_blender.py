"""Render original source accessories fitted to the accepted donor base."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
import json
paths=['cars/GT4_NISS0004.glb','kits/350z-native-seats.glb']
for p in paths:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'godot/assets'/p))
 if p.startswith('cars/'):
  for obj in set(bpy.data.objects)-before:
   if obj.type=='MESH'and obj.name=='body':
    modifier=obj.modifiers.new('Donor cabin fit wireframe','WIREFRAME');modifier.thickness=.003
bpy.ops.object.camera_add(location=(5,-7,3));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6;bpy.context.scene.camera=cam
for position,power in [((3,-4,5),1500),((-4,-1,4),1000),((0,5,3),1200)]:
 bpy.ops.object.light_add(type='AREA',location=position);light=bpy.context.object;light.data.energy=power;light.data.size=5;light.rotation_euler=(Vector((0,0,.7))-light.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.world.color=(.18,.18,.18);s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(ROOT/'artifacts/juiced2-build/kits/350z-seat-fit.png');bpy.ops.render.render(write_still=True)
