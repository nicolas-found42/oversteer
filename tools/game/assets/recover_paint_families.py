"""Stage original paint family/prices and symbolic 72-byte material writer.

The small evaluator supports only the bounded recovered820F8F78 writer. RGB/HSV
calls remain named source operations rather than an invented color conversion.
"""
import hashlib,json,re,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/presentation';SECTIONS=ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections';GEN=ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default'
functions=['821C48C0','821C4F00','821C5A68','821C5E20','821C6280','821C6650','821C83E8','822191A0','82218FD0','820EFCD0','820FAC50','820FA060','820F8F78','820F9428','8207AC80','8207ADC0','820F94D8','820FA388','820F9BA0','82108108','821083E8','82108438','82108580'];texts={}
for path in GEN.glob('*.cpp'):
 text=path.read_text()
 for function in functions:
  token=f'DEFINE_REX_FUNC(sub_{function})'
  if token not in text:continue
  start=text.index(token);end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end];texts[function]=body;(OUT/f'paint-consumer-{function}.cpp').write_text(body)
assert len(texts)==len(functions)
rdata=(SECTIONS/'82000400-.rdata.bin').read_bytes();data=(SECTIONS/'824A0000-.data.bin').read_bytes()
def constant(address):
 if 0x82000400<=address<0x82000400+len(rdata):return struct.unpack_from('>f',rdata,address-0x82000400)[0]
 if 0x824A0000<=address<0x824A0000+len(data):return dict(native_global=f'{address:08x}',disc_initial=struct.unpack_from('>f',data,address-0x824A0000)[0],runtime_value_unbound=True)
 raise ValueError(hex(address))
def op(kind,a,b):
 if isinstance(a,(int,float))and isinstance(b,(int,float)):return struct.unpack('>f',struct.pack('>f',a-b if kind=='subtract'else a*b))[0]
 return {kind:[a,b]}
def evaluate(family,channel):
 body=texts['820F8F78'];lines=body.splitlines();labels={m.group(1):i for i,line in enumerate(lines)if(m:=re.match(r'(loc_\w+):',line))};switch={int(k):v for k,v in re.findall(r'case (\d+):\s*goto (loc_\w+);',body)}
 r={i:0 for i in range(32)};r.update({1:0x10000,3:0x20000,4:family,5:channel,6:0x30000});f={};mem={0x30000:'input.r',0x30004:'input.g',0x30008:'input.b'};mem.update({0x20000+i:f'previous.material[{i}]'for i in range(0,72,4)});pc=0;comparison=0
 def addr(operand):
  m=re.fullmatch(r'(-?\d+)\(r(\d+)\)',operand);return (r[int(m[2])]+int(m[1]))&0xffffffff
 def read(a):return mem[a]if a in mem else constant(a)
 for _ in range(1000):
  if pc>=len(lines):break
  line=lines[pc];pc+=1
  if not line.strip().startswith('// '):continue
  ins=line.strip()[3:];parts=ins.split(' ',1);code=parts[0];args=parts[1].split(',')if len(parts)>1 else[]
  if code in ['mflr','stfd','lfd','stw','stwu','mtctr','rlwinm','lwzx']:continue
  if code=='lis':r[int(args[0][1:])]=(int(args[1])<<16)&0xffffffff
  elif code=='addi':r[int(args[0][1:])]=(r[int(args[1][1:])]+int(args[2]))&0xffffffff
  elif code=='mr':r[int(args[0][1:])]=r[int(args[1][1:])]
  elif code=='lfs':f[int(args[0][1:])]=read(addr(args[1]))
  elif code=='stfs':mem[addr(args[1])]=f[int(args[0][1:])]
  elif code in ['fmuls','fsubs']:f[int(args[0][1:])]=op('multiply'if code=='fmuls'else'subtract',f[int(args[1][1:])],f[int(args[2][1:])])
  elif code in ['cmpwi','cmplwi']:
   value=r[int(args[1][1:])];comparison=value-int(args[2])
  elif code=='bctr':pc=labels[switch[family-1]]
  elif code in ['beq','bgt','bne']:
   take=comparison==0 if code=='beq'else comparison>0 if code=='bgt'else comparison!=0
   if take:pc=labels['loc_'+args[-1][2:].upper()]
  elif code=='b':
   target=int(args[0],16)
   if target==0x823ddcac:break
   pc=labels[f'loc_{target:08X}']
  elif code=='bl':
   target=int(args[0],16)
   if target==0x823ddc5c:continue
   assert target in [0x8207ac80,0x8207adc0],ins
   vector=[read(r[3]+i*4)for i in range(3)]
   for i in range(3):mem[r[4]+4*i]={'source_call':f'{target:08x}','inputs':vector,'component':i}
  elif code!='Switch':raise ValueError(ins)
 else:raise AssertionError('Writer did not terminate')
 return {str(i):mem[0x20000+i]for i in range(4,72,4)if 0x20000+i in mem}
