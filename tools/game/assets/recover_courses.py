"""Recover native BTF routes; centimeter units and constant road width inferred."""
import json,struct,math,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text())
out=ROOT/'artifacts/juiced2-build/courses';out.mkdir(parents=True,exist_ok=True)
tracks=[]
with open(inv['iso'],'rb') as iso:
 for f in inv['files']:
  if not f['path'].endswith('.btf'):continue
  iso.seek(f['offset']);b=iso.read(f['size']);n=struct.unpack_from('>I',b)[0];start=4+16*n+60;points=[]
  count=struct.unpack_from('>I',b,start-4)[0]
  for i in range((count+1)//2):
   p=struct.unpack_from('>4f',b,start+i*140)
   if not all(math.isfinite(v) and abs(v)<1e7 for v in p):raise ValueError(f['path'])
   if points and math.dist(p[:3],points[-1][:3])>3000:raise ValueError('discontinuous '+f['path'])
   points.append(p)
  closure=math.dist(points[0][:3],points[-1][:3]);assert closure<2000
  ident=re.sub('[^a-z0-9]+','_',f['path'][7:-4].lower()).strip('_')
  origin=points[0][:3];normal=[[round((p[j]-origin[j])/100,5) for j in range(3)] for p in points]
  length=sum(math.dist(normal[i],normal[(i+1)%len(normal)]) for i in range(len(normal)))
  city=f['path'].split('/')[1].replace('_',' ');route=f['path'].split('/')[-1][:-4]
  row=dict(id=ident,name=city+' / '+route,city=city,route=route,points=normal,road_width=14.0,length_m=round(length,3),source=dict(kind='recovered_native_route_samples',path=f['path'],iso_offset=f['offset'],sha256=hashlib.sha256(b).hexdigest(),record_offset=start,record_stride=140,sample_count=len(points),header_count=count,origin_source_units=list(origin),closure_gap_source_units=closure),confidence=dict(positions='high: all33 contiguous sample arrays form closed routes',unit_scale='inferred centimetres',road_width='reconstructed 14m constant; native cross section unresolved',direction='native record order; race reversal unresolved'),scenery_status='native geometry archive inventoried; material/mesh format not decoded')
  tracks.append(row);(out/(ident+'.btf')).write_bytes(b)
(ROOT/'data/juiced2/tracks.json').write_text(json.dumps(dict(schema_version=1,tracks=tracks),indent=2)+'\n')
(ROOT/'artifacts/juiced2-build/course-verification.json').write_text(json.dumps(dict(route_count=len(tracks),all_closed=True,max_closure_gap_m=max(t['source']['closure_gap_source_units']/100 for t in tracks),sample_count=sum(len(t['points']) for t in tracks)),indent=2))
print('Recovered',len(tracks),'native routes;',sum(len(t['points']) for t in tracks),'samples')
