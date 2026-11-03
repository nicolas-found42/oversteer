"""Retain bounded direct references to mutable native performance coefficients."""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-recovery/recompiled-handling';OUT=ROOT/'artifacts/juiced2-build/native-performance/operands';targets={0x824ac1a0:'human engine/tyre coefficient',0x824cbe70:'front tyre coefficient',0x824cc05c:'handling step coefficient'};references={a:[]for a in targets};files=[]
for path in sorted((SOURCE/'generated/default').glob('*recomp*.cpp')):
 text=path.read_text();files.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(text.encode()).hexdigest()));registers={};history={};name=None
 for index,line in enumerate(text.splitlines()):
  match=re.match(r'DEFINE_REX_FUNC\((\w+)\)',line)
  if match:name=match[1];registers={}
  if not line.strip().startswith('// '):continue
  instruction=line.strip()[3:]
  match=re.fullmatch(r'(lis|li) r(\d+),(-?\d+)',instruction)
  if match:
   op,reg,value=match.groups();registers[int(reg)]=(int(value)*(65536 if op=='lis'else 1))&0xffffffff;history[int(reg)]=[instruction];continue
  match=re.fullmatch(r'(addi|ori) r(\d+),r(\d+),(-?\d+)',instruction)
  if match:
   op,dest,source,value=match.groups();dest,source,value=int(dest),int(source),int(value)
   if source in registers:registers[dest]=((registers[source]+value)if op=='addi'else registers[source]|value)&0xffffffff;history[dest]=history[source]+[instruction]
   else:registers.pop(dest,None)
   continue
  match=re.fullmatch(r'(\w+) ([rf]\d+),(-?\d+)\(r(\d+)\)',instruction)
  if match:
   op,operand,offset,reg=match.groups();reg=int(reg)
   if reg in registers:
    address=(registers[reg]+int(offset))&0xffffffff
    if address in targets:references[address].append(dict(function=name,path=str(path.relative_to(ROOT)),line=index+1,instruction=instruction,address_arithmetic=history[reg]+[f'base+({offset})'],is_store=op.startswith('st')))
   if op.startswith('l')and operand.startswith('r'):registers.pop(int(operand[1:]),None)
  if instruction.startswith('bl '):
   for reg in range(13):registers.pop(reg,None)
  else:
   match=re.match(r'(?:mr|add|subf|mulli|rlwinm|srawi|or|and|mflr|cntlzw)\.? r(\d+)',instruction)
   if match:registers.pop(int(match[1]),None)
data_path=SOURCE/'decoded-sections/824A0000-.data.bin';raw=data_path.read_bytes();report=dict(schema_version=1,globals=[dict(address=f'{address:08x}',role=role,bits=raw[address-0x824a0000:address-0x824a0000+4].hex(),disc_value=struct.unpack_from('>f',raw,address-0x824a0000)[0],references=references[address],startup_writer_proven=False,initialized_value=None)for address,role in targets.items()],section=dict(path=str(data_path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest()),scanned_files=files,limits=['Bounded local direct-address scan, not complete control-flow/interprocedural/indirect store analysis.','Disc-initial mutable values are not claimed immutable or proven poststartup defaults.','No constructor writer found by this bounded scan; do not infer absence of every later indirect write.','Stock human modifiers may already be present in preparedHandling; do not multiply again without base/source accounting.'])
(OUT/'mutable-global-audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print({f'{address:08x}':dict(references=len(refs),stores=sum(r['is_store']for r in refs))for address,refs in references.items()})
