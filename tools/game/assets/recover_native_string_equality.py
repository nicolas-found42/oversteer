"""Verify original823DC190 ASCII equality and preserve superseded claim explicitly."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters/string-equality-proof';OUT.mkdir(exist_ok=True)
source=ROOT/'artifacts/juiced2-recovery/recompiled-handling';text_path=source/'decoded-sections/82070000-.text.bin';text=text_path.read_bytes();functions={}
for path in (source/'generated/default').glob('*recomp*.cpp'):
 body=path.read_text()
 for address in ['823DC190','823DCB18','82239FC0','82243540','82243B70']:
  marker=f'DEFINE_REX_FUNC(sub_{address})';at=body.find(marker)
  if at<0:continue
  end=body.find('\nDEFINE_REX_FUNC',at+1);value=body[at:end if end>=0 else None];(OUT/f'{address}.cpp').write_text(value);functions[address]=dict(source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(value.encode()).hexdigest())
assert len(functions)==5
instructions=[]
for address,expected,reg in [(0x823dc1c0,0x60c60020,6),(0x823dc1d4,0x60a50020,5)]:
 actual=struct.unpack_from('>I',text,address-0x82070000)[0];assert actual==expected
 instructions.append(dict(address=f'{address:08x}',word=f'{actual:08x}',opcode=actual>>26,RS=(actual>>21)&31,RA=(actual>>16)&31,immediate=actual&65535,meaning=f'ori r{reg},r{reg},32'))
def native(a,b):
 a=a+b'\0';b=b+b'\0';i=0
 while True:
  x,y=a[i],b[i];difference=x-y
  if y==0:return difference
  if difference==0:i+=1;continue
  if 65<=y<=90:y|=32
  if 65<=x<=90:x|=32
  difference=x-y
  if difference:return difference
  i+=1
def folded(a):return bytes(c|32 if 65<=c<=90 else c for c in a)
cases=0
for a in range(1,128):
 for b in range(1,128):
  left,right=bytes([a]),bytes([b]);assert(native(left,right)==0)==(folded(left)==folded(right));cases+=1
examples=[]
for left,right in [(b'Combats',b'combats'),(b'dancer01',b'Dancer01'),(b'eye',b'eyes'),(b'eyes',b'eye'),(b'',b''),(b'',b'A'),(b'A',b'')]:
 result=native(left,right);assert(result==0)==(folded(left)==folded(right));examples.append(dict(left=left.decode(),right=right.decode(),result=result,equal=result==0));cases+=1
report=dict(schema_version=1,correction=dict(superseded_claim='823DC190 is case-sensitive strcmp',verdict='Contradicted by original PPC and translated source',history='Earlier source contracts/messages used the wrong description. Those generated contracts were regenerated before an immutable old-file backup existed; this audit retains the exact superseded claim, not a fabricated original-file hash.'),semantics='Return0 iff both NUL-terminated strings are equal under ASCII A..Z folding. No prefix match. Non-ASCII byte behavior is not Unicode casefold.',original_code=dict(path=str(text_path.relative_to(ROOT)),section_sha256=hashlib.sha256(text).hexdigest(),function_start='823dc190',function_end_exclusive='823dc1e4',function_bytes_sha256=hashlib.sha256(text[0x823dc190-0x82070000:0x823dc1e4-0x82070000]).hexdigest(),checked_instructions=instructions),functions=functions,caller_branches=dict(component='82239FC0:cmpwi r3,0;beq8223A054 returns1-based component index',replacement='82243540:cmpwi r3,0;bne skipsreplacement;zero executescopy',modifier='82243B70:cmpwi r3,0;bne82243F20 skipsnamedoperation;zero matches'),verification=dict(cases=cases,all_equalities_match_independent_ASCII_fold=True,examples=examples),separate_semantics='823DCB18 substring function performs bytewise matching without uppercase folding; constructor substring classification remains case-sensitive.',limits=['Static source/machinebyte proof, not PowerPC runtime execution.','Filename hashing has its own independently recovered ASCII uppercase algorithm; equality correction does not change hash inputs.'])
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Verified',cases,'ASCII/termination cases +two originaloriwords')
