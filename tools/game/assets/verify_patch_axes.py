"""Execute the straight-line recovered patch scalar arithmetic on control fixtures."""
import json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/collision';rdata=(ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin').read_bytes()
def execute(path,registers,floats,memory):
 def f32(v):return struct.unpack('>f',struct.pack('>f',v))[0]
 for line in path.read_text().splitlines():
  if not line.strip().startswith('//'):continue
  ins=line.strip()[3:].strip();op,_,args=ins.partition(' ');a=args.split(',')
  if op=='lis':registers[a[0]]=(int(a[1])*65536)&0xffffffff
  elif op=='mr':registers[a[0]]=registers.get(a[1],0)
  elif op=='addi':registers[a[0]]=(registers.get(a[1],0)+int(a[2]))&0xffffffff
  elif op in['lfs','stfs']:
   match=re.fullmatch(r'(-?\d+)\((r\d+)\)',a[1]);address=(registers.get(match[2],0)+int(match[1]))&0xffffffff
   if op=='stfs':memory[address]=f32(floats[a[0]])
   elif address in memory:floats[a[0]]=memory[address]
   else:floats[a[0]]=struct.unpack_from('>f',rdata,address-0x82000400)[0]
  elif op in['fmuls','fadds','fsubs','fdivs']:
   x,y=floats[a[1]],floats[a[2]];floats[a[0]]=f32({'fmuls':lambda:x*y,'fadds':lambda:x+y,'fsubs':lambda:x-y,'fdivs':lambda:x/y}[op]())
  elif op in['fmadds','fmsubs','fnmsubs','fnmadds']:
   x,y,z=[floats[v]for v in a[1:]];value=x*y+z if op in['fmadds','fnmadds']else x*y-z;floats[a[0]]=f32(-value if op.startswith('fn')else value)
  elif op in['fmr','frsp']:floats[a[0]]=floats[a[1]]
  elif op=='fneg':floats[a[0]]=-floats[a[1]]
  elif op.startswith('f')or op.startswith('lfd'):raise ValueError('unhandled floating instruction '+ins)
 return registers,floats,memory
# Native 8230A7D0 materializes four original rows of four Vec4 controls.
memory={0x100000+16*k+4*axis:float(k+100*axis)for k in range(16)for axis in range(3)}
execute(SOURCE/'native-8230A918.cpp.txt',{'r3':0x200000,'r4':0x100000},{},memory);rows=[]
for u,v in[(0,0),(1,0),(0,1),(1,1),(.25,.75)]:
 local=dict(memory);execute(SOURCE/'native-8230AAA0.cpp.txt',{'r3':0x200000,'r6':0x300000},{'f1':u,'f2':v},local);rows.append(dict(u=u,v=v,position=[local[0x300000+4*i]for i in range(3)]))
report=dict(native_transpose='8230A918',native_evaluator='8230AAA0',fixture='original control[k]=[k,100+k,200+k]',results=rows,limits=['Straight-line recovered scalar arithmetic interpreted; fixture uses exact endpoints and is not a full PPC runtime.'])
(SOURCE/'native-patch-axis-fixture.json').write_text(json.dumps(report,indent=2)+'\n');print(rows)
