"""Retain material/UV evidence for manually chosen front-window inspection rays."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));from tools.carmodels.assets import decode_scene
cars=json.loads((ROOT/'godot/assets/cars.json').read_text())['cars'];reports=[]
for code in ['GT4_HOND0019','GT4_TOYT0006','GT4_NISS0021','GT4_LNCA0005']:
 car=next(c for c in cars if c['code']==code);paints={r['name']:r for r in car['paint_materials']};parts=decode_scene((ROOT/'godot/assets/cars'/f'{code}.glb').read_bytes());rays=[]
 for x in [-.25,0,.25]:
  origin=np.array([x,2.0,-6]);direction=np.array([x,.85,0])-origin;direction/=np.linalg.norm(direction);hits=[]
  for part in parts:
   if part['name']!='body':continue
   tri=part['positions'][part['indices']];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);safe=np.abs(a)>1e-8;f=np.where(safe,1/np.where(safe,a,1),0);s=origin-tri[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*(q@direction);t=f*np.einsum('ij,ij->i',e2,q);selected=np.where(safe&(u>=0)&(v>=0)&(u+v<=1)&(t>0))[0]
   for i in selected:
    material=part['material'];uv=part['uv'][part['indices'][i]].T@np.array([1-u[i]-v[i],u[i],v[i]]);texture=material['texture'];rgba=material['factor'].tolist()
    if texture is not None:
     y=int((uv[1]%1)*texture.shape[0])%texture.shape[0];xx=int((uv[0]%1)*texture.shape[1])%texture.shape[1];rgba=(texture[y,xx]/255*material['factor']).tolist()
    paint=paints.get(material['name']);mask_value=None
    if paint and paint.get('mask_path'):
     mask=np.asarray(Image.open(ROOT/'godot'/paint['mask_path'][6:]).convert('L'));mask_value=int(mask[int((uv[1]%1)*mask.shape[0])%mask.shape[0],int((uv[0]%1)*mask.shape[1])%mask.shape[1]])
    hits.append(dict(distance=float(t[i]),position=(origin+t[i]*direction).tolist(),material=material['name'],uv=uv.tolist(),base_rgba=rgba,alpha_mode=material['alpha_mode'],paintable=bool(paint),mask_value=mask_value))
  rays.append(dict(origin=origin.tolist(),direction=direction.tolist(),hits=sorted(hits,key=lambda h:h['distance'])))
 reports.append(dict(code=code,inspection='Manual front-window-region rays; all intersections retained, no semantic automatic exclusion.',rays=rays))
out=ROOT/'artifacts/juiced2-build/donor-pass-audit/window-rays.json';out.write_text(json.dumps(reports,indent=2,allow_nan=False)+'\n')
for r in reports:
 print(r['code'],[(h['material'],[round(v,2)for v in h['position']],h['paintable'],h['mask_value'])for h in r['rays'][1]['hits'][:5]])
