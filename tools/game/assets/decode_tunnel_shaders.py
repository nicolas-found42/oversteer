"""Stage original tunnel effect bindings and Xenos VS/PS disassembly."""
import hashlib,json,struct
from pathlib import Path
from decode_texturecombine import ROOT,data,groups,alu,fmt_operand,fmt_scalar

OUT=ROOT/'artifacts/juiced2-build/tunnel-shaders';OUT.mkdir(exist_ok=True)
effects={'simpleGradient':(0x396624,[0x396a80,0x396bb4]),'luminousScroll':(0x38be50,[0x38c3b0,0x38c544,0x38c6d8,0x38c86c]),'backLightScroll':(0x3652e4,[0x3657c0,0x36596c]),'luminous':(0x38a3b0,[])}
programs=[];techniques=[]
def decode(name,kind,index):
 record=groups[0 if kind=='vertex'else 1][index];start=record['offset'];raw=data[start:start+record['size']];base=record['metadata_size'];header=struct.unpack_from('>I',raw,0x18)[0];offset,size=struct.unpack_from('>2I',raw,header);assert offset+size==record['code_size'];code=raw[base+offset:base+offset+size];words=struct.unpack('>'+str(size//4)+'I',code);cf=[];instructions={};lines=[];stop=False
 for pair in range(len(words)//3):
  a,b,c=words[3*pair:3*pair+3]
  for half,(w0,w1)in enumerate([(a,b&65535),((b>>16)|(c<<16),c>>16)]):
   opcode=(w1>>12)&15;entry=dict(index=pair*2+half,opcode=opcode,address=w0&4095,count=(w0>>12)&7,sequence=(w0>>16)&4095,predicate_condition=bool(w1&(1<<9)));cf.append(entry)
   if opcode in [1,2,5,6]:
    lines.append(f"CF{entry['index']} op{opcode}:")
    for j in range(entry['count']):
     index=entry['address']+j;fetch=bool((entry['sequence']>>(j*2))&1)
     if fetch:
      fw=words[index*3:index*3+3];op=fw[0]&31
      ins=dict(index=index,fetch=True,fetch_opcode=op,raw=[f'{w:08x}'for w in fw],dest=(fw[0]>>12)&63,source=(fw[0]>>5)&63,fetch_constant=(fw[0]>>20)&31,dest_swizzle=[(fw[1]>>(k*3))&7 for k in range(4)])
      if op==0:ins.update(vertex_format=(fw[1]>>16)&63,vertex_stride=fw[2]&255,vertex_offset_words=((fw[2]>>8)&0x7fffff),fetch_constant_select=(fw[0]>>25)&3)
      else:ins.update(texture_index=(fw[0]>>20)&31,source_swizzle=[(fw[0]>>(26+k*2))&3 for k in range(3)])
      lines.append(f' {index:02d} FETCH '+str(ins))
     else:
      ins=alu(words,index);src=', '.join(fmt_operand(o)for o in ins['sources']);dst=('EXPORT'if ins['export']else'r')+str(ins['vector_dest'])+'.'+''.join('xyzw'[k]for k in range(4)if ins['vector_mask']>>k&1);line=f" {index:02d} {ins['vector_opcode']}{'_sat'if ins['vector_clamp']else''} {dst}, {src}"
      if ins['scalar_mask']or ins['scalar_opcode']!='retain_prev':line+=f" | {ins['scalar_opcode']} r{ins['scalar_dest']}."+''.join('xyzw'[k]for k in range(4)if ins['scalar_mask']>>k&1)+', '+fmt_scalar(ins)
      lines.append(line)
     instructions[index]=ins
   else:
    lines.append(f'CF{entry["index"]} op{opcode} raw{w0:08x}/{w1:04x}')
    assert opcode in [0,12],entry
   if opcode in [2,6]:stop=True;break
  if stop:break
 ctbase=0x28;_,_,_,count,at,_,_=struct.unpack_from('>7I',raw,ctbase);bindings=[]
 for i in range(count):
  no,rs,ri,rc,res,ty,de=struct.unpack_from('>I4H2I',raw,ctbase+at+i*20);no+=ctbase;bindings.append(dict(name=raw[no:raw.index(0,no)].decode(),register_set=rs,register_index=ri,register_count=rc))
 literal={str(256-offset//16+i):list(struct.unpack_from('>4f',raw,base+i*16))for i in range(offset//16)}
 ident=name+'-'+kind+'-'+str(record['index']);(OUT/(ident+'.shader')).write_bytes(raw);(OUT/(ident+'.ucode')).write_bytes(code);(OUT/(ident+'.asm.txt')).write_text('\n'.join(lines)+'\n')
 return dict(id=ident,kind=kind,record=record,sha256=hashlib.sha256(raw).hexdigest(),ucode_sha256=hashlib.sha256(code).hexdigest(),bindings=bindings,literal_constants=literal,control_flow=cf,instructions=list(instructions.values()))
for effect,(address,descriptors)in effects.items():
 assert data[address:address+len(effect)]==effect.encode()
 for descriptor in descriptors:
  name=data[descriptor:data.index(0,descriptor)].decode();annotation_count,annotation_bytes=struct.unpack_from('>2I',data,descriptor+40);p=descriptor+48+annotation_bytes
  passes=struct.unpack_from('>I',data,p)[0]
  if passes==0:
   techniques.append(dict(effect=effect,effect_name_offset=address,name=name,descriptor_offset=descriptor,pass_count=0));continue
  assert passes==1 and data[p+4:p+7]==b'P0\0'
  vertex_index=struct.unpack_from('>I',data,p+60)[0];pixel_index=struct.unpack_from('>I',data,p+108)[0]
  techniques.append(dict(effect=effect,effect_name_offset=address,name=name,descriptor_offset=descriptor,pass_offset=p,vertex_index=vertex_index,pixel_index=pixel_index,annotation_raw=data[descriptor+48:p].hex()))
  for kind,index in [('vertex',vertex_index),('pixel',pixel_index)]:
   ident=f'{effect}-{name}-{kind}-{index}'
   if not any(row['id']==ident for row in programs):programs.append(decode(effect+'-'+name,kind,index))
report=dict(source=dict(path='artifacts/juiced2-build/world-uv/Juiced2.fxl',sha256=hashlib.sha256(data).hexdigest()),techniques=techniques,programs=programs,limits=['Source-onlydisassembly;effecttechniquechoiceandsampler/targetstatebindingsremainseparate.','FullFXLpassrender-stateformatnotyetdecoded;rawtechniqueannotationsretained.','Math/fixturesnotyetindependentlyverified.'])
(OUT/'programs.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print([(t['effect'],t['name'],t.get('vertex_index'),t.get('pixel_index'))for t in techniques])
