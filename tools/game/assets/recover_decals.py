"""Recover exact original decal catalog/categories and all bound source artwork.

Default output is staged evidence. --publish writes game assets after coordination.
"""
import sys,json,struct,zlib,hashlib,re,shutil
from pathlib import Path
from PIL import Image,ImageDraw
from jfs_hash import filename_hash
from decal_color_mode import classify
from xenos_texture import decode
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-build/decals';source.mkdir(exist_ok=True);inventory=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());archives={}
with open(inventory['iso'],'rb')as iso:
 for ext in ['jfs','jfshdr']:
  path=source/('cardecals.'+ext)
  if not path.exists():
   row=next(x for x in inventory['files']if x['path']=='cardecals.'+ext);iso.seek(row['offset']);path.write_bytes(iso.read(row['size']))
  archives[ext]=path.read_bytes()
h=archives['jfshdr'];archive=archives['jfs'];members={}
for i in range(struct.unpack_from('>I',h)[0]):
 key,o,p,u,_,_=struct.unpack_from('>6I',h,4+i*24);raw=archive[o:o+p];raw=raw if p==u else zlib.decompress(raw);assert len(raw)==u;members[key]=dict(raw=raw,index=i,offset=o,packed_size=p,decoded_size=u)
key=filename_hash('decals.txt');catalog_source=members[key];text=catalog_source['raw'].decode();categories=[];names=[]
for line in text.splitlines():
 fields=line.split()
 if not fields:continue
 if fields[0]=='NUMDECALS':categories.append(dict(id=fields[1],name=fields[1],declared_count=int(fields[2]),design_ids=[]))
 elif fields[0]=='DECAL':names.append(fields[1])
 else:raise ValueError(line)
category_by={c['id']:c for c in categories};prefixes=sorted(category_by,key=len,reverse=True);staged=source/'prepared';(staged/'native').mkdir(parents=True,exist_ok=True);designs=[];unresolved=[];bound=set();representatives={}
for label in names:
 filename=label+'.ddt';key=filename_hash(filename);category=next((p for p in prefixes if label.startswith(p+'_')),None)
 if key not in members or category is None:unresolved.append(dict(native_label=label,key=f'{key:08x}',category=category));continue
 member=members[key];b=member['raw'];fmt,w,height=struct.unpack_from('>3I',b);im=decode(b[40:],w,height,fmt)
 if im is None:unresolved.append(dict(native_label=label,key=f'{key:08x}',reason='unsupported native texture format'));continue
 dest=staged/'native'/f'{key:08x}.png';im.save(dest);ident=f'native_{key:08x}';bound.add(key);category_by[category]['design_ids'].append(ident);representatives.setdefault(category,dest);designs.append(dict(id=ident,native_label=label,name=label,category=category,texture_path=f'res://assets/decals/native/{key:08x}.png',width=w,height=height,color_mode='authored_rgba',default_tint=[1,1,1,1],alpha_bbox=im.getchannel('A').getbbox(),source=dict(bank='cardecals.jfs',filename=filename,key=f'{key:08x}',member=member['index'],offset=member['offset'],packed_size=member['packed_size'],decoded_size=member['decoded_size'],format_hex=hex(fmt),sha256=hashlib.sha256(b).hexdigest())))
 designs[-1].update(classify(im))
for category in categories:category['recovered_count']=len(category['design_ids']);category['count_matches_declaration']=category['declared_count']==category['recovered_count']
result=dict(categories=categories,designs=designs,source=dict(bank='cardecals.jfs',archive_sha256=hashlib.sha256(archive).hexdigest(),catalog_filename='decals.txt',catalog_key='9398ce24',catalog_member=catalog_source['index'],catalog_sha256=hashlib.sha256(catalog_source['raw']).hexdigest()),unresolved=unresolved,unclassified_texture_keys=[f'{k:08x}'for k in members if k not in bound and k!=filename_hash('decals.txt')],limits=['Original catalog and bitmap art recovered; full runtime projection/layer/category workflow acceptance is separate.','Six menu supercategories are not inferred as exact source bindings from category names.','Exact constant black/white visible source RGB is classified as alpha mask; chosen-color fill is an explicit renderer adaptation, native compositor formula unresolved.'])
(staged/'catalog.json').write_text(json.dumps(result,indent=2)+'\n');cols=10;cell=150;items=list(representatives.items());sheet=Image.new('RGB',(cols*cell,((len(items)+cols-1)//cols)*170),(45,45,45));draw=ImageDraw.Draw(sheet)
for i,(category,p)in enumerate(items):
 im=Image.open(p).convert('RGBA');im.thumbnail((140,140));x=i%cols*cell+5;y=i//cols*170+5;sheet.paste(im,(x,y),im);draw.text((x,y+140),category,fill='white')
sheet.save(source/'native-decal-categories.png');(source/'verification.json').write_text(json.dumps(dict(declared_designs=len(names),recovered=len(designs),categories=len(categories),unresolved=unresolved,unclassified=len(result['unclassified_texture_keys']),count_mismatches=[dict(id=c['id'],declared=c['declared_count'],actual=c['recovered_count'])for c in categories if not c['count_matches_declaration']]),indent=2)+'\n')
if '--publish'in sys.argv:
 dest=ROOT/'godot/assets/decals';shutil.copytree(staged,dest,dirs_exist_ok=True);(ROOT/'data/juiced2/decals.json').write_bytes((staged/'catalog.json').read_bytes())
print('Recovered',len(designs),'/',len(names),'native designs;',len(categories),'declared categories;',len(unresolved),'unresolved;',len(result['unclassified_texture_keys']),'unclassified textures;', 'PUBLISHED'if'--publish'in sys.argv else'STAGED')
