"""Inspect recovered Paintshop geometry with explicitly authored preview lighting."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/presentation/paintbooth-stage';meta=json.loads((OUT/'venue.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(OUT/'paintbooth.glb'))
# glTF(Yup) to Blender(Zup): [x,y,z] -> [x,-z,y].
def point(v):return Vector((v[0],-v[2],v[1]))
base=meta['donor_display']['position_rh_m'];before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'godot/assets/cars/GT4_HOND0018.glb'))
for obj in set(bpy.data.objects)-before:
 if obj.parent is None:obj.location+=point(base);obj.rotation_euler.z+=math.pi/2
for image in bpy.data.images:image.alpha_mode='CHANNEL_PACKED'
camera_pos=[-30,-.2,32.8];target=[-30,-.65,29.5];bpy.ops.object.camera_add(location=point(camera_pos));camera=bpy.context.object;camera.rotation_euler=(point(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='PERSP';camera.data.angle=math.radians(110);bpy.context.scene.camera=camera
for position,power,size in [([-30,1.2,30],350,4),([-33,.7,30],200,3),([-27,.7,30],200,3)]:
 bpy.ops.object.light_add(type='AREA',location=point(position));light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(point([-30,-1,30])-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.world.color=(.08,.08,.08);scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'source-room-preview.png');bpy.ops.render.render(write_still=True)
(OUT/'preview-proof.json').write_text(json.dumps(dict(source_glb=meta['sha256'],camera_rh=camera_pos,target_rh=target,display_ground=base,limits=['Inspection camera/lighting are authored for geometry review, not native projection/DLT parity.','Accepted donor car is displayed only for scale proof; source car geometry remains unchanged.']),indent=2)+'\n')
