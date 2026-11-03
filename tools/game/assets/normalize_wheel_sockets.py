"""Author four animation/swap sockets preserving native world-space geometry."""
import sys,json,struct,hashlib,copy,re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools.carmodels.assets import node_matrix
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());report=[]
def pack(d,tail):
 j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);return struct.pack('<4sIIII',b'glTF',2,20+len(j)+len(tail),len(j),0x4e4f534a)+j+tail
for c in doc['cars']:
 path=ROOT/'godot/assets/cars'/f"{c['code']}.glb";b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);tail=b[20+n:];nodes=d['nodes'];world={};parents={};roots=d['scenes'][0]['nodes']
 def visit(i,mat,parent=None):
  world[i]=mat@node_matrix(nodes[i]);parents[i]=parent
  for j in nodes[i].get('children',[]):visit(j,world[i],i)
 for i in roots:visit(i,np.eye(4))
 sockets=[]
 if c['game']=='gran-turismo-4':
  for loc in ['front_left','front_right','rear_left','rear_right']:
   idx=next(i for i,n in enumerate(nodes) if n.get('name')=='wheel_'+loc);pos=world[idx][:3,3].tolist();sockets.append(dict(node='wheel_'+loc,center=pos,radius=.20,tire_node='tire_'+loc,rim_nodes=['wheel_'+loc],tire_embedded=False))
 elif c['game']=='ford-racing-2':
  for i,node in enumerate(nodes):
   name=node.get('name','')
   if re.match('WHEEL_(BACK|FRONT)_(LEFT|RIGHT)_',name):
    pos=world[i][:3,3].tolist();loc=('front' if pos[2]<0 else 'rear')+('_left' if pos[0]<0 else '_right');parent=parents[i]
    if parent is None:roots.remove(i)
    else:nodes[parent]['children'].remove(i)
    mat=world[i].copy();mat[:3,3]-=pos;nodes[i]={k:v for k,v in node.items()if k not in ['translation','rotation','scale','matrix']};nodes[i]['name']='source_combined_rim_tire';nodes[i]['matrix']=mat.T.reshape(-1).tolist();wrapper=len(nodes);nodes.append(dict(name='wheel_'+loc,translation=pos,children=[i]));roots.append(wrapper);sockets.append(dict(node='wheel_'+loc,center=pos,radius=.20,tire_node=None,rim_nodes=['wheel_'+loc],tire_embedded=True,replacement_tire_path='res://assets/wheels/shared-tire.glb'))
 else:
  groups={}
  for i,node in enumerate(nodes):
   name=node.get('name','');match=re.search(r'@axl_(\d+)',name) if c['game']=='midnight-club-los-angeles' else re.match(r'whl_(\d+)_(rim|tire)',name)
   if match and 'mesh'in node:groups.setdefault(match[1],[]).append(i)
  for group,ids in groups.items():
   tireids=[i for i in ids if 'tire' in nodes[i].get('name','').lower()];samples=[]
   for i in tireids or ids:
    for pr in d['meshes'][nodes[i]['mesh']]['primitives']:
     a=d['accessors'][pr['attributes']['POSITION']];lo=a.get('min');hi=a.get('max')
     if lo and hi:
      for point in [lo,hi]:samples.append((world[i]@np.array([*point,1]))[:3])
   if not samples:raise ValueError('missing wheel bounds '+c['code'])
   pos=(np.min(samples,axis=0)+np.max(samples,axis=0))/2;loc=('front' if pos[2]<0 else 'rear')+('_left' if pos[0]<0 else '_right');rimids=[i for i in ids if i not in tireids]
   for kind,children in [('wheel',rimids),('tire',tireids)]:
    if not children:continue
    for i in children:
     parent=parents[i]
     if parent is None:roots.remove(i)
     else:nodes[parent]['children'].remove(i)
     mat=world[i].copy();mat[:3,3]-=pos;nodes[i]={k:v for k,v in nodes[i].items() if k not in ['matrix','translation','rotation','scale']};nodes[i]['matrix']=mat.T.reshape(-1).tolist();nodes[i]['name']=('rim_surface_' if kind=='wheel' else 'rubber_surface_')+str(i)
    idx=len(nodes);nodes.append({'name':kind+'_'+loc,'translation':pos.tolist(),'children':children});roots.append(idx)
   sockets.append(dict(node='wheel_'+loc,center=pos.tolist(),radius=.20,tire_node='tire_'+loc,rim_nodes=['wheel_'+loc],tire_embedded=False))
 if len(sockets)!=4:raise ValueError(f"Expected4 sockets {c['code']} got{len(sockets)}")
 for socket in sockets:
  axle='front'if 'front'in socket['node']else'rear';spec=c.get('model_car_spec',{});socket['radius']=spec.get('tire.rim_diameter_'+axle,16)*.0254/2;socket['outer_radius']=socket['radius']+spec.get('tire.section_width_'+axle,205)/1000*spec.get('tire.aspect_'+axle,55)/100
 c['wheel_sockets']=sockets;c['wheel_nodes']=[s['node'] for s in sockets];out=pack(d,tail);path.write_bytes(out);c['prepared_sha256']=hashlib.sha256(out).hexdigest();report.append(dict(code=c['code'],sockets=sockets))
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes());(ROOT/'artifacts/juiced2-build/wheel-socket-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Normalized120 wheel sockets')
