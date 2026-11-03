import bpy,math,sys,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for i,name in enumerate(['native_male_baggy_t','native_female_zip']):
 before=set(bpy.data.objects);base=ROOT/('artifacts/juiced2-build/characters/staged-actions/proof'if'--actions'in sys.argv else'artifacts/juiced2-build/characters/staged'if'--staged'in sys.argv else'godot/assets/characters');bpy.ops.import_scene.gltf(filepath=str(base/f'{name}.glb'));new=set(bpy.data.objects)-before
 for obj in new:
  if obj.parent is None:obj.location.x+=(-.85 if i==0 else .85)
bpy.ops.object.camera_add(location=(0,-5,1.1));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.4;bpy.context.scene.camera=cam
for pos,power,size in [((-3,-4,4),900,5),((3,-1,3),700,4),((0,3,3),700,3)]:
 bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.world.color=(.2,.2,.2);scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'artifacts/juiced2-build/characters/native-avatar-preview.png');bpy.ops.render.render(write_still=True)
if '--staged'in sys.argv or '--actions'in sys.argv:
 report=[]
 for frame in [0,90,180]:
  scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();bounds=[]
  for obj in bpy.data.objects:
   if obj.type!='MESH':continue
   ev=obj.evaluated_get(deps);mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];bounds.append(dict(name=obj.name,min=[min(v[i]for v in points)for i in range(3)],max=[max(v[i]for v in points)for i in range(3)]));ev.to_mesh_clear()
  report.append(dict(frame=frame,bounds=bounds));prefix='native-podium'if'--actions'in sys.argv else'native-idle';scene.render.filepath=str(ROOT/'artifacts/juiced2-build/characters'/f'{prefix}-frame-{frame}.png');bpy.ops.render.render(write_still=True)
 (ROOT/'artifacts/juiced2-build/characters'/(prefix+'-blender-proof.json')).write_text(json.dumps(report,indent=2)+'\n')
