"""Extract six original FXL TextureCombine pixel programs and bounded Xenos ALU.

Bitfield decoding follows retained ReXGlue/Xenia ucode.h; no native runtime or
unproven PowerPC provider is used. The raw records remain available for checking.
"""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/world-uv/Juiced2.fxl';OUT=ROOT/'artifacts/juiced2-build/characters/texturecombine';OUT.mkdir(exist_ok=True);inventory=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());source_row=next(r for r in inventory['files']if r['path'].lower()=='juiced2.fxl')
with open(inventory['iso'],'rb')as iso:iso.seek(source_row['offset']);original=iso.read(source_row['size'])
if SOURCE.exists():assert SOURCE.read_bytes()==original
else:SOURCE.parent.mkdir(parents=True,exist_ok=True);SOURCE.write_bytes(original)
data=original;SDK=ROOT/'artifacts/juiced2-recovery/rexglue-sdk';ucode=(SDK/'src/graphics/format/ucode.cpp').read_text();tables={}
for key,count in [('Scalar',64),('Vector',32)]:
 text=ucode.split(f'kAlu{key}OpcodeInfos[{count}] = {{',1)[1].split('\n};',1)[0];tables[key]=re.findall(r'\{"([^"]+)"',text);assert len(tables[key])==count
p=0;groups=[]
for group in ['vertex','pixel']:
 count=struct.unpack_from('>I',data,p)[0];p+=4;records=[]
 for index in range(count):
  size=struct.unpack_from('>I',data,p)[0];p+=4;magic,meta,code=struct.unpack_from('>3I',data,p);assert magic==0x102a1101 if group=='vertex'else magic==0x102a1100;assert meta+code==size;records.append(dict(index=index,offset=p,size=size,metadata_size=meta,code_size=code));p+=size
 groups.append(records)
def operand(a,b,c,i):
 shift=(3-i)*8;rawreg=(c>>shift)&255;temp=(c>>(32-i))&1;swizzle=(b>>shift)&255;return dict(raw_index=rawreg,raw_swizzle=swizzle,register='r'if temp else'c',index=rawreg&63 if temp else rawreg,absolute=bool(rawreg&128)if temp else bool(a&128),relative=bool(rawreg&64)if temp else False,negate=bool((b>>(27-i))&1),swizzle=[((swizzle>>(2*j))+j)&3 for j in range(4)])
def alu(words,index):
 a,b,c=words[index*3:index*3+3];return dict(index=index,raw=[f'{w:08x}'for w in[a,b,c]],vector_opcode=tables['Vector'][(c>>24)&31],scalar_opcode=tables['Scalar'][(a>>26)&63],vector_dest=a&63,scalar_dest=(a>>8)&63,vector_mask=(a>>16)&15,scalar_mask=(a>>20)&15,vector_clamp=bool(a&(1<<24)),scalar_clamp=bool(a&(1<<25)),export=bool(a&(1<<15)),export_zero=bool(a&(1<<14)),predicated=bool(b&(1<<28)),predicate_condition=bool(b&(1<<27)),sources=[operand(a,b,c,i)for i in range(1,4)])
def fmt_operand(o,scalar=False):
 sw=o['swizzle'];name=o['register']+str(o['index'])+'.'+''.join('xyzw'[j]for j in(sw[3:4]+sw[:1]if scalar else sw));return('-'if o['negate']else'')+('abs('+name+')'if o['absolute']else name)
def fmt_scalar(ins):
 o=ins['sources'][2]
 if ins['scalar_opcode']not in['mulsc','addsc','subsc']:return fmt_operand(o,True)
 a,_,c=[int(w,16)for w in ins['raw']];index=((a>>26)&1)|(((c>>29)&1)<<1)|(o['raw_swizzle']&0x3c);prefix='-'if o['negate']else'';return prefix+'c'+str(o['raw_index'])+'.'+'xyzw'[o['swizzle'][3]]+', '+prefix+'r'+str(index)+'.'+'xyzw'[o['swizzle'][0]]