assert all(f'// li r21,{price}'in texts['821C4F00']for price in [3000,5000,12000,7500,20000])
assert '// stw r30,20(r31)'in texts['822191A0']
families=[]
for enum,name,price in [(0,'gloss',3000),(1,'metallic',5000),(2,'flake',12000),(3,'pearl',12000),(4,'matt',7500),(5,'thinfilm',20000)]:
 families.append(dict(id=name,native_enum=enum,price=price,material_state_by_channel={str(channel):evaluate(enum,channel)for channel in ({'pearl':[0,1],'flake':[0,3]}.get(name,[0]))}))
bindings={'4':'colour2','16':'cFleckColor','28':'colour1','40':'twoToneExp','44':'minReflect','48':'maxReflect','52':'fFlakie','56':'fFleckPower','60':'fFleckLocality','64':'bTryThinFilm','68':'fFilmThickness'}
for address,name in [(0x82037f78,'colour1'),(0x82037f80,'colour2'),(0x82037f88,'cFleckColor'),(0x82037f94,'fFilmThickness'),(0x82037fa4,'bTryThinFilm'),(0x82037fb4,'fFleckLocality'),(0x82037fc4,'fFleckPower'),(0x82037fd0,'fFlakie'),(0x82037fd8,'maxReflect'),(0x82037fe4,'minReflect'),(0x82037ff0,'twoToneExp')]:
 offset=address-0x82000400;assert rdata[offset:rdata.index(0,offset)].decode()==name
report=dict(schema_version=1,uniform_bindings=bindings,uniform_binding_proof='820FA388 firsthandle set passes originalrdata names→820F9BA0 argument-to-handle offsets→820FA06072byte-to-uniform writes; alternate per-layer names remain separate',families=families,source_functions={key:hashlib.sha256(value.encode()).hexdigest()for key,value in texts.items()},material_record=dict(size=72,type_offset=0,base_rgb_offsets=[4,8,12],secondary_rgb_offsets=[16,20,24],third_rgb_offsets=[28,32,36],scalar_offsets=list(range(40,72,4)),scalar_semantics='Exact original uniform names bound separately; not glTF metallic/roughness equivalents'),purchase=dict(price_consumers=['821C4F00 selecteditem+268 family tag','821C5A68 price display','821C5E20 color-page initialization'],cart_consumer='821C5E20 writes cart82581670 slot0 +4=selected0,+8=family price,+12=0; flags+680=1,+564=1',checkout='821C4F00 reads wallet+20; subtracts821C83E8 sum of selected cart slot prices; calls822191A0 new-balance setter; no extra separate RGB fee in this paint entry',preview='821C6650 converts packed source8bitRGB by1/255 and calls820F8F78 then820FAC50',persistence='820EFCD0 copies all72bytes type+17floats'),limits=['Symbolic writer preserves original RGB/HSV calls rather than substituting unverified color-space arithmetic.','Native globals retain disc-initial values and unknown runtime binding separately; they are not fixed shader constants.','Six native families have no chrome alias. Legacy authored chrome migration is a separate compatibility decision.','Catalog432/797 source colors do not prove active user palette selection; source local records retained independently.','Material coefficients are source data; exact Godot shader execution/BRDF translation remains separate.'])
# Preserve exact shipped stock color records separately from interactive-family rules.
header=(ROOT/'artifacts/juiced2-recovery/scripts.jfshdr').read_bytes();archive=(ROOT/'artifacts/juiced2-recovery/scripts.jfs').read_bytes();catalogs=[]
for index,key in [(432,0x62cc08f9),(797,0xb770ec39)]:
 actual,offset,packed,size,*_=struct.unpack_from('>6I',header,4+24*index);assert actual==key
 raw=archive[offset:offset+packed];raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size
 start,cursor=struct.unpack_from('>2I',raw,4);rows=[]
 for fmt in raw[start:cursor].split(b'\3')[0].decode().strip().splitlines():
  row=[]
  for kind in fmt:
   value=struct.unpack_from('>f'if kind=='f'else'>i',raw,cursor)[0];cursor+=4
   if kind=='s':value=raw[value:raw.index(0,value)].decode()
   row.append(value)
  rows.append(row)
 assert cursor==len(raw);catalogs.append(dict(member=index,key=f'{key:08x}',sha256=hashlib.sha256(raw).hexdigest(),native_rows=rows))
