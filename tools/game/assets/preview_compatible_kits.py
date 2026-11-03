"""Render source wing/seat mounting checks against each accepted donor body."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];kits=json.loads((ROOT/'godot/assets/kits.json').read_text())['kits'];out=ROOT/'artifacts/juiced2-build/kits/fit-captures';out.mkdir(exist_ok=True)
filters=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]
for car in sorted({k['compatible_cars'][0]for k in kits}):
 if filters and car not in filters:continue
 for category in ['spoiler','seats']:
  choice=next((k for k in kits if car in k['compatible_cars']and k['category']==category),None)
  if not choice:continue
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  for path in ['cars/'+car+'.glb',choice['model_path'].replace('res://assets/','')]:
   before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'godot/assets'/path))
   if category=='seats'and path.startswith('cars/'):
    for obj in set(bpy.data.objects)-before:
     if obj.type=='MESH'and not any(x in obj.name.lower()for x in ['wheel','tire','whl','rim']):m=obj.modifiers.new('Fit inspection wireframe','WIREFRAME');m.thickness=.003
  bpy.ops.object.camera_add(location=(5,-7,3));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.7))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=6;bpy.context.scene.camera=camera
  for pos,power in [((3,-4,5),1500),((-4,-1,4),1000),((0,5,3),1200)]:
   bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.size=5;l.rotation_euler=(Vector((0,0,.7))-l.location).to_track_quat('-Z','Y').to_euler()
  s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.world.color=(.18,.18,.18);s.render.resolution_x=900;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(out/(car+'-'+category+'.png'));bpy.ops.render.render(write_still=True)
