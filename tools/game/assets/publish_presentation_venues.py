"""Publish verified original room subset and source-only creator camera contract."""
import hashlib,json,shutil,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/presentation';STAGE=SOURCE/'paintbooth-stage';venue=json.loads((STAGE/'venue.json').read_text());raw=(STAGE/'paintbooth.glb').read_bytes();assert hashlib.sha256(raw).hexdigest()==venue['sha256'];n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);assert len(doc['scenes'][0]['nodes'])==9 and venue['counts']['triangles']==11268
# Textures already published for the identical original Garage; preserve paths.
for image in doc.get('images',[]):
 if 'uri'in image:
  a=STAGE/image['uri'];b=ROOT/'godot/assets/worlds'/image['uri'];assert a.read_bytes()==b.read_bytes(),image['uri']
shutil.copyfile(STAGE/'paintbooth.glb',ROOT/'godot/assets/worlds/paintbooth.glb')
for source,runtime,data in [('paintbooth-stage/venue.json','presentation-paintbooth.json','native-paintbooth-venue.json'),('creator-presentation.json','presentation-creator.json','native-creator-presentation.json')]:
 payload=(SOURCE/source).read_bytes();json.loads(payload);(ROOT/'godot/assets'/runtime).write_bytes(payload);(ROOT/'data/juiced2'/data).write_bytes(payload)
print('Published verified9instance PaintBox geometry and source creator14camera/20marker contracts')
