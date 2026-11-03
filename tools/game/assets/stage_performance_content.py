"""Stage optional per-car native performance adaptations on fresh production data."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/native-performance'
source=ROOT/'data/juiced2/content.json';raw=source.read_bytes();content=json.loads(raw);mapping=json.loads((OUT/'donor-mapping.json').read_text());assert mapping['source_content_sha256']==hashlib.sha256(raw).hexdigest(),'Regenerate stage_donor_performance.py from current production content first'
by={row['car_id']:row for row in mapping['cars']};assert len(by)==30 and set(by)=={car['id']for car in content['cars']}
for car in content['cars']:car['native_performance']=by[car['id']]
result=json.dumps(content,indent=2,allow_nan=False)+'\n';target=OUT/'content-with-native-performance.json';target.write_text(result)
(OUT/'content-binding.json').write_text(json.dumps(dict(source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(raw).hexdigest(),staged=str(target.relative_to(ROOT)),staged_sha256=hashlib.sha256(result.encode()).hexdigest(),cars=30,publication='STAGED ONLY; no runtime/source content mutated',schema='CarDefinition.native_performance optional object; no top-level performance_catalog field',limits=['All mappings remain explicit relative endpoint adaptations.','Core consumer/package policy must be verified before a separately authorized coherent publication.']),indent=2)+'\n')
print('Staged30native_performancefields;productionunchanged')
