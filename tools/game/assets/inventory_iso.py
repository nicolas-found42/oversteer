"""Index the supplied ISO without modifying its contents."""
import mmap,struct,json,hashlib,pathlib
src=pathlib.Path('resources/games/juiced-2/juiced-2-hot-import-nights.iso'); out=pathlib.Path('artifacts/juiced2-recovery');base=265879552
with src.open('rb') as f:
 m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ); vd=base+32*2048
 assert m[vd:vd+20]==b'MICROSOFT*XBOX*MEDIA'
 root,size=struct.unpack_from('<II',m,vd+20);rows=[];seen=set()
 def directory(sec,size,prefix):
  start=base+sec*2048
  def node(o):
   if (start,o) in seen: return
   seen.add((start,o))
   if o+14>size:raise ValueError('directory bounds')
   l,r,s,n,attr,nlen=struct.unpack_from('<HHIIBB',m,start+o)
   name=m[start+o+14:start+o+14+nlen].decode('ascii');path=prefix+name
   if l: node(l*4)
   rows.append({'path':path,'sector':s,'offset':base+s*2048,'size':n,'directory':bool(attr&16),'attributes':attr})
   if attr&16:directory(s,n,path+'/')
   if r:node(r*4)
  if size:node(0)
 directory(root,size,'')
 (out/'xdvdfs-inventory.json').write_text(json.dumps({'iso':str(src.resolve()),'partition_base':base,'descriptor_offset':vd,'files':rows},indent=2))
 print('Indexed',len(rows),'XDVDFS records')
