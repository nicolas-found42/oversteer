import json,struct,numpy as np,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import node_matrix
tracks=json.loads((ROOT/'data/juiced2/tracks.json').read_text())['tracks'];track=next((t for t in tracks if len(sys.argv)>1 and t['id']==sys.argv[1]),tracks[0]);b=(ROOT/'godot/assets/worlds'/f"{track['id']}.glb").read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:];origin=np.array(track['source']['origin_source_units'])/100
if len(sys.argv)>2:origin+=np.array(track['points'][int(sys.argv[2])])
hits=[]
def acc(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dt='<f4' if a['componentType']==5126 else '<u4';cols=3 if a['type']=='VEC3' else 1;return np.frombuffer(binary,dtype=dt,count=a['count']*cols,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,cols)
def visit(i,parent):
 node=d['nodes'][i];mat=parent@node_matrix(node)
 if 'mesh' in node:
  for pr in d['meshes'][node['mesh']]['primitives']:
   pos=acc(pr['attributes']['POSITION']);p=pos@mat[:3,:3].T+mat[:3,3];tri=p[acc(pr['indices']).ravel()];a=tri.reshape(-1,3,3);low=a.min(1);hi=a.max(1);keep=(low[:,0]<=origin[0])&(hi[:,0]>=origin[0])&(low[:,2]<=origin[2])&(hi[:,2]>=origin[2]);a=a[keep]
   for t in a:
    den=(t[1,2]-t[2,2])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,2]-t[2,2])
    if abs(den)<1e-7:continue
    u=((t[1,2]-t[2,2])*(origin[0]-t[2,0])+(t[2,0]-t[1,0])*(origin[2]-t[2,2]))/den;v=((t[2,2]-t[0,2])*(origin[0]-t[2,0])+(t[0,0]-t[2,0])*(origin[2]-t[2,2]))/den
    if u>=0 and v>=0 and u+v<=1:hits.append(dict(height=u*t[0,1]+v*t[1,1]+(1-u-v)*t[2,1],material=d['materials'][pr['material']],uv_accessor=pr['attributes'].get('TEXCOORD_0')))
 for j in node.get('children',[]):visit(j,mat)
for i in d['scenes'][0]['nodes']:visit(i,np.eye(4))
print('BTF',origin,'hits',[(round(float(h['height']),3),h['material']['name'],h['material'].get('extras',{}).get('nativeShader'))for h in hits])
