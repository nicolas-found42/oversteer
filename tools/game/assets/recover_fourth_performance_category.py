"""Stage versioned original fourth-column identity/bounds; preserve earlier contract."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-recovery/recompiled-handling';OUT=ROOT/'artifacts/juiced2-build/native-performance/fourth-category-v2';OUT.mkdir(parents=True,exist_ok=True)
wanted=['821CAA18','8221ACB8','8220E8A0','8220EED0','821CA168','821CA448','82109860','8210AB20','8210D0E8','8210D988','821C9138','821944D0','82194718'];functions={}
for path in (SOURCE/'generated/default').glob('*recomp*.cpp'):
 text=path.read_text()
 for name in wanted:
  marker=f'DEFINE_REX_FUNC(sub_{name})';start=text.find(marker)
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end if end>=0 else None];(OUT/f'{name}.cpp').write_text(body);functions[name]=dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(body.encode()).hexdigest())
assert len(functions)==len(wanted)
layout_path=ROOT/'artifacts/juiced2-build/ui/layout-fields/ui-949143e7.json';layout=json.loads(layout_path.read_text());fields=layout['fields'];texts=[];current=None
for row in fields:
 if row[0]=='BeginText':current=dict(name=row[1],rectangle=row[2:]);texts.append(current)
 elif row[0]=='EndText':current=None
 elif current is not None and row[0]=='Caption':current['local_caption']=row[1]
columns=[next(text for text in texts if text.get('local_caption')==number)for number in [38,39,40,41]]
text_path=ROOT/'artifacts/juiced2-build/ui/text-catalog/ui-2381f47b.txt';english=text_path.read_text();labels={}
for line in english.splitlines():
 if ' = 'in line:
  key,value=line.split(' = ',1);labels[int(key)]=value
assert [labels[number]for number in [38,39,40,41]]==['POWER','HANDLING','WEIGHT','EXTREME NITRO']
rdata_path=SOURCE/'decoded-sections/82000400-.rdata.bin';rdata=rdata_path.read_bytes();address=(((-32254)<<16)-22300)&0xffffffff;assert address==0x8201a8e4;bits=rdata[address-0x82000400:address-0x82000400+4];assert struct.unpack('>f',bits)[0]==.5
report=dict(schema_version=2,supersedes='Earlier abbreviated category3=NOS label; precise original English label is EXTREME NITRO. Earlier operand contracts remain retained and are not silently rewritten.',identity=dict(column_index=3,caption_id=41,english_label=labels[41],layout=dict(path=str(layout_path.relative_to(ROOT)),sha256=hashlib.sha256(layout_path.read_bytes()).hexdigest(),bank=layout['bank'],member=layout['source_member'],columns=columns),english_table=dict(path=str(text_path.relative_to(ROOT)),sha256=hashlib.sha256(text_path.read_bytes()).hexdigest(),title=labels[44],columns={str(number):labels[number]for number in [38,39,40,41]})),query=dict(caller='821CAA18',anchor='821CAB44..821CAB98',callee='8221ACB8',args={'r3':'active player profile','r4':'league row r30','r5':3},meaning='Tests prototype unlock bit league*4+3 inprofile2040/2044,with explicit global unlock-all branch incallee',installed_row_match='Immediately preceding821CAB44 loads selectedcar9644 andcompareswithleague r30; profile-session override usesprofile0 instead.'),installed_value=dict(field_offset=9644,type='u32/integer league identifier; notpackedPower/Handling/Weight andnotfloatcapacity',constructor='82109860 writes0',preview_setter='821CA168 state244==4 and268!=0 writesstateleague248 toselectedcar9644',remove='821CA448 whenstate268!=0 writes0',ai_setter='8210D988 whenincomingr7flagsetwritesgeneratedleague r26 to9644',ui_bounds='Prototype unlock rows selection144+3→league3..9; performancecardnavigation league248 isbounded by source stock/maxpotentialrange304..308 andspecialNOS transitionatleague3; notlegacy0..3',getter='8210AB20 returns9644 outsideexplicitprofile-session override',serialization='821944D0 copies9644→serialized9684;82194718 restores9684→9644'),separate_capacity=dict(field_offset=9640,type='f32 materialized NOS-capacity input',constructor=dict(function='82109860',value=.5,literal_address=f'{address:08x}',raw_bits=bits.hex()),consumer='8210D0E8 reads9640 andcomputescapacity throughits ownscalar/sentinelbranch; itdoesnot directlyread9644',relation='No9644→9640 conversion or9644→physicscapacity/torquemultiplier proven bythistrace. Do notreplace9640 withleague orport3tiercapacityfromthiscolumn.'),limits=['Englishcaption/localCaptiongeometry are original recovered resources; active locale/table-selection consumer remains separate.','Prototype unlock choice andperformancecardpurchase/license flow are separate state machines; categorylabel isnotproof of casheligibility,boostforce,refillpolicy orcapacityrange.','Installedleague0default/removal isknown; no universalvalidationrange orlower-tier0..3schema inferred fromallpossiblewriters.','No runtime assets, DLLs, core/frontend files or priorversionedcontracts modified.'],functions=functions)
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Staged original EXTREME NITRO column3;9644league/9640capacityboundary')
