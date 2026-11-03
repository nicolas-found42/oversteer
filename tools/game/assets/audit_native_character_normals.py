"""Measure original float normals against original triangle winding, no edits."""
import hashlib,json,struct
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters'
catalog=json.loads((SOURCE/'component-catalog-evidence.json').read_text());reports=[]
for skin in catalog['skins']:
 raw=(ROOT/skin['path']).read_bytes();cursor=0;parts=[]
 while (vs:=raw.find(struct.pack('<I',0x70000007),cursor))>=0:
  cursor=vs+4;nv=struct.unpack_from('<I',raw,vs+4)[0]
  strides=[st for st in [68,76]if nv and raw[vs+8+nv*st:vs+12+nv*st]==struct.pack('<I',0x70000006)]
  if not strides:continue
  assert len(strides)==1;stride=strides[0]
  p=np.array([struct.unpack_from('<3f',raw,vs+8+i*stride)for i in range(nv)])
  n=np.array([struct.unpack_from('<3f',raw,vs+8+i*stride+32)for i in range(nv)])
  assert np.isfinite(p).all()and np.isfinite(n).all()
  ng=struct.unpack_from('<I',raw,vs+8+nv*stride+4)[0];at=vs+8+nv*stride+8;triangles=[]
  for _ in range(ng):
   first=struct.unpack_from('<I',raw,at)[0]
   if first==0:_,nt,mid=struct.unpack_from('<3I',raw,at);at+=12
   else:nt,mid=struct.unpack_from('<2I',raw,at);at+=8
   tri=np.array(struct.unpack_from('<'+str(nt*3)+'H',raw,at),dtype=int).reshape(-1,3);assert tri.max()<nv
   triangles.append(tri);at=(at+6*nt+15)&~15
  tri=np.concatenate(triangles);cross=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]])
  length=np.linalg.norm(cross,axis=1);avg=n[tri].mean(1);avg_len=np.linalg.norm(avg,axis=1);good=(length>1e-8)&(avg_len>1e-8)
  dots=np.sum(cross[good]*avg[good],axis=1)/(length[good]*avg_len[good])
  unit_error=float(np.max(abs(np.linalg.norm(n,axis=1)-1)))
  parts.append(dict(source_vertex_offset=vs,stride=stride,vertices=nv,triangles=len(tri),degenerate_triangles=int(np.sum(~good)),normal_unit_max_error=unit_error,source_cross_vs_native_normal_percentiles=np.percentile(dots,[0,1,10,50,90,99,100]).tolist(),source_clockwise_fraction=float(np.mean(dots<0)),opposed_area_fraction=float(np.sum(length[good][dots<0])/np.sum(length[good])),export_analysis='ExporterY/Zreflectionhasdet-1andALSOswapsindices0,2,1:bothcancel,retainingnativeCWorientationandopposingoutwardnativeNORMAL. Candidatepreservesoriginalindiceswithreflectedcoordinates.'))
 reports.append(dict(key=skin['key'],name=skin['native_name'],source_path=skin['path'],sha256=hashlib.sha256(raw).hexdigest(),parts=parts))
all_parts=[part for skin in reports for part in skin['parts']]
report=dict(skins=reports,summary=dict(source_skins=len(reports),drawable_skins=sum(bool(s['parts'])for s in reports),chunks=len(all_parts),all_float_normal_unit_error_max=max(p['normal_unit_max_error']for p in all_parts),chunks_source_clockwise_majority=sum(p['source_clockwise_fraction']>.5 for p in all_parts)),limits=['NormalsandindicesfromoriginalJSM; windingclockwiserelativetooriginalauthorednormal—notanassumptionfromD3Dname.','No runtimeassetschanged; sourceNORMAL/indexcandidateandnativeGPUproofstillrequired.','Retainoriginalhardedges/duplicatevertices; no welding.'])
out=SOURCE/'native-normal-winding-audit.json';out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['summary'])
