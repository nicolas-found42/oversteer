"""Sample original static road triangles at native BTF centerline points."""
import sys,json,struct,math,collections
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import node_matrix
p=ROOT/'data/juiced2/tracks.json';doc=json.loads(p.read_text());reports=[]
for track in doc['tracks']:
 path=ROOT/'godot/assets/worlds'/f"{track['id']}.glb";b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:];triangles=[];material_counts=collections.Counter();cache={}
 def accessor(i):
  if i in cache:return cache[i]
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];cols={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']];dt={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];result=np.frombuffer(binary,dtype=dt,count=a['count']*cols,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,cols);cache[i]=result;return result
 def visit(i,parent):
  node=d['nodes'][i];mat=parent@node_matrix(node)
  if 'mesh'in node:
   for pr in d['meshes'][node['mesh']]['primitives']:
    material=d['materials'][pr['material']];shader=material.get('extras',{}).get('nativeShader','').lower()
    p=accessor(pr['attributes']['POSITION']);p=p@mat[:3,:3].T+mat[:3,3];t=p[accessor(pr['indices']).ravel()].reshape(-1,3,3);triangles.append(t);material_counts[shader]+=len(t)
  for j in node.get('children',[]):visit(j,mat)
 for i in d['scenes'][0]['nodes']:visit(i,np.eye(4))
 original=track.get('native_ai_points',track['points']);track['native_ai_points']=original;origin=np.array(track['source']['origin_source_units'])/100;points=np.array(original)+origin;surface=[];deltas=[];matched=0
 if triangles:
  t=np.concatenate(triangles);lo=t.min(1);hi=t.max(1)
  for point in points:
   keep=(lo[:,0]<=point[0])&(hi[:,0]>=point[0])&(lo[:,2]<=point[2])&(hi[:,2]>=point[2]);a=t[keep];height=point[1];found=False
   if len(a):
    den=(a[:,1,2]-a[:,2,2])*(a[:,0,0]-a[:,2,0])+(a[:,2,0]-a[:,1,0])*(a[:,0,2]-a[:,2,2]);valid=abs(den)>1e-8;a=a[valid];den=den[valid]
    u=((a[:,1,2]-a[:,2,2])*(point[0]-a[:,2,0])+(a[:,2,0]-a[:,1,0])*(point[2]-a[:,2,2]))/den;v=((a[:,2,2]-a[:,0,2])*(point[0]-a[:,2,0])+(a[:,0,0]-a[:,2,0])*(point[2]-a[:,2,2]))/den;valid=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1+1e-5);ys=u[valid]*a[valid,0,1]+v[valid]*a[valid,1,1]+(1-u[valid]-v[valid])*a[valid,2,1]
    if len(ys):
     candidate=ys[np.argmin(abs(ys-point[1]))]
     if abs(candidate-point[1])<=2:height=float(candidate);found=True;matched+=1;deltas.append(height-point[1])
   surface.append([float(point[0]-origin[0]),round(float(height-origin[1]),6),float(point[2]-origin[2])])
 else:surface=original
 track['surface_points']=surface;track['surface_source']={'kind':'vertical sample of original instanced native all static native triangles; nearest vertical face within2m ofBTF (native shader names are not surface semantics: Sydney bridge floor uses TreeFrondSingle)','model_path':f'res://assets/worlds/{track["id"]}.glb','matched_samples':matched,'sample_count':len(points),'unmatched_policy':'retained original BTF Y; no invented vertical offset','max_match_distance_m':2}
 reports.append(dict(id=track['id'],road_triangles=sum(material_counts.values()),shader_triangle_counts=dict(material_counts),matched=matched,total=len(points),median_delta_m=float(np.median(deltas))if deltas else None,max_abs_delta_m=max(map(abs,deltas))if deltas else None));print(track['id'],matched,'/',len(points),'roadtris',sum(material_counts.values()),flush=True)
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/tracks.json').write_bytes(p.read_bytes());cp=ROOT/'data/juiced2/content.json';content=json.loads(cp.read_text());by={t['id']:t for t in doc['tracks']}
for t in content['tracks']:t['surface_points']=by[t['id']]['surface_points']
cp.write_text(json.dumps(content,indent=2)+'\n');(ROOT/'godot/assets/game-content.json').write_text(json.dumps(content,separators=(',',':'))+'\n');(ROOT/'artifacts/juiced2-build/native-road-height-verification.json').write_text(json.dumps(reports,indent=2)+'\n')
