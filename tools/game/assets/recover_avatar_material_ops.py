"""Stage exact component texture-operation graphs without inventing shader math."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters';manifest=json.loads((ROOT/'godot/assets/characters/components.json').read_text());ops=[]
def parse(tokens):
 tokens=list(tokens);assert tokens.pop(0)=='modify'
 target=tokens.pop(0)
 if target=='label':target=dict(namespace='label',name=tokens.pop(0))
 else:target=dict(namespace='native_texture_or_group',name=target)
 node=dict(target=target);kind=tokens.pop(0);node['operation']=kind
 if kind=='label':node['label']=tokens.pop(0)
 elif kind=='hsv':
  parameters={}
  while tokens:
   name=tokens.pop(0);assert name in ['range','hue','saturation','value']
   count=2 if name=='range'else 1;values=[float(tokens.pop(0))for _ in range(count)];parameters[name]=values if count==2 else values[0]
  node['explicit_parameters']=parameters;node['native_parameters']={'hue':parameters.get('hue',0.0),'saturation':parameters.get('saturation',1.0),'value':parameters.get('value',1.0),'range':parameters.get('range',{'min':0.0,'max_global':'824cc044','disc_initial':360.0})};node['defaults_source']='8223A2A8 allocatesmodifier296bytes:offset272hue0,276sat1,280value1,284rangeMin0,288rangeMaxfrom824cc044;explicitnumbersparsedwithoutscaleorclamp'
 elif kind in ['alpha','mattalpha']:
  assert tokens and tokens[0]=='modify';node['input']=parse(tokens);tokens=[]
 else:raise ValueError(kind)
 assert not tokens
 return node
for component in manifest['components']:
 rows=[(i,row)for i,row in enumerate(component['native_rows'])if row[0]=='modify']
 if not rows:continue
 ops.append(dict(component_id=component['id'],category=component['category'],name=component['name'],source=component['source'],operations=[dict(row_index=index,native_row=row,graph=parse(row))for index,row in rows]))
source_functions={};wanted=['82239018','8223A2A8','82243540','82244CE8','82243B70','822445E0','82250CD0','82250818','822D3C00']
for path in (ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default').glob('*.cpp'):
 text=path.read_text()
 for function in wanted:
  token=f'DEFINE_REX_FUNC(sub_{function})'
  if token not in text:continue
  start=text.index(token);end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end];(OUT/f'attribute-consumer-{function}.cpp').write_text(body);source_functions[function]=hashlib.sha256(body.encode()).hexdigest()
assert len(source_functions)==len(wanted)
rdata=(ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin').read_bytes();fxl_path=ROOT/'artifacts/juiced2-build/world-uv/Juiced2.fxl';fxl=fxl_path.read_bytes();assert fxl.find(b'TextureCombine')==0x363e00
report=dict(source_functions=source_functions,components=ops,presets=[dict(id=p['id'],native_components=p['native_components'],native_attributes=p['native_attributes'])for p in manifest['native_presets']['presets']],pipeline=['82239018 gathersselectedcomponentmodifiers','82243540 bindsreplacement/materialtargets','82244CE8 schedulescombinedsourceassembly','82243B70/822445E0 constructsoperationnodes','82250CD0 schedulesdynamictexturetask','82250818 selectsoriginaltechniqueandbindstextures/vectors then822D3C00draws'],effect=dict(file='Juiced2.fxl',sha256=hashlib.sha256(fxl).hexdigest(),name='TextureCombine',name_offset=0x363e00,techniques=['Copy','Blend','SAdd','HSV','Alpha','MattAlpha'],technique_table='824af8d0 sixnamepointers;82250818 usesnode+140 toindex',texture_uniforms=['TextureA','TextureB'],value_uniform=dict(name='vValue',node_offset=156,count=3,source='82250818 passesnode+156 tovectoruniformsetter'),range_uniform=dict(name='vRange',node_offset=144,count=2,source='82250818 passesnode+144 tovectoruniformsetter'),shader_metadata_offsets=[0xe4504,0xe4518,0xe4530]),attributes=dict(skeleton=['SKELETON_TALL','SKELETON_FAT','SKELETON_STOCKY'],skeleton_contract='native-body-scales.json',other_raw_attributes=['SKIN_DARK','SKIN_RED','SKIN_YELLOW','HAIR_BLONDE','HAIR_BLACK','HAIR_BROWN','HAIR_RED','PROFILE_NERVOUS'],other_raw_attribute_execution='No downstream consumer binding proven yet; retainedpresets are not evidence of RGBtint orgeometryexecution.'),limits=['TextureCombineHSV/Alpha/MattAlpha pixelmath isdecodedandfixture-checked separatelyintexturecombine/contract.json; samplertransfer/targetquantization remainunbound.','Label and texturegroup expansion require sourcebindings; do not applymodifiers toallmaterials by guessedsubstring.','Selectedcomponent operation graphs are distinctfrom8legacyrawskin/hair/profileattributes.','No runtimeassets changed bythisreport.'])
report['target_binding']=dict(parser='8223A2A8',group_flags={'allskintextures':1,'allclothtextures':2,'allhairtextures':4},consumer='82243B70',matching='Modifierflagsbit1 matchesnativetextureentrytype0(skin);bit2matchestype2(cloth);bit4matchestype3(hair);otherwiseASCIIcase-insensitive823DC190texture-namecomparison;labeltargetsresolvedseparately',limits=['Preparedmaterialtexturesmustcarryoriginaltype/namebinding; no guessedsubstring/globaltint.'])
report['shader_contract']='texturecombine/contract.json (generatedbydecode_texturecombine.py→texturecombine_fixtures.py→build_texturecombine_contract.py)'
report['numeric_parsing']=dict(consumer='8223A2A8',hue_offset=272,saturation_offset=276,value_offset=280,range_offsets=[284,288],arithmetic='822C15B0parsesfloatanddirectstfs;noHSVscaleorclampintheparser;originalGPUtechniqueownsremainingmath.')
(OUT/'native-material-operations.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Staged',len(ops),'components;',sum(len(o['operations'])for o in ops),'exactoriginalmaterialoperationgraphs')
