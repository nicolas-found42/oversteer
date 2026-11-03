"""Bounded original CLD v2 parser, exact serialized reads from 82270218.

The native categories and surface bytes are retained without shader-name or
orientation classification. Parametric controls are not called triangle meshes.
"""
import struct,json,hashlib
from pathlib import Path
def parse(raw):
 cursor=0
 def take(size):
  nonlocal cursor
  assert 0<=size<=len(raw)-cursor,(cursor,size,len(raw));result=raw[cursor:cursor+size];cursor+=size;return result
 def unpack(fmt):return struct.unpack('>'+fmt,take(struct.calcsize('>'+fmt)))
 def count():
  value=unpack('I')[0];assert value<10000000;return value
 def surfaces(n):
  result=list(take(n));take((-n)%4);return result
 assert count()==2
 nv=count();points=[list(unpack('3fI'))for _ in range(nv)]
 nt=count();triangles=[dict(indices=list(unpack('4I')),normal=list(unpack('4f')))for _ in range(nt)];flags=surfaces(nt)
 for row,flag in zip(triangles,flags):row['surface_raw']=flag;row['surface_id']=flag&127
 ns=count();splines=[dict(indices=list(unpack('4I')))for _ in range(ns)];flags=surfaces(ns)
 for row,flag in zip(splines,flags):row.update(surface_raw=flag,surface_id=flag&127)
 for row in splines:row['planes']=list(unpack('12f'))
 for row in splines:row['bounds']=list(unpack('8f'))
 npoly=count();polygons=[]
 for _ in range(npoly):
  planes=list(unpack('20f'));metadata=list(unpack('6I'));bounds_frame=list(unpack('12f'));bounds=list(unpack('8f'));flag=unpack('B')[0];polygons.append(dict(planes=planes,metadata=metadata,bounds_frame=bounds_frame,bounds=bounds,surface_raw=flag,surface_id=flag&127))
 polygon_indices=list(unpack(str(count())+'I'))if npoly else[]
 for row in polygons:
  n,first=row['metadata'][:2];assert first+n<=len(polygon_indices);row['indices']=polygon_indices[first:first+n]
 npatch=count();patches=[]
 for _ in range(npatch):
  metadata=list(unpack('19I'));bounds_frame=list(unpack('12f'));bounds=list(unpack('8f'));flag=unpack('B')[0];patches.append(dict(metadata=metadata,bounds_frame=bounds_frame,bounds=bounds,surface_raw=flag,surface_id=flag&127))
 for row in triangles:
  assert max(row['indices'][:3],default=0)<nv
 for row in splines+polygons:assert max(row['indices'],default=0)<nv
 return dict(points=points,triangles=triangles,splines=splines,polygons=polygons,patches=patches,parsed_offset=cursor,trailing_bytes=len(raw)-cursor,trailing_sha256=hashlib.sha256(raw[cursor:]).hexdigest())
if __name__=='__main__':
 root=Path(__file__).resolve().parents[3];source=root/'artifacts/juiced2-build/collision';reports=[]
 for path in source.glob('*.cld'):
  raw=path.read_bytes();doc=parse(raw);doc['source_sha256']=hashlib.sha256(raw).hexdigest();(source/(path.name+'.json')).write_text(json.dumps(doc,separators=(',',':'),allow_nan=False)+'\n');report=dict(source=path.name,sha256=doc['source_sha256'],counts={key:len(doc[key])for key in ['points','triangles','splines','polygons','patches']},parsed_offset=doc['parsed_offset'],trailing_bytes=doc['trailing_bytes']);reports.append(report);print(path.name,report['counts'],'tail',report['trailing_bytes'])
 (source/'native-cld-inventory.json').write_text(json.dumps(dict(consumer='82270218',records=reports,limits=['Trailing native spatial hierarchy retained by SHA but not decoded.','Parametric patch metadata retained; control layout and collision evaluation require additional native consumer evidence.']),indent=2)+'\n')
