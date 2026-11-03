"""Recover mounting planes only from explicit native LicensePlate mesh materials."""
import json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import decode_scene
p=ROOT/'data/juiced2/cars.json';doc=json.loads(p.read_text());reports=[]
for car in doc['cars']:
 b=(ROOT/'godot/assets/cars'/f"{car['code']}.glb").read_bytes();d=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);names={m['name']for m in d['materials']if m.get('extras',{}).get('sourceShader')=='LicensePlate'};vertices=[]
 for part in decode_scene(b,car['game']):
  if part['material']['name']in names:vertices.extend(part['positions'][np.unique(part['indices'])].tolist())
 if not vertices:car['plate_socket']=None;continue
 ps=np.array(vertices);centre=ps.mean(0);eigenvectors=np.linalg.eigh(np.cov((ps-centre).T))[1];normal=eigenvectors[:,0]
 if normal[2]<0:normal=-normal
 right=np.array([1.,0,0]);right-=normal*np.dot(right,normal);right/=np.linalg.norm(right);up=np.cross(normal,right);widths=(ps-centre)@right;heights=(ps-centre)@up;centre+=right*(widths.min()+widths.max())/2+up*(heights.min()+heights.max())/2
 socket=dict(center=(centre+normal*.002).tolist(),normal=normal.tolist(),right=right.tolist(),up=up.tolist(),size=[float(np.ptp(widths)),float(np.ptp(heights))],source='Exact native MCLA LicensePlate sourceShader primitive vertices in normalized selected scene',material_names=sorted(names),confidence='high semantic mounting surface; runtime text-plane alignment still requires capture verification');car['plate_socket']=socket;reports.append(dict(code=car['code'],socket=socket))
p.write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'godot/assets/cars.json').write_bytes(p.read_bytes());(ROOT/'artifacts/juiced2-build/plate-socket-verification.json').write_text(json.dumps(dict(recovered=reports,unresolved=[c['code']for c in doc['cars']if c['plate_socket']is None]),indent=2));print('Recovered',len(reports),'exact source plate planes; no guessed anchors for remaining',30-len(reports))
