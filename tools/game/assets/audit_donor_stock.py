"""Stage accepted30 stock input qualifications and primary-backed corrections only."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/donor-stock-audit';OUT.mkdir(parents=True,exist_ok=True)
roster=json.loads((ROOT/'artifacts/juiced2-recovery/initial-roster.json').read_text())['cars'];content_path=ROOT/'data/juiced2/content.json';content=json.loads(content_path.read_text());cars={x['id']:x for x in content['cars']}
notes={
'GT4_HOND0018':'Different generation: acceptedEK1998, matched2001EP3 2.0L. OfficialHondaEK9 proves1595cc185PS; equipment-dependent1040..1090kg. Exactequipment/year specification still needs bounded choice; do not label197bhp/1998cc/1170kg authoritative.',
'GT4_MINI0001':'PeriodCooperS163PS reference plausibly matches output/mass; rawsourcecalls itTurbo5MT, whileR53is supercharged6MT. Manufacturer exactyear/weightconvention still pending.',
'FOCUS_SVT':'Existingidentity-specific originalJuiced2handling bound; distinguish nativegame tune1256kg from manufacturercurbmass. ExistingFordprimarysource retained elsewhere; not newly reverified here.',
'MCLA_VP_VW_GOLF_83':'Market/engine ambiguity: accepted1983GTI, matched90HP Golf generation. US1.8GTI vsEU112PS must not be conflated; exact donor market unverified.',
'GT4_RE__0001':'Accepted2002ClioRS; matched182HP variant is later trim. Stockoutput/mass requires172vs182 model-year audit.',
'GT4_HOND0019':'AcceptedJDMDC2TypeR1998; currentAcura196HP proxy differsJDM200PS. Mass/equipment/gear spec still unverified.',
'GT4_MAZD0012':'Accepted1989NA;90HP reference is not originalJDM120PS trim. Exactmarket and curbmass need primary table.',
'GT4_NISS0056':'Accepted1999S15SpecR6MT vs matched1994S14/200SX200HP5MT. Nissan1999primary table proves250PS/1240kg/1998cc/RWD; correction source-ready.',
'GT4_HOND0030':'JDM2003S2000 reference output250PS plausible; market-specificweight/year still not independently primary-verified in this pass.',
'GT4_MAZD0007':'Mazda2002primary confirmsSpiritRTypeA280PS5MT2seats. Existing2616cc is doubled rotary equivalence, not physical1308cc; mass1300kg not independently verified.',
'GT4_TOYT0006':'Existing1993RZJDMsource is same-family earlier-year proxy to1997. Current266.87bhp derives torque rather than advertised280PS; exact stock power convention needs correction.',
'GT4_NISS0004':'Accepted2003Z33; matched300HP output is laterrev. Need2003market-specific280PS/287SAE table, no silent substitution.',
'GT4_SUBR0017':'AcceptedGFwagonVersionVI1999; matchedSTisedan/6MT reference not exactwagon. Output/mass/gearbox likely different; primary audit pending.',
'GT4_MITS0001':'Confirmedinvalid320kg upstreamraw705lbs(320kg), not parserunitloss. OriginalMitsubishiJan2003manual: GSRGH-CT9A/SJGFZ classification0751410kg;076sunroof1430kg. Selected non-sunroofGSR1410 correction staged.',
'GT4_NISS0021':'Accepted2002VspecIINur; existing2000VspecII reference and1635kg are not exact. Nissanprimary2000VspecII1560kg/206kW;2002MspecNur1580kg is differenttrim. ExactNurweight pending, no false interchange.',
'GT4_LNCA0005':'Accepted1991IntegraleEvoluzioneAWD; rawmatch1993Delta2.0FWD184bhp is differentmodel. Layout already correctedAWD; stockpower/mass remain proxy.',
'GT4_BMW_0010':'E46M3samegeneration343PS plausible;1470kg DIN vsEU convention unverified. Exactcoupe/manual/equipment must be qualified.',
'MC3_VP_ELISE_04':'Donorfilename04 suggests2004 but acceptedyearunknown; current710kg/Rover122HP proxy not established2004Toyota111R. Keep unknownvariant, no exactidentity claim.',
'MCLA_VP_AUD_R8_08':'Confirmedgeneration/engine mismatch:2008R8V8vs matched5.2V10525PS. Audi primary saysinitial4.2V8420PS/quattro; exactcurbmass/market pending.',
'MCLA_VP_LAM_GALLARDO_06':'Spyder2006samebody reference;520HP units SAEvsPS unclear, curbmass convention pending primary.',
'MUSTANG_68':'1968donor uses1965-68 289271HP proxy; exact1968engine option unknown. Do not present representative as exactstock.',
'MCLA_VP_CHV_CAMAROSS_69':'1969RSSS uses1967family295HP350reference; exact350/396option andgross/net power not source-verified.',
'MCLA_VP_BUK_GRANDNATIONAL_87':'AcceptedGNX, matched1988ordinaryRegal170HP is incompatible. Buick/GMprimary historical pages located; exactGNXrated276HP andmass must be retained only after source extraction.',
'MCLA_VP_CHV_CORVETTEZ06_07':'2007Z06matched2008sameLS7variant;506HPvsSAE505 unitrounding needs primary confirmation;1418kg convention pending.',
'GT4_DODG0005':'Existingidentity-specific originalJuiced2Viperhandling; manufacturerpresssource2005coupe is not exact2003roadster. Distinguish nativegame tune from donorphysicalspec.',
'GT4_ASMT0005':'2003show/debutDB9vs2004productionreference;450HPunit and1710kg transmission/equipment pending.',
'MCLA_VP_SLN_S7_06':'Accepted2006S7 but priorreference2000-04NA542bhp. Saleenprimary distinguishesNA550HP and2005TT750HP; donortrim requires explicit source identity before selectingTT.',
'LIGHTNING_SVT':'Confirmedwrongenginefamily:regularF150228bhp versusSVT2002380SAEhp. FordRacingofficialhistory confirms2001-04380HP; exactweight/reference pending.',
'F100_1956':'Accepted1956F100 unspecifiedengine; current223six133grossHP/1275kg representative adaptation, exactGLBengine/trim cannot be proved from name.',
'MC3_VP_ESCALADE_03':'Acceptedfilename2003 vsrawgeneration2000;345bhp6.0RWD plausible2003 reference but AWD/RWD trim and2428kg unverified.'}
assert len(notes)==30
rows=[]
for row in roster:
 code=row['code'];h=cars[code]['handling']
 rows.append({'car_id':code,'accepted_identity':row['source_name'],'accepted_year':row.get('year'),'prior_match':row['match'],'current_stock':{key:h.get(key)for key in ['mass','peak_bhp','peak_torque','engine_size','layout','body_length','body_width','body_height']},'qualification':'native_game_tune_not_manufacturer_spec'if code in ['FOCUS_SVT','GT4_DODG0005']else'primary_correction_ready'if code=='GT4_MITS0001'else'proxy_or_exact_variant_unverified','findings':notes[code],'all_fields_manufacturer_verified':False})
pdf=OUT/'sources/mitsubishi-evo-viii-technical.pdf';assert pdf.read_bytes().startswith(b'%PDF')
text=OUT/'sources/mitsubishi-evo-viii-technical.txt';t=text.read_text();assert '075 to 076'in t and 'Total 1 370 1 380 1 390 1 1400 1 410 1 430'in t
source={'url':'https://www.tuningevo.club/manuals/EVO_8/2003_Lancer_Evo_8_Technical_Infomation_Manual.pdf','retrieved_on':'2026-11-03','publisher':'Mitsubishi Motors Corporation','document_date':'January2003','distribution':'third-party mirror of manufacturer-authored manual','path':str(pdf.relative_to(ROOT)),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'anchors':['PDFpage73 OutlineSpecification:SNDFZ/SJDFZ/SJGFZ classification035..058/059..074/075..076','PDFpage75 weighttable:0751410kg,0761430kg;076includesS(sunroof)','PDFpage4:GH-CT9A/SJGFZGSR4WD6MT'],'limitation':'Mirrored/translated manual includes OCR/translation defects inothercells; selectedGSRweight cross-checked with manufacturerbrochure indexedtable and exactclassification binding.'}
corrections={'schema_version':1,'input_content_sha256':hashlib.sha256(content_path.read_bytes()).hexdigest(),'corrections':[{'car_id':'GT4_MITS0001','field':'handling.mass','old':320,'new':1410,'units':'kg','identity':'2003JapanGSRGH-CT9A-SJGFZ nonsunroofclassification075','source':source,'quality_flags':['upstream_secondary_curbweight_corrupt','matched_secondary_5MT_not_GSR6MT','manufacturer_authored_primary_correction'],'not_changed':'Otherhandlingfields,meshgeometry,nativeCarModInfo and counterpartstock/max remain untouched.'}],'publication':'STAGEDONLY; canonicalmergeddataset publication requires coordination'}
staged=copy.deepcopy(content);next(x for x in staged['cars']if x['id']=='GT4_MITS0001')['handling']['mass']=1410
for name,data in [('stock-identity-audit-v1.json',{'schema_version':1,'cars':rows,'counts':{'audited_qualifications':30,'all_stock_fields_primary_verified':0,'staged_mass_corrections':1},'limits':['This is a complete30-row identity/input qualification audit, not30 primary-spec certifications.','High-impact mismatches are held, not silently tuned to gameplay targets.','No runtime content,sourceprofiles,normalizedarchive orGLBs modified.']}),('stock-corrections-v1.json',corrections),('content-evo-mass-corrected-STAGED.json',staged)]:
 (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
print('Staged30qualifications,Evo320→1410kg primarycorrection; no production writes')
