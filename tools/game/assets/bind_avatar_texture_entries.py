"""Stage original JSM->typed texture-entry->DDT binding evidence, no runtime writes."""
import hashlib,json,re,struct
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/characters';OUT=SOURCE/'texture-entry-binding';OUT.mkdir(exist_ok=True)
GEN=ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default'
rdata_path=ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/82000400-.rdata.bin';rdata=rdata_path.read_bytes()
def literal(address):
 at=address-0x82000400;return rdata[at:rdata.index(0,at)].decode('ascii')
tests=[(5,[0x82045c5c,0x82045c64]),(6,[0x82045c6c]),(4,[0x82045c74]),(1,[0x8203dd6c]),(2,[0x82045c7c]),(3,[0x820397e4])]
assert [[literal(a)for a in addresses]for _,addresses in tests]==[['simple','glasses'],['crowd'],['lash'],['eye'],['cloth'],['hair']]
assert literal(0x8203d720)=='.'and literal(0x82039460)=='Normal'and literal(0x82045c84)=='Normal2'and literal(0x8202c464)=='.ddt'
functions={};wanted=['8223FCE8','8223FA48','8223F720','82243420','82243540','822437E0','822408F0','8223E380','822A4D20','822A6D58','82243B70','823DC190','823DCB18']
for path in GEN.glob('*recomp*.cpp'):
 text=path.read_text()
 for address in wanted:
  marker=f'DEFINE_REX_FUNC(sub_{address})';start=text.find(marker)
  if start<0:continue
  end=text.find('\nDEFINE_REX_FUNC',start+1);body=text[start:end if end>=0 else None];(OUT/f'{address}.cpp').write_text(body);functions[address]=dict(source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(body.encode()).hexdigest())
assert len(functions)==len(wanted)
manifest=json.loads((ROOT/'godot/assets/characters/components.json').read_text());art=json.loads((SOURCE/'avatar-materials.json').read_text());images={row['name'].lower():row for row in art['textures']};slots=[]
for skin in manifest['skins']:
 for material in skin['materials']:
  name=material['native_jtd'];kind=next((kind for kind,addresses in tests if any(literal(address)in name for address in addresses)),0);stem=name.split('.',1)[0]
  image=images.get(stem.lower())
  if image:assert filename_hash(stem+'.ddt')==int(image['key'],16)
  slots.append(dict(skin_id=skin['id'],skin_key=skin['source']['key'],model_path=skin['model_path'],slot=material['slot'],prepared_material_name=material['name'],native_jtd=name,native_entry_type=kind,native_initial_names={'4':name,'100':stem+'Normal','196':stem+'Normal2'if kind==0 else None},loader_base_name=stem,ddt_filename=stem+'.ddt',ddt_key=f'{filename_hash(stem+".ddt"):08x}',texture_source=image['source']if image else None,prepared_texture_path=material['base_texture_path'],source_skin=skin['source']))
report=dict(schema_version=2,source_rdata=dict(path=str(rdata_path.relative_to(ROOT)),sha256=hashlib.sha256(rdata).hexdigest()),functions=functions,constructor=dict(address='8223F720',type_offset=0,entry_size=304,tests=[dict(result=kind,case_sensitive_substrings=[dict(address=f'{a:08x}',value=literal(a))for a in addresses])for kind,addresses in tests],default_type=0,names={'4':'original JSM material-name string including extension','100':'replace first dot and remaining extension with Normal; missing dot appends Normal','196':'type0 only: replace first dot and extension with Normal2; other types leave prior field intact; null in slot report means no assignment proven by this constructor'},debug_override=dict(global_address='82577ad0',nonzero_behavior='Constructor first seeds names with smallColour/smallNormal; original+4 and computed+100 overwrite those fields, non-skin+196 may retain smallNormal;8223E380 may force smallColour texture loading',active_value_unbound=True),type_persistence='Type is assigned BEFORE selected component replacements; replacement does not reclassify it.'),pipeline=['8223FCE8 calls8223FA48 after geometry parse','8223FA48 reads little-endian original material-list count/tag3 strings and calls8223F720 in serialized order; appends304-byte entries to source asset+24 vector','82243420 copies304-byte entries into prepared selected model option+136 vector','82243540 applies selected exact-name replacement pairs to entry names+4/+100/+196; strips first dot in+4 before matching, type unchanged','822437E0 invokes822408F0 per entry','822408F0 loads+4/+100/+196 through8223E380 into pointers292/296/300','8223E380 strips first dot and passes resulting name to822A4D20','822A4D20 creates loader822A6D58, which appends literal.ddt from8202C464 to the requested basename','82243B70 uses retained entrytype0/2/3 for selected groupflags1/2/4; otherwise ASCII case-insensitive entry+4 target-name equality through823DC190'],slots=slots,replacement_rule=dict(case_sensitive=False,equality='823DC190 folds ASCII A..Z on both compared strings; retained source body',consumer='82243540',scope='Selected replacement vector is applied across all selected model entries, not restricted to the component carrying the replacement row.',rows='Component native_rows texture operands: fromName,toName[,third operand retained separately]. Native equality folds ASCII case; constructor substring classification remains separately case-sensitive through823DCB18; archive hash uppercases ASCII.'),limits=['Entry classification is an exact port of native string tests, not an inferred material-name heuristic.','The source entry type is not a complete material shading/transparency policy.','Original normal art entries may use currently unsupported pixel formats; no invented normal maps.','Ordered selected modifier collection/label expansion and actual shader operation execution remain separate contracts.','No runtime assets or source shader constants changed.'])
(OUT/'contract.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(f'Staged{len(slots)} typed source slots across{len(manifest["skins"])} prepared skins')
if __name__=='__main__':pass
