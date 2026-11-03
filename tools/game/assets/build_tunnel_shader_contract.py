"""Retain proven tunnel shader equations, uploads, fixtures and explicit limits."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/tunnel-shaders'
programs=json.loads((OUT/'programs.json').read_text());fixtures=json.loads((OUT/'fixtures.json').read_text());assert fixtures['cases']==15000
rdata=(ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin').read_bytes()
assert struct.unpack_from('>I',rdata,0x8204d090-0x82000400)[0]==0x3b808081
assert struct.unpack_from('>I',rdata,0x82048638+40-0x82000400)[0]==0x822d4340
wanted=['8219C3D0','8219C568','8219B9C8','8228D128','822CF670','822CF638','822CF718','822CF6E0','822D4340','822D67D0','822CDEA8','822FEBF8','822FD9A8','822E5BD8','822E5C28','822E5AE8'];functions={}
for p in (ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default').glob('*.cpp'):
 text=p.read_text()
 for address in wanted:
  start=text.find(f'DEFINE_REX_FUNC(sub_{address})')
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end];(OUT/f'{address}.cpp').write_text(body);functions[address]=dict(sha256=hashlib.sha256(body.encode()).hexdigest(),source=str(p.relative_to(ROOT)))
assert len(functions)==len(wanted)
constants={}
for address,expected in [(0x8201a8e4,.5),(0x8204cb10,1.)]:
 value=struct.unpack_from('>f',rdata,address-0x82000400)[0];assert value==expected
 constants[hex(address)]=dict(value=value,bits=rdata[address-0x82000400:address-0x82000400+4].hex())
for address,label in [(0x8202b448,b'g_expParams1'),(0x8202b458,b'g_expParams2')]:
 assert rdata[address-0x82000400:].split(b'\0',1)[0]==label
atmospheres=[]
from jfs_hash import filename_hash
names={filename_hash(name):name for name in ['profile.atm','profile22.atm','split_screen.atm','DNA_LAB.atm']}
for path in sorted((OUT/'lighting').glob('tunnel-*.bin')):
 raw=path.read_bytes();fields={};rows=[]
 for line in raw.decode('ascii').splitlines():
  parts=line.split()
  if not parts or parts[0].startswith((';','[')):continue
  try:values=[float(v) for v in parts[1:]]
  except ValueError:continue
  if values:rows.append(dict(name=parts[0],values=values));fields[parts[0]]=values
 key=int(path.stem.rsplit('-',1)[1],16)
 item=dict(member=path.name,native_key=f'{key:08x}',verified_filename=names.get(key),sha256=hashlib.sha256(raw).hexdigest(),rows=rows,effective_numeric_fields=fields)
 required=['SceneManualExposure','SceneMinBloom','SceneMaxBloom','Contrast','Saturation']
 if all(k in fields for k in required):
  exposure,low,high,contrast,saturation=[fields[k][0] for k in required];slope=(high-1)/(high-low)
  item['candidate_uniforms_from_explicit_fields']=dict(g_expParams1=[exposure,low,slope,1-slope*low],g_expParams2=[saturation,contrast,.5*(1-contrast),contrast*exposure],precision='Real-number equation illustration; native instructions round f32 and use fused negative multiply-add. Not an active-phase/default claim.')
 atmospheres.append(item)
report=dict(schema_version=2,source=programs['source'],techniques=programs['techniques'],program_bindings=[dict(id=p['id'],kind=p['kind'],record=p['record'],sha256=p['sha256'],bindings=p['bindings'],literal_constants=p['literal_constants'])for p in programs['programs']],
 equations=fixtures['equations'],grade_channels=dict(g_expParams1=dict(register=17,x='unusedbythesepixelprograms',y='minimuminputtomax(R,G,B,y)',z='maxRGBdenominatorslope',w='denominatorbias'),g_expParams2=dict(register=15,x='saturationfactorabout0.3300000131*sumRGB',y='unusedbythesepixelprograms',z='post-saturationadditivebias',w='post-saturationmultiplicativegain')),
 vertex=dict(simpleGradient='VS617:clip=MVP*POSITION;TEXCOORD0=inputUV.xy.Noangularpositionprojection.',luminousScroll='VS586:TEXCOORD0=inputUV.xy+g_Focus_Time.w*(uScroll,vScroll)',backLightScroll='VS58:sameUVformula;uScrollc49/vScrollc48vsVS586uScrollc48/vScrollc49'),
 palette_upload=dict(consumer='8219B9C8',cached_handles='8219C568 cachescolour1/2/3through822CFCA0→8228D128atcontroller196/200/204',packed_input='822CF670 queuesARGBvalue;822CF638dispatchesmaterialvirtual40',virtual_binding='82048638+40→822D4340',conversion='ARGB8→RGBAf32 usingliteral8204D090bits3b808081(f32 1/255);NOsRGBtransfer',uniform_write='822D67D0memcopiesfloatvectortoeffectuniforms;nomath/gammaconversion',example=dict(native_rgb=[5,0,6],uploaded_rgb=[5/255,0,6/255]),limits='Scriptcolour→packedARGBchannelstoremustremainconsistentwithoriginalscenecontroller; paletteuniformconversionitselfisproven.'),
 global_upload=dict(initializer='822CDEA8 resolves original names8202B448/8202B458 to singleton handles236/240',writer='822FEBF8 uploads via822CF278',state_mapping={'76':'Contrast','80':'Saturation','180':'SceneManualExposure','184':'SceneMinBloom','188':'SceneMaxBloom'},atmosphere_copy='822FD9A8 copies atmosphere1000/1004/1012/1016/1020 to those state fields; optional scene override may replace them',equations={'g_expParams1':['E','Bmin','(Bmax-1)/(Bmax-Bmin)','1-z*Bmin'],'g_expParams2':['S','C','0.5*(1-C)','C*E']},arithmetic='Native fsubs/fdivs/fmuls round f32; bias paths use fnmsubs fused arithmetic. No denominator guard or clamp in this writer.',constants=constants),
 atmospheres=atmospheres,
 functions=functions,verification=fixtures,
 remaining=dict(exposure_globals='Namedglobalwriter and atmosphere field mapping are proven; active creator/main phase atmosphere and later camera overrides remain unbound. Explicit fixture values are not defaults.',texture_transfer='EquationsconsumeGPU-sampledRGBA; originalsamplergamma/filter/addressingandtextureformattransferremainseparate.',time_units='Shaderusesg_Focus_Time.w; writer/unitsnotyetbound.DonotsilentlyequatewithGodotTIMEseconds.',blend='Luminous_2b/2a/2shareVS586/PS660butdifferinserializedpassstate; originalstateenum/blendselectionnotyetdecoded.OpaquePBRisnotprovenequivalent.',luminous_effect='Effectname38a3b0known;itsdynamicVS/PSselectorrecordsneedseparateparser.Notclaimeddecodedbythestaticscrollprograms.',normal_boundary='Original111normal/windingbatchissource-correct,butnativefacecreasepersisted; separatefrontendGodotarrayprobeexcludeslargeimportnormalerrors.'),
 limits=['No runtimeassetschangedbythesehelpers.','No guessedexposure,angularpaletteweights,opacitymaterialorRGBtintsubstitute.','Float32CPUfixturesarenotahardwareGPUprecisionclaim.'])
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Stagedoriginaltunnelshadercontract;15kfixtures;named global upload and nine original atmosphere members')
