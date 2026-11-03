"""Render old/nonzero-alpha staged paint masks on unchanged actual geometry."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/donor-pass-audit'
old=json.loads((ROOT/'data/juiced2/cars.json').read_text())['cars'];new=json.loads((OUT/('staged-composite-paint-cars.json'if'--composite'in sys.argv else'staged-paint-cars.json')).read_text())['cars']
for code in ['MC3_VP_ESCALADE_03']if'--composite'in sys.argv else['GT4_BMW_0010','GT4_TOYT0006']:
 for mode,catalog in [('before',old),('staged',new)]:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  # Remove prior imported datablocks so exact material names remain stable.
  for mesh in list(bpy.data.meshes):
   if mesh.users==0:bpy.data.meshes.remove(mesh)
  for material in list(bpy.data.materials):
   if material.users==0:bpy.data.materials.remove(material)
  bpy.ops.import_scene.gltf(filepath=str(ROOT/'godot/assets/cars'/(code+'.glb')))
  car=next(c for c in catalog if c['code']==code)
  for row in car['paint_materials']:
   material=bpy.data.materials.get(row['name'])
   if not material:continue
   tree=material.node_tree;shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED');input=shader.inputs['Base Color'];link=input.links[0].from_socket if input.links else None;color=tuple(input.default_value)
   mix=tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=color;mix.inputs[2].default_value=(.8,.015,.02,1)
   if link:tree.links.new(link,mix.inputs[1])
   if row.get('mask_path'):
    texture=tree.nodes.new('ShaderNodeTexImage');path=(ROOT/'godot/assets/paint_masks'if mode=='before'else OUT/'paint_masks')/Path(row['mask_path']).name;texture.image=bpy.data.images.load(str(path));texture.image.colorspace_settings.name='Non-Color';tree.links.new(texture.outputs['Color'],mix.inputs[0])
   else:mix.inputs[0].default_value=1
   tree.links.new(mix.outputs[0],input)
  bpy.ops.object.camera_add(location=(5,7,2.5));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.65))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.5;bpy.context.scene.camera=camera
  for pos,power in [((3,4,5),1500),((-4,1,4),1000),((0,-5,3),1200)]:
   bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=5;light.rotation_euler=(Vector((0,0,.7))-light.location).to_track_quat('-Z','Y').to_euler()
  scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.world.color=(.18,.18,.18);scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(code+'-paint-'+mode+'.png'));bpy.ops.render.render(write_still=True)
