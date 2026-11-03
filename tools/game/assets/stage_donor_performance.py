"""Stage explicit relative native package endpoints for the accepted donor roster.

This is an adaptation catalog, never a replacement for donor authoritative base
physics or proof that a similar source vehicle shares an exact native tune.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'artifacts/juiced2-build/native-performance';OUT.mkdir(parents=True,exist_ok=True)
# Each choice is deliberate; absent native donors use a documented counterpart.
MAPPINGS=[
 ('GT4_HOND0018','CIVTYPER','Honda Civic Type R family; exact generation/variant is not established here.'),
 ('GT4_MINI0001','MINI','Mini Cooper S model family; relative package adaptation only.'),
 ('FOCUS_SVT','FOCUS_SVT','Same named SVT Focus; exact base tune has separate identity evidence, not inferred from this catalog.'),
 ('MCLA_VP_VW_GOLF_83','GOLF_GTI','Golf GTI family across generations; 1983 donor is not the native modern variant.'),
 ('GT4_RE__0001','MEGANE','Renault front-drive performance hatch counterpart; Clio V6 is a different layout and is deliberately not used.'),
 ('GT4_HOND0019','ac_integra','Integra performance family; original trim/market identity is not established here.'),
 ('GT4_MAZD0012','MX5','MX-5 family across generations; donor NA is not asserted to be native MX5 variant.'),
 ('GT4_NISS0056','Silvia_S15','Silvia S15 model family; ratio-only package adaptation.'),
 ('GT4_HOND0030','S2000','Honda S2000 model family; ratio-only package adaptation.'),
 ('GT4_MAZD0007','RX7','Mazda RX-7 family; Spirit R trim identity not established by this row.'),
 ('GT4_TOYT0006','SUPRA_95','Toyota Supra family; donor RZ trim and native balanced stock values remain separate.'),
 ('GT4_NISS0004','350Z','Nissan 350Z model family; ratio-only package adaptation.'),
 ('GT4_SUBR0017','WRX','Subaru Impreza WRX family; wagon/version-VI donor differs from source variant.'),
 ('GT4_MITS0001','Evo','Lancer Evolution family; exact native model-year/trim not established here.'),
 ('GT4_NISS0021','GTR','Skyline GT-R family; original variant unspecified in this catalog; donor AWD is retained.'),
 ('GT4_LNCA0005','Celica_GT4','No native Delta: turbo AWD compact rally-car counterpart; donor identity and AWD remain unchanged.'),
 ('GT4_BMW_0010','BMW_M3','BMW M3 family; exact generation/trim not established here.'),
 ('MC3_VP_ELISE_04','Exige','Lotus mid-engine lightweight sports-car counterpart, not an Elise exact tune.'),
 ('MCLA_VP_AUD_R8_08','ACNSX_04','No native R8: mid-engine sports-car counterpart; donor AWD retained, no drivetrain transplant.'),
 ('MCLA_VP_LAM_GALLARDO_06','Zonda','No native Gallardo: mid-engine exotic counterpart; donor AWD retained, no drivetrain transplant.'),
 ('MUSTANG_68','MUSTANG67','Adjacent-year classic Mustang counterpart; 1968 donor is not asserted identical to 1967.'),
 ('MCLA_VP_CHV_CAMAROSS_69','CAMARO_SS','Classic Camaro SS family; exact RS/SS trim identity not established here.'),
 ('MCLA_VP_BUK_GRANDNATIONAL_87','GTO','No native GNX: front-engine rear-drive American performance-car counterpart; donor turbo engine and RWD retained.'),
 ('MCLA_VP_CHV_CORVETTEZ06_07','z06','Corvette Z06 model family; exact year-specific tune not established here.'),
 ('GT4_DODG0005','VIPER_SRT','Same Viper SRT family; separate exact base-tune evidence is not expanded by this ratio mapping.'),
 ('GT4_ASMT0005','ASTON_DB9','DB9 model family; ratio-only package adaptation.'),
 ('MCLA_VP_SLN_S7_06','Saleen_s7','Saleen S7 family; naturally aspirated/turbo distinction is not resolved, so no exact native tune claim.'),
 ('LIGHTNING_SVT','FALCON','No native Lightning truck: heavy front-engine performance-vehicle counterpart; truck base geometry/engine/layout retained.'),
 ('F100_1956','TORINO','No native F100: heavy classic Ford counterpart; no native truck tuning claim.'),
 ('MC3_VP_ESCALADE_03','FALCON','No native Escalade: heavy front-engine vehicle counterpart; SUV base physics/layout retained.'),
]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 catalog_path=OUT/'catalog.json';roster_path=ROOT/'data/juiced2/cars.json';content_path=ROOT/'data/juiced2/content.json'
 catalog=json.loads(catalog_path.read_text());roster=json.loads(roster_path.read_text())['cars'];content=json.loads(content_path.read_text());native={c['native_id']:c for c in catalog['cars']};cars={c['id']:c for c in content['cars']}
 assert len(MAPPINGS)==30 and {row[0]for row in MAPPINGS}=={c['code']for c in roster}==set(cars)
 fields=['stock_power','stock_weight','max_power','min_weight','brake_factor','tyre_factor','suspension_factor','turbo_factor','cost_modifier'];items=[]
 for code,native_id,reason in MAPPINGS:
  source=native[native_id];base=cars[code]['handling'];power_ratio=source['max_power']/source['stock_power'];mass_ratio=source['min_weight']/source['stock_weight']
  assert power_ratio>=1 and 0<mass_ratio<=1
  items.append(dict(car_id=code,name=cars[code]['name'],native_id=native_id,binding_kind='relative_endpoint_adaptation',rationale=reason,native_fields={key:source[key]for key in fields},native_row=source['native_row'],source=catalog['source'],ratios=dict(maximum_power_over_base=power_ratio,minimum_mass_over_base=mass_ratio),authoritative_base=dict(peak_bhp=base['peak_bhp'],mass=base['mass'],layout=base['layout']),adapted_endpoints=dict(maximum_power=base['peak_bhp']*power_ratio,minimum_mass=base['mass']*mass_ratio),rules=['Preserve authoritative base Handling at package factor zero.','Apply relative power/mass endpoints; do not replace base with native balanced stock values.','Do not alter donor drivetrain or physical dimensions.','Other native package factors are preserved source operands; their exact runtime consumer semantics remain separately evidenced.']))
 report=dict(schema_version=1,source_catalog_sha256=sha(catalog_path),source_roster_sha256=sha(roster_path),source_content_sha256=sha(content_path),cars=items,native_packages=catalog['packages'],native_engine_endpoints=catalog['engine_endpoints'],native_gear_ratios=catalog['gear_ratios'],limits=['All thirty mappings are explicitly relative adaptations, including model-family overlaps.','No additional native stock tune/variant identity is inferred.','Nine numeric CarModInfo operands exist; twelve refers to supplier categories, not twelve tuning factors.','No runtime assets or core/frontend files are modified.','Exact package interpolation, prototype eligibility and unlock consumers are retained in catalog.json and require their own implementation/verification.'])
 (OUT/'donor-mapping.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Staged30 relative mappings;9 original operands each; runtime unchanged')
if __name__=='__main__':main()
