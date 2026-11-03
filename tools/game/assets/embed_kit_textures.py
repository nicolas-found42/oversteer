"""Embed unchanged original PNG bytes to remove external texture import ordering."""
import json,struct,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
for name in sys.argv[1:]:
 p=ROOT/'godot/assets/kits'/name;raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);changed=0
 for image in d.get('images',[]):
  if 'uri'not in image:continue
  png=(p.parent/image.pop('uri')).read_bytes()
  while len(binary)%4:binary.append(0)
  d['bufferViews'].append(dict(buffer=0,byteOffset=len(binary),byteLength=len(png)));binary.extend(png);image.update(bufferView=len(d['bufferViews'])-1,mimeType='image/png');image.setdefault('extras',{})['sourcePngSha256']=hashlib.sha256(png).hexdigest();changed+=1
 if not changed:continue
 while len(binary)%4:binary.append(0)
 d['buffers'][0]['byteLength']=len(binary);j=json.dumps(d,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary);print(name,changed,'unchanged PNG images embedded')
