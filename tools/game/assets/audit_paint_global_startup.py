"""Retain bounded direct-reference evidence; absence is not a no-indirect-write proof."""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'artifacts/juiced2-recovery/recompiled-handling'
OUT=ROOT/'artifacts/juiced2-build/presentation/paint-global-startup';OUT.mkdir(parents=True,exist_ok=True)
data_path=SOURCE/'decoded-sections/824A0000-.data.bin';data=data_path.read_bytes()
addresses=[0x8257797c,0x82577980,0x82577984,0x82577988]
refs={address:[] for address in addresses};functions={};files=[]
for path in sorted((SOURCE/'generated/default').glob('*recomp*.cpp')):
 text=path.read_text();files.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(text.encode()).hexdigest()))
 registers={};function=None;function_start=0;lines=text.splitlines()
 for index,line in enumerate(lines):
  match=re.match(r'DEFINE_REX_FUNC\((\w+)\)',line)
  if match:function=match[1];registers={};function_start=index
  match=re.search(r'// (lis|li) r(\d+),(-?\d+)',line)
  if match:
   op,reg,value=match.groups();registers[int(reg)]=(int(value)*(65536 if op=='lis' else 1))&0xffffffff;continue
  match=re.search(r'// (addi|ori) r(\d+),r(\d+),(-?\d+)',line)
  if match:
   op,dest,source,value=match.groups();dest,source,value=int(dest),int(source),int(value)
   if source in registers:registers[dest]=((registers[source]+value)if op=='addi'else(registers[source]|value))&0xffffffff
   else:registers.pop(dest,None)
   continue
  match=re.search(r'// (\w+) ([rf]\d+),(-?\d+)\(r(\d+)\)',line)
  if match:
   op,operand,offset,base=match.groups();base=int(base)
   if base in registers:
    address=(registers[base]+int(offset))&0xffffffff
    if address in refs:
     refs[address].append(dict(function=function,path=str(path.relative_to(ROOT)),line=index+1,instruction=line.strip(),candidate=True))
     end=next((i for i in range(index+1,len(lines))if lines[i].startswith('DEFINE_REX_FUNC')),len(lines));functions[function]='\n'.join(lines[function_start:end])+'\n'
   # A load overwrites its destination GPR; never carry the old address through it.
   if op.startswith('l')and operand.startswith('r'):registers.pop(int(operand[1:]),None)
  elif re.search(r'// (mr|lwzx|add|subf|rlwinm|or|and|mflr) r\d+',line):
   dest=int(re.search(r' r(\d+)',line)[1]);registers.pop(dest,None)
# Require the known reader while treating broad linear-scan candidates as leads only.
for address in addresses:
 assert any(ref['function']=='sub_820F8F78'and 'lfs 'in ref['instruction']for ref in refs[address])
for name,body in functions.items():(OUT/f'{name}.cpp').write_text(body)
report=dict(schema_version=1,globals=[dict(address=f'{address:08x}',disc_bits=data[address-0x824a0000:address-0x824a0000+4].hex(),disc_value=struct.unpack_from('>f',data,address-0x824a0000)[0],references=refs[address],initialized_value=None,status='No nonzero initializer proven; do not substitute an invented default.')for address in addresses],sections=[dict(path=str(data_path.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest())],scanned_files=files,reader_bodies={name:hashlib.sha256(body.encode()).hexdigest()for name,body in functions.items()},limits=['Static instruction-comment scan, not runtime observation.','Tracks only local lis/li/addi/ori address construction and conservative GPR load invalidation; branches, interprocedural pointers, register-indexed stores and copies are not fully analyzed.','Reference candidates require source reading; absence of a direct writer does not exclude indirect writes.','Pearl span has a separately proven CRT writer; this report does not extend that proof to unrelated globals.'])
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({item['address']:len(item['references'])for item in report['globals']}))