report['stock_color_catalogs']=catalogs
layout_path=ROOT/'artifacts/juiced2-build/ui/layout-fields/ui-0f393c40.json';layout=json.loads(layout_path.read_text());images=json.loads((ROOT/'godot/assets/ui/native/manifest.json').read_text());items=[]
for index,row in enumerate(layout['fields']):
 if row[0]!='AddNewTexturedItem':continue
 label=row[1];key=f'{filename_hash("Textures"+chr(92)+label+".ddt"):08x}';matches=[r for r in images if r['key']==key];assert matches
 items.append(dict(id=row[5],native_label=label,caption_id=row[6],texture_key=key,texture_paths=[r['path']for r in matches],native_row=row,row_index=index))
assert [i['id']for i in items]==['gloss','metallic','matt','pearl','flake','thinfilm','stopper']
report['style_ui']=dict(layout='ui-0f393c40',sha256=hashlib.sha256(layout_path.read_bytes()).hexdigest(),items=items,order='Exact sourcecarouselorder; differsfromnativeenumorder')
report['record_fields']=[dict(name='native_type',offset=0,type='u32_be'),dict(name='base_rgb',offset=4,type='vec3_f32_be',proof='BaseColour82037c2c→table824b8550→821083E8 readsrecord+4 then820F8F78 channel0'),dict(name='fleck_rgb',offset=16,type='vec3_f32_be'),dict(name='secondary_rgb',offset=28,type='vec3_f32_be')]+[dict(name=name,offset=offset,type='f32_be')for offset,name in [(40,'two_tone_exp'),(44,'min_reflect'),(48,'max_reflect'),(52,'flakie'),(56,'fleck_power'),(60,'fleck_locality'),(64,'try_thin_film'),(68,'film_thickness')]]
report['record_fields'][-2]['proof']='820F8F78 storesfloat0/1 withstfs;820FA060 usesfloatsetter822CF8E8 fornativebTryThinFilm, notu32/bool'
assert next(f for f in families if f['id']=='thinfilm')['material_state_by_channel']['0']['64']==1.0
assert next(f for f in families if f['id']=='matt')['material_state_by_channel']['0']['44']==0.0
assert next(f for f in families if f['id']=='gloss')['material_state_by_channel']['0']['52']==0.0
report['scalar_controls']=[dict(family='pearl',channel=2,uniform='twoToneExp',offset=40,slope_address='8257d19c',slope=constant(0x8257d19c),intercept_address='824ce600',intercept=constant(0x824ce600)),dict(family='flake',channel=4,uniform='fFlakie',offset=52,slope_address='8201158c',slope=constant(0x8201158c),intercept_address=f'{0x82020000-80-22860:08x}',intercept=constant(0x82020000-80-22860)),dict(family='flake',channel=5,uniform='fFleckPower',offset=56,slope_address='8201ffb0',slope=constant(0x8201ffb0),intercept_address='8204cb08',intercept=constant(0x8204cb08)),dict(family='thinfilm',channel=6,uniform='fFilmThickness',offset=68,slope_address='824cbf10',slope=constant(0x824cbf10),intercept_address='824b6d74',intercept=constant(0x824b6d74))]
startup_path=OUT/'pearl-balance-startup/contract.json'
if startup_path.exists():
 startup=json.loads(startup_path.read_text());assert startup['span']['after_constructor']==1.0 and startup['bias']['decoded_initial']==0.0
 pearl=report['scalar_controls'][0];pearl['startup_binding']=dict(source=str(startup_path.relative_to(ROOT)),sha256=hashlib.sha256(startup_path.read_bytes()).hexdigest(),constructor='82474BB0',constructor_table_entry='824A022C',startup_span=1.0,startup_bias=0.0,default_mapping='f32(input*1+0)',limits='Staticstartupwriterproof,notruntimecapture;laterindirectwritesnotexcluded.')
report['scalar_control_arithmetic']='820F9428 writesfloat32nativeFMADD(input,slope,intercept); noadditionalclampinthissetter. UIinputboundsareseparate.'
report['color_workflow']=dict(consumer='821C5E20',state_field='controller+36',pearl='baseRGB channel0 then secondaryRGB channel1 then scalar channel2 then one12000cartentry',flake='baseRGB channel0 then fleckRGB channel3 then scalar channel4 then scalar channel5 then one12000cartentry',thinfilm='baseRGB channel0 then scalar channel6 then one20000cartentry',limits=['Channel ordering is source state-machine evidence; native localized caption binding retained separately.','Scalar channel functions820F9428 and820F94D8 are source consumer leads; runtime globals in their arithmetic remain unbound.'])
(OUT/'native-paint-families.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Staged6native families/prices;8symbolic source color-channel material states')
