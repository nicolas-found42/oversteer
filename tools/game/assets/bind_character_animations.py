"""Bind original action strings to ANM members using native filename formatting."""
import re,json,struct,hashlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters'
def fast_hash(name):
 data=name.upper().encode('ascii');prefix=0;result=0
 for j,b in enumerate(data):
  if j<len(data)-1:prefix=(prefix+(b+7)*(b+j))&0xffffffff
  result=(result+(b+j)*(b+19)*prefix)&0xffffffff
 return result%4000000000
for value in ['CommonMale_AvatarIdle01.anm','Unique01_BetAcceptedGrudge01.anm','CommonMale_Fidget03.anm']:assert fast_hash(value)==filename_hash(value)
sources=[ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin',SOURCE/'script-67fc7231.bin',SOURCE/'anm-40a638b8.bin'];names={};source_rows=[]
for path in sources:
 raw=path.read_bytes();source_rows.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest()))
 for match in re.finditer(rb'[A-Za-z][A-Za-z0-9_]{2,65}',raw):
  name=match.group().decode('ascii');names.setdefault(name,[]).append(dict(source=str(path.relative_to(ROOT)),offset=match.start()))
members={}
for path in (SOURCE/'decoded-anm').glob('*.json'):
 clip=json.loads(path.read_text());members.setdefault(int(clip['source_key'],16),[]).append({k:clip[k]for k in ['source_bank','source_member','source_sha256','bone_count']})
prefixes=['CommonMale','CommonFemale']+[f'Unique{i:02}'for i in range(1,9)];hits={}
for source_name,evidence in names.items():
 candidates={source_name+'.anm':dict(format='Exact source identifier + .anm')}
 for prefix in prefixes:
  for suffix in ['']+[f'{i:02}'for i in range(1,11)]:candidates[prefix+'_'+source_name+suffix+'.anm']=dict(format='%s_%s%02d'if suffix else'%s_%s',prefix=prefix,action=source_name,ordinal=int(suffix)if suffix else None)
 for filename,construction in candidates.items():
  key=fast_hash(filename)
  if key not in members:continue
  identity=filename.upper()
  if identity not in hits:hits[identity]=dict(filename=filename,key=f'{key:08x}',construction=construction,source_identifier=source_name,source_evidence=evidence,members=members[key])
result=dict(bindings=sorted(hits.values(),key=lambda x:x['filename']),sources=source_rows,source_identifier_count=len(names),native_consumers=['82040BF4 %s_%s%02d_Left','82040C04 %s_%s%02d','82243234 stored action name + .anm','822AB038 native filename hash'],limits=['Only actual source identifiers and native prefix/ordinal formatting are tested.','Filename bindings are evidence; action integration and skin/motion parity require separate runtime verification.'])
(SOURCE/'animation-name-bindings.json').write_text(json.dumps(result,indent=2)+'\n');print('Bound',len(hits),'original animation filenames from',len(names),'source identifiers')
