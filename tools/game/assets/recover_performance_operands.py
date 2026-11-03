"""Stage source operand bytes and package UI/encoding contracts; no runtime writes."""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-recovery/recompiled-handling';OUT=ROOT/'artifacts/juiced2-build/native-performance/operands';OUT.mkdir(parents=True,exist_ok=True)
sections=[]
for path in (SOURCE/'decoded-sections').glob('*.bin'):
 try:base=int(path.name[:8],16)
 except ValueError:continue
 sections.append((base,path,path.read_bytes()))
wanted=['821064C8','8210C558','821C7510','8210CFA0','821CB9D0','821CA168','821C9E28','821CAA18','821C9138','821CA528','8220EED0','8220F488','8221ACB8','822177D8','82217870','8221AF00','821C8608','8210AAA8','8210A968'];functions={};bodies={}
for path in (SOURCE/'generated/default').glob('*recomp*.cpp'):
 text=path.read_text()
 for name in wanted:
  marker=f'DEFINE_REX_FUNC(sub_{name})';start=text.find(marker)
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end if end>=0 else None];bodies[name]=body;(OUT/f'{name}.cpp').write_text(body);functions[name]=dict(source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(body.encode()).hexdigest())
assert len(functions)==len(wanted)
operands=[]
for name,body in bodies.items():
 registers={};history={}
 for line in body.splitlines():
  if not line.strip().startswith('// '):continue
  instruction=line.strip()[3:]
  match=re.fullmatch(r'(lis|li) r(\d+),(-?\d+)',instruction)
  if match:
   op,dest,value=match.groups();dest=int(dest);registers[dest]=(int(value)*(65536 if op=='lis'else 1))&0xffffffff;history[dest]=[instruction];continue
  match=re.fullmatch(r'(addi|ori) r(\d+),r(\d+),(-?\d+)',instruction)
  if match:
   op,dest,source,value=match.groups();dest,source,value=int(dest),int(source),int(value)
   if source in registers:registers[dest]=((registers[source]+value)if op=='addi'else registers[source]|value)&0xffffffff;history[dest]=history[source]+[instruction]
   else:registers.pop(dest,None)
   continue
  match=re.fullmatch(r'(lfs|lfd) f(\d+),(-?\d+)\(r(\d+)\)',instruction)
  if match:
   op,dest,offset,base=match.groups();base=int(base);offset=int(offset)
   if base in registers:
    address=(registers[base]+offset)&0xffffffff;size=4 if op=='lfs'else 8;found=next(((start,path,raw)for start,path,raw in sections if start<=address and address+size<=start+len(raw)),None)
    if found:
     start,path,raw=found;bits=raw[address-start:address-start+size];value=struct.unpack('>f'if size==4 else'>d',bits)[0];operands.append(dict(function=name,instruction=instruction,address_arithmetic=history[base]+[f'base+({offset})'],address=f'{address:08x}',section=str(path.relative_to(ROOT)),bits=bits.hex(),decoded_disc_value=value,kind='literal_read_only'if '.rdata.'in path.name else'mutable_global_disc_value_only',initialized_runtime_value_unbound='.rdata.'not in path.name))
   continue
  if instruction.startswith('bl '):
   for reg in range(13):registers.pop(reg,None)
  else:
   match=re.match(r'(?:lwz|lbz|lhz|ld|mr|add|subf|mulli|rlwinm|srawi|or|and|mflr|cntlzw)\.? r(\d+)',instruction)
   if match:registers.pop(int(match[1]),None)
assert any(item['function']=='821064C8'for item in operands)and any(item['function']=='8210C558'for item in operands)
source_catalog=json.loads((OUT.parent/'catalog.json').read_text())
price_rows=[]
for league,package in enumerate(source_catalog['packages']):
 raw=package['native_price_operands'];steps=package['steps']
 for category,name in enumerate(['Power','Handling','Weight']):
  low,high=raw[category*2:category*2+2];price_rows.append(dict(league=league,category=category,name=name,minimum=low,maximum=high,steps=steps,prices=[low+int((high-low)*item/steps)for item in range(steps)]))
