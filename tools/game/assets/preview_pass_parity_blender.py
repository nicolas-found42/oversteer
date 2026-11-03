"""Render staged/source GT4 pass parity with explicit back-face transparency."""
import bpy,sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit'
if args:OUT=OUT/args.pop(0)
for code in args or ['GT4_HOND0019','GT4_MAZD0012','GT4_BMW_0010']:
 for mode in ['before','staged']:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  path=(ROOT/'godot/assets/cars'if mode=='before'else OUT)/(code+'.glb')
  bpy.ops.import_scene.gltf(filepath=str(path))
  # Cycles does not apply material back-face culling itself. Mirror the glTF
  # single-sided rule explicitly so this comparison tests that exact change.
  for material in bpy.data.materials:
   if not material.use_nodes or not material.use_backface_culling:continue
   tree=material.node_tree;output=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL')
   if not output.inputs['Surface'].links:continue
   original=output.inputs['Surface'].links[0].from_socket
   mix=tree.nodes.new('ShaderNodeMixShader');transparent=tree.nodes.new('ShaderNodeBsdfTransparent');geometry=tree.nodes.new('ShaderNodeNewGeometry')
   tree.links.new(geometry.outputs['Backfacing'],mix.inputs[0]);tree.links.new(original,mix.inputs[1]);tree.links.new(transparent.outputs[0],mix.inputs[2]);tree.links.new(mix.outputs[0],output.inputs['Surface'])
  bpy.ops.object.camera_add(location=(5,7,2.5));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.65))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.5;bpy.context.scene.camera=camera
  for pos,power in [((3,4,5),1500),((-4,1,4),1000),((0,-5,3),1200)]:
   bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=5;light.rotation_euler=(Vector((0,0,.7))-light.location).to_track_quat('-Z','Y').to_euler()
  scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.world.color=(.18,.18,.18);scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(code+'-'+mode+'.png'));bpy.ops.render.render(write_still=True)