reports=[]
for order,name in enumerate(['Copy','Blend','SAdd','HSV','Alpha','MattAlpha']):
 record=groups[1][0x48+order];start=record['offset'];raw=data[start:start+record['size']];base=record['metadata_size'];header_offset=struct.unpack_from('>I',raw,0x18)[0];ucode_offset,ucode_size=struct.unpack_from('>2I',raw,header_offset);assert ucode_offset+ucode_size==record['code_size'];code=raw[base+ucode_offset:base+ucode_offset+ucode_size];assert len(code)==ucode_size and len(code)%12==0;words=struct.unpack('>'+str(len(code)//4)+'I',code);cf=[];instructions={};lines=[];stop=False
 for pair in range(len(words)//3):
  a,b,c=words[pair*3:pair*3+3]
  for half,(w0,w1)in enumerate([(a,b&65535),((b>>16)|(c<<16),c>>16)]):
   opcode=(w1>>12)&15;entry=dict(index=pair*2+half,opcode=opcode,address=w0&4095,count=(w0>>12)&7,sequence=(w0>>16)&4095,predicate_condition=bool(w1&(1<<9)));cf.append(entry)
   if opcode in [1,2,5,6]:
    lines.append(f"CF{entry['index']} op{opcode} predicate{entry['predicate_condition']}:")
    for j in range(entry['count']):
     index=entry['address']+j;fetch=bool((entry['sequence']>>(j*2))&1)
     if fetch:fw=words[index*3:index*3+3];ins=dict(index=index,fetch=True,raw=[f'{w:08x}'for w in fw],dest=(fw[0]>>12)&63,texture_index=(fw[0]>>20)&31,dest_swizzle=[(fw[1]>>(k*3))&7 for k in range(4)]);lines.append(f' {index:02d} FETCH '+str(ins['raw']))
     else:
      ins=alu(words,index);prefix='p'+str(int(ins['predicate_condition']))+' 'if ins['predicated']else'';src=', '.join(fmt_operand(o)for o in ins['sources']);dst=('oC'if ins['export']else'r')+str(ins['vector_dest'])+'.'+''.join('xyzw'[k]for k in range(4)if ins['vector_mask']>>k&1);line=f" {index:02d} {prefix}{ins['vector_opcode']}{'_sat'if ins['vector_clamp']else''} {dst}, {src}"
      if ins['scalar_mask']or ins['scalar_opcode']!='retain_prev':line+=f" | {ins['scalar_opcode']}{'_sat'if ins['scalar_clamp']else''} r{ins['scalar_dest']}."+''.join('xyzw'[k]for k in range(4)if ins['scalar_mask']>>k&1)+', '+fmt_scalar(ins)
      lines.append(line)
     instructions[index]=ins
   else:assert opcode in [0,12],entry
   if opcode in[2,6]:stop=True;break
  if stop:break
 # Technique descriptor's actual shader index links name to exact pixel record.
 descriptor=0x364098+order*0x14c;assert data[descriptor:descriptor+len(name)]==name.encode();assert struct.unpack_from('>I',data,descriptor+0xec)[0]==record['index']
 ctbase=0x28;_,_,_,ctcount,ctoffset,_,_=struct.unpack_from('>7I',raw,ctbase);bindings=[]
 for ci in range(ctcount):
  no,rs,ri,rc,res,ty,de=struct.unpack_from('>I4H2I',raw,ctbase+ctoffset+ci*20);no+=ctbase;bindings.append(dict(name=raw[no:raw.index(0,no)].decode(),register_set=rs,register_index=ri,register_count=rc))
 if ucode_offset:
  literal_descriptor=struct.unpack_from('>I',raw,struct.unpack_from('>I',raw,0x14)[0]+20)[0];assert(literal_descriptor&65535)*4==ucode_offset;assert(literal_descriptor>>16)-256==256-ucode_offset//16
 (OUT/(name+'.shader')).write_bytes(raw);(OUT/(name+'.ucode')).write_bytes(code);(OUT/(name+'.asm.txt')).write_text('\n'.join(lines)+'\n');reports.append(dict(name=name,constant_bindings=bindings,record=record,technique_descriptor_offset=descriptor,pixel_index_field_offset=descriptor+0xec,sha256=hashlib.sha256(raw).hexdigest(),ucode_sha256=hashlib.sha256(code).hexdigest(),ucode_file_offset=start+base+ucode_offset,literal_constants={str(256-ucode_offset//16+i):list(struct.unpack_from('>4f',raw,base+i*16))for i in range(ucode_offset//16)},control_flow=cf,instructions=list(instructions.values())))
report=dict(source=dict(iso_member=source_row['path'],iso_offset=source_row['offset'],iso_size=source_row['size'],path=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),vertex_shaders=len(groups[0]),pixel_shaders=len(groups[1])),programs=reports,decoder_source=dict(ucode_header_sha256=hashlib.sha256((SDK/'include/rex/graphics/format/ucode.h').read_bytes()).hexdigest(),opcode_table_sha256=hashlib.sha256(ucode.encode()).hexdigest()),limits=['Direct bitfield disassembly; instruction math and pixel fixtures need independent execution/checks.','Technique→pixelrecord bound byoriginal descriptor indices, not inferred from adjacent program order.','No runtimeassets changed.'])
(OUT/'programs.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Extracted6exactTextureCombinepixelprograms; originalshaderindices72..77')
