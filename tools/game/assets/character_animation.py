"""Append exact decoded native channels to an existing glTF skin document."""
import numpy as np

def append_source_clip(doc,binary,clip,label,key):
 nodes={node['name']:i for i,node in enumerate(doc['nodes'])};samplers=[];channels=[]
 def add(values,typ):
  values=np.array(values,dtype='<f4');assert np.isfinite(values).all()
  while len(binary)%4:binary.append(0)
  vi=len(doc['bufferViews']);data=values.tobytes();doc['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(data)));binary.extend(data);ai=len(doc['accessors']);item=dict(bufferView=vi,componentType=5126,count=len(values),type=typ)
  if typ=='SCALAR':item.update(min=[float(values.min())],max=[float(values.max())])
  doc['accessors'].append(item);return ai
 for track in clip['tracks']:
  assert track['name']in nodes and track['flags']&128
  count=max(2,track['key_count']-1);times=np.linspace(0,track['duration_ms']/1000,count);poses={'translation':[],'rotation':[]}
  for index in range(count):
   frame=track['keys'][min(max(index,track['begin_key']),track['end_key']-1)-track['begin_key']];t=frame.get('translation',track['constants'].get('translation'));q=frame.get('rotation_wxyz',track['constants'].get('rotation_wxyz'))
   if t is not None:poses['translation'].append([t[0]*.01,t[2]*.01,t[1]*.01])
   if q is not None:
    q=np.array([-q[1],-q[3],-q[2],q[0]],dtype=float);q/=np.linalg.norm(q)
    if poses['rotation']and np.dot(q,poses['rotation'][-1])<0:q=-q
    poses['rotation'].append(q.tolist())
  time_accessor=add(times,'SCALAR')
  for target,values in poses.items():
   if not values:continue
   output=add(values,'VEC3'if target=='translation'else'VEC4');sampler=len(samplers);samplers.append(dict(input=time_accessor,output=output,interpolation='LINEAR'));channels.append(dict(sampler=sampler,target=dict(node=nodes[track['name']],path=target)))
 evidence=dict(name=label,filename=label+'.anm',source_key=key,source_bank=clip['source_bank'],source_member=clip['source_member'],source_sha256=clip['source_sha256'],bone_tracks=len(clip['tracks']),duration_seconds=max(t['duration_ms']for t in clip['tracks'])/1000,native_consumers=['82243234 filename+.anm','82242808 uniform key interpolation','82308498 WXYZ quaternion matrix'],limits=['Original local transforms and exact filename identity retained; source guard key omitted at native duration.','Native quaternion interpolation approximated by glTF LINEAR quaternion interpolation; visual pose/motion proof required.','Untracked original bones retain source bind transforms.'])
 return dict(name=label,samplers=samplers,channels=channels,extras=evidence),evidence