report=dict(schema_version=1,functions=functions,operands=operands,price=dict(consumer='821CB9D0',anchor='821CBADC..821CBB6C',inputs={'248':'league','256':'zero-based item index','260':'category','264':'prototype/special fixed-price flag'},ordinary='low=PackData[league]+12+4*category;high=+24+4*category;steps=+8;integerTerm=trunc_signed_i32(((high-low)*item)/steps);price=trunc_i32(f32(f32(integerTerm)+f32(low))). Denominator is steps, NOTsteps−1.',rows=price_rows,prototype_fixed_by_league={'3':12000,'4':20000,'5':26000,'6':40000,'7':56000,'8':82000,'9':150000},special_default=12000,cost_modifier='CarModInfo+148 is not read in the ordinary price calculation block; do not silently multiply it into this quote.'),packed_install=dict(writer='8210CFA0',args={'r3':'car','r4':'category','r5':'league','r6':'item'},destination='car+4*(category+19): categories0/1/2→76/80/84',upper_clamp='item=min(item,PackData[league].steps−1)',remove='If item==−1,write0',installed='otherwise0x40000000|((league<<25)&0x3e000000)|(item&0x01ffffff)'),accept=dict(consumer='821CA168',anchor='821CA2E0..821CA420',wallet_guard='Checks wallet20>=state272 before selection accept',preview='state244==4 applies directly; state268nonzero writescar9644=league248; otherwise8210CFA0(category260,league248,item256)',queued_request='Othermode writes selectedcategory/item/league/price/NOSflag tosharedrequest824C1EAC,exceptWeightcategory2→824C1F70; purchaseconfirmationconsumer remains separate.'),availability=dict(minimum_league=dict(writer='821C8608 loc821C8DC0..821C8DE0',state_offset=304,helper='8210AAA8',inputs='nativecar116stockPower/120stockWeight; f32division; originalstrictthresholdintervalscan;fallback0'),maximum_league=dict(state_offset=308,helper='8210A968',inputs='nativecar124maxPower/128minWeight; originalthresholdscan;fallback9'),player_league='821C9E28: selectedleague248 mustnotexceedactiveprofileleague+4 beforeownership/unlock classification',ordinary_owned=dict(index='((league*3+category)*3)+item',word_base_offset=2112,scope='Activeplayerprofile; global acrosscars, not percarinventory'),prototype_owned='8221ACB8 profilebitmask2040/2044 category0..3',currently_installed='821C9E28 comparespackedleague/item andinstalledhighbits; exactcurrentselection→UIstate244=3',reinstall='OwnedselectioncanUIstate244=4;821CA168 state4 installsdirectly withoutqueuedpurchase/debit; not blanketfreeupgrades.',prototype_item='821C9138 loc821C9838..821C9888 sets264=1,item256=3 atmaxpotentialleaguewhenadvancedfromordinaryitem2; ordinarythreeitems0..2 distinctfromprototype3'),remove=dict(consumer='821C7510',meaning='Startsbyclearingcartselectedslot(index/price−1,aux0),thenrestoresbackedupcarfields. It is NOT package quote calculation.'),prototype_unlock=dict(consumer='8220EED0',bit='((selectedRow144+3)*4)+category140',category_range=[0,3],categories={'0':'Power','1':'Handling','2':'Weight','3':'NOS'},fourth_category_proof='821CAA18 loc821CAB44 reads car9644(NOSleague);loc821CAB8C passesr5=3 to8221ACB8, tyingfourthunlockcolumn toNOS.',initial_profile=dict(constructor='822177D8 clearswords2040/2044 then calls82217870;82217870 clears40bits frombase2040 andbyte2036=0',mask_words=[0,0],tokens=0,promotion='8221AF00 when league increases to3 sets2036=1 anddirty2048=1,unlessall40bitsalreadyunlocked',boundary='No first12preunlock found; UIselectedrow+3 addressesleague3..9,while8221ADF0 checksall40bits. Do not manufacture first12unlocked to reconcilethis.'),token='Successfulselectedunlock setsprofile2040/2044 bit anddecrementsbyte2036 by1; dirty/persistencefields separate.'),limits=['Address decoder follows local literal register construction, clears recognized load/ALU destinations and volatile GPRs at calls; it does not claim exhaustive control-flow/global-write analysis.','Mutable.data operands are disc values, not proven initialized runtime constants.','Exact native float operation ordering is retained in full source bodies; decoder values do not authorize algebraic reordering.','Price tables are ordinarynative catalog quantities, not automatic donor stock tune identity.','No runtime/core/frontend changes.'])
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Staged',len(operands),'addressedFPoperands;',len(price_rows),'league/categorypricelists')
