"""Measure source-ground cross sections and separate physical-wall candidates.

Widths follow connected original triangle coverage from native road-contact Y,
not an offset from the AI path. Unknown/censored sides retain explicit fallback.
Wall candidates are original non-foliage vertical triangles crossing car height;
this is geometric collision evidence, not recovered CLD collision classification.
"""
import json,struct,sys,math,hashlib,re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import node_matrix
p=ROOT/'data/juiced2/tracks.json';doc=json.loads(p.read_text());reports=[];MAX=150.;STEP=.10
for track in doc['tracks']:
 if 'drift'not in track['id']and track['city']not in ['Paris','Sydney']:continue
 path=ROOT/'godot/assets/worlds'/f"{track['id']}.glb";raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);binary=raw[28+size:];cache={};triangles=[];labels=[];shaders=[];wall_allowed=[]
 def accessor(ai):
  if ai not in cache:
   a=d['accessors'][ai];v=d['bufferViews'][a['bufferView']];cols={'SCALAR':1,'VEC3':3}[a['type']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]);cache[ai]=np.ndarray((a['count'],cols),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',cols*dt.itemsize),dt.itemsize)).copy()
  return cache[ai]
 def visit(i,parent):
  node=d['nodes'][i];m=parent@node_matrix(node)
  if 'mesh'in node:
   mesh=d['meshes'][node['mesh']]
   for primitive in mesh['primitives']:
    vertices=accessor(primitive['attributes']['POSITION']);vertices=vertices@m[:3,:3].T+m[:3,3];tri=vertices[accessor(primitive['indices']).ravel()].reshape(-1,3,3);mat=d['materials'][primitive['material']];shader=mat.get('extras',{}).get('nativeShader','').lower();triangles.append(tri);labels.extend([mesh['name']]*len(tri));shaders.extend([shader]*len(tri));wall_allowed.extend([not any(w in shader for w in ['tree','foliage','leaf','frond'])]*len(tri))
  for j in node.get('children',[]):visit(j,m)
 for i in d['scenes'][0]['nodes']:visit(i,np.eye(4))
 t=np.concatenate(triangles);lo=t.min(1);hi=t.max(1);normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normal_length=np.linalg.norm(normals,axis=1);ny=abs(normals[:,1])/np.maximum(normal_length,1e-12);ground=ny>.65;walls=(ny<.5)&np.array(wall_allowed);origin=np.array(track['source']['origin_source_units'])/100;points=np.array(track.get('surface_points',track['points']))+origin;centreline=np.array(track['points'])+origin;widths=[];wall_widths=[];evidence=[]
 for index,point in enumerate(points):
  tangent=centreline[(index+1)%len(points)]-centreline[(index-1)%len(points)];tangent[1]=0;tangent/=max(np.linalg.norm(tangent),1e-9);left=np.array([-tangent[2],0,tangent[0]])
  # A finite native-space query is a censoring bound, never presented as an edge.
  near=(lo[:,0]<=point[0]+MAX)&(hi[:,0]>=point[0]-MAX)&(lo[:,2]<=point[2]+MAX)&(hi[:,2]>=point[2]-MAX)&(lo[:,1]<=point[1]+3)&(hi[:,1]>=point[1]-3)&(ground|walls);ids=np.where(near)[0];a=t[ids];distance=(a-point)@tangent;keep=(distance.min(1)<=1e-7)&(distance.max(1)>=-1e-7);ids=ids[keep];a=a[keep];distance=distance[keep];crossings=[]
  for v,w in [(0,1),(1,2),(2,0)]:
   den=distance[:,w]-distance[:,v];u=np.divide(-distance[:,v],den,out=np.full_like(den,np.nan),where=abs(den)>1e-10);valid=(u>=-1e-7)&(u<=1+1e-7);q=a[:,v]+u[:,None]*(a[:,w]-a[:,v]);q[~valid]=np.nan;crossings.append(q)
  q=np.stack(crossings,1);s=(q-point)@left;valid=np.isfinite(s).sum(1)>=2;ids=ids[valid];q=q[valid];s=s[valid]
  if not len(ids):widths.append([track['road_width']/2]*2);wall_widths.append([None,None]);evidence.append(dict(index=index,confidence='fallback_no_crosssection',surface_half_widths=widths[-1]));continue
  minix=np.nanargmin(s,axis=1);maxix=np.nanargmax(s,axis=1);smin=s[np.arange(len(s)),minix];smax=s[np.arange(len(s)),maxix];ymin=q[np.arange(len(q)),minix,1];ymax=q[np.arange(len(q)),maxix,1];g=ground[ids]&(smax-smin>1e-6);spans=np.stack([smin[g],smax[g],ymin[g],ymax[g]],1);gids=ids[g];contains=(spans[:,0]<=0)&(spans[:,1]>=0)
  if not contains.any():initial=None
  else:
   candidates=np.where(contains)[0];ys=spans[candidates,2]+(spans[candidates,3]-spans[candidates,2])*(-spans[candidates,0])/(spans[candidates,1]-spans[candidates,0]);best=int(np.argmin(abs(ys-point[1])));initial=int(candidates[best])if abs(ys[best]-point[1])<=.35 else None
  side_width=[];side_flags=[];floor_label=None
  for side in [-1,1]:
   if initial is None:side_width.append(None);side_flags.append('unmatched_floor');continue
   row=spans[initial];edge=float(row[0]if side<0 else row[1]);height=float(row[2]if side<0 else row[3]);floor_label=labels[gids[initial]];visited={initial}
   for _ in range(len(spans)):
    candidates=np.where((spans[:,0]<=edge+1e-4)&(spans[:,1]>=edge-1e-4)&((spans[:,0]<edge-1e-5)if side<0 else(spans[:,1]>edge+1e-5)))[0];accepted=[]
    for candidate in candidates:
     if int(candidate)in visited:continue
     row=spans[candidate];at=row[2]+(row[3]-row[2])*(edge-row[0])/(row[1]-row[0])
     if abs(at-height)<=STEP:accepted.append(int(candidate))
    if not accepted:break
    chosen=min(accepted,key=lambda i:spans[i,0])if side<0 else max(accepted,key=lambda i:spans[i,1]);visited.add(chosen);row=spans[chosen];edge=float(row[0]if side<0 else row[1]);height=float(row[2]if side<0 else row[3])
    if abs(edge)>=MAX:break
   side_width.append(abs(edge));side_flags.append('measured_floor_edge'if abs(edge)<MAX else'censored_floor')
  # Left = positive projection on [-dz, +dx]; right = negative projection.
  side_width=side_width[::-1];side_flags=side_flags[::-1];wall_dist=[];wall_sources=[]
  for sign in [1,-1]:
   candidates=[]
   for j,tid in enumerate(ids):
    if not walls[tid]:continue
    ya=q[j,:,1];finite=np.isfinite(ya);ys=ya[finite];ss=s[j,finite]
    if ys.max()<point[1]+.5 or ys.min()>point[1]+.3:continue
    delta=ys[-1]-ys[0]
    position=float(ss[0]+(ss[-1]-ss[0])*(point[1]+.5-ys[0])/delta)if abs(delta)>1e-7 else float(ss.mean())
    if .1<position*sign<MAX:candidates.append((position*sign,int(tid)))
   if candidates:
    distance,tid=min(candidates);wall_dist.append(distance);wall_sources.append(labels[tid])
   else:wall_dist.append(None);wall_sources.append(None)
  final=[]
  for side in range(2):
   floor=side_width[side];wall=wall_dist[side]
   if floor is None or side_flags[side]=='censored_floor':value=wall if wall is not None else track['road_width']/2
   else:value=min(floor,wall)if wall is not None else floor
   final.append(round(max(.1,float(value)),4))
  widths.append(final);wall_widths.append([round(v,4)if v is not None else None for v in wall_dist]);evidence.append(dict(index=index,surface_half_widths=final,floor_half_widths=side_width,floor_status=side_flags,wall_half_widths=wall_widths[-1],floor_native_geometry=floor_label,wall_native_geometries=wall_sources,confidence='source_geometry_crosssection; drivable/wallclassification adaptation'))
 track['surface_half_widths']=widths;track['wall_half_widths']=wall_widths;track['crosssection_source']=dict(kind='Exact original instanced native triangle cross sections, connected floor coverage plus vertical wall candidates',model_path=f'res://assets/worlds/{track["id"]}.glb',model_sha256=hashlib.sha256(raw).hexdigest(),sample_count=len(points),left_direction='[-dz/L,0,+dx/L] relative travel',max_search_m=MAX,censored_policy='Physical wall if measured, otherwise original7m halfwidth fallback; never claim query bound as measured edge',floor_join_height_tolerance_m=STEP,wall_height_test='crosses source ground +.5m, base not above+.3m; excludes native tree/foliage shader vertical faces',limits=['Native CLD collision classification not yet decoded; static geometric floor and wall candidates are explicit adaptations.','Per-sample provenance in native-crosssections evidence; source BTF AI path is not interpreted as an arena boundary.'])
 report=dict(id=track['id'],samples=len(points),surface_width_range=[np.min(np.array(widths),axis=0).tolist(),np.max(np.array(widths),axis=0).tolist()],wall_matches=sum(v is not None for pair in wall_widths for v in pair),samples_evidence=evidence);reports.append(report);print(track['id'],len(points),'range',report['surface_width_range'],'wallmatches',report['wall_matches'],flush=True)
p.write_text(json.dumps(doc,indent=2,allow_nan=False)+'\n');(ROOT/'godot/assets/tracks.json').write_bytes(p.read_bytes());by={t['id']:t for t in doc['tracks']}
for p in [ROOT/'data/juiced2/content.json',ROOT/'godot/assets/game-content.json']:
 content=json.loads(p.read_text())
 for t in content['tracks']:
  if 'surface_half_widths'in by[t['id']]:t['surface_half_widths']=by[t['id']]['surface_half_widths'];t['wall_half_widths']=by[t['id']]['wall_half_widths']
 p.write_text(json.dumps(content,indent=2,allow_nan=False)+'\n')
(ROOT/'artifacts/juiced2-build/native-crosssections.json').write_text(json.dumps(reports,indent=2,allow_nan=False)+'\n')
