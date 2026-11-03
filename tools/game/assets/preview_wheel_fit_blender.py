"""Compare actual rim/tire occlusion before and after source face alignment."""
import bpy,json,struct,math
from pathlib import Path
from mathutils import Matrix,Quaternion,Vector
ROOT=Path(__file__).resolve().parents[3];catalog=json.loads((ROOT/'data/juiced2/cars.json').read_text())['cars'];measured=json.loads((ROOT/'artifacts/juiced2-build/wheel-replacement-fit.json').read_text())['cars'];out=ROOT/'artifacts/juiced2-build/wheel-fit';out.mkdir(exist_ok=True);CB=Matrix.Rotation(math.pi/2,4,'X')
def array_matrix(values):return Matrix([values[i:i+4]for i in range(0,16,4)]).transposed()
def load(path,world=None):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.data.objects)-before
 if world is not None:
  for obj in new:
   if obj.parent is None:obj.matrix_world=CB@world@CB.inverted()@obj.matrix_world
 return new
for code in ['GT4_MITS0001','FOCUS_SVT']:
 car=next(c for c in catalog if c['code']==code);draft=next(c for c in measured if c['code']==code);raw=(ROOT/'godot/assets/cars'/f'{code}.glb').read_bytes();d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);world={};named={}
 def visit(i,parent):
  n=d['nodes'][i]
  if 'matrix'in n:m=array_matrix(n['matrix'])
  else:
   q=n.get('rotation',[0,0,0,1]);m=Matrix.Translation(Vector(n.get('translation',[0,0,0])))@Quaternion((q[3],q[0],q[1],q[2])).to_matrix().to_4x4()@Matrix.Diagonal([*n.get('scale',[1,1,1]),1])
  world[i]=parent@m;named[n.get('name','')]=i
  for c in n.get('children',[]):visit(c,world[i])
 for i in d['scenes'][0]['nodes']:visit(i,Matrix.Identity(4))
 for mode in ['before','after']:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);load(ROOT/'godot/assets/cars'/f'{code}.glb')
  for socket in car['wheel_sockets']:
   obj=bpy.data.objects.get(socket['node']);assert obj,socket['node']
   for child in [obj,*obj.children_recursive]:child.hide_render=True
   W=world[named[socket['node']]];native=next(s for s in draft['sockets']if s['node']==socket['node']);scale=W.to_scale()
   T=array_matrix(native['replacement_transforms']['mesh'])if mode=='after'else Matrix.Diagonal([socket['radius']/abs(v)for v in scale]+[1]);load(ROOT/'godot/assets/wheels/mesh.glb',W@T)
   if socket.get('tire_embedded'):
    TT=array_matrix(native['replacement_tire_transform'])if mode=='after'else Matrix.Diagonal([socket['outer_radius']/abs(v)for v in scale]+[1]);load(ROOT/'godot/assets/wheels/shared-tire.glb',W@TT)
  bpy.ops.object.camera_add(location=(5,7,2.5));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.65))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.5;bpy.context.scene.camera=camera
  for pos,power in [((3,4,5),1500),((-4,1,4),1000),((0,-5,3),1200)]:
   bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=5;light.rotation_euler=(Vector((0,0,.7))-light.location).to_track_quat('-Z','Y').to_euler()
  scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.world.color=(.18,.18,.18);scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/(code+'-'+mode+'.png'));bpy.ops.render.render(write_still=True)
