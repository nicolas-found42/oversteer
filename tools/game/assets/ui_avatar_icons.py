"""Bind exact creator AddNewTexturedItem operands to recovered native PNGs."""
import hashlib,json
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/ui';images=json.loads((ROOT/'godot/assets/ui/native/manifest.json').read_text());bindings={}
for filename in ['ui_frontend-3e17f6c7.json','ui_frontend-8d63cc95.json']:
 path=SOURCE/'layout-fields'/filename;layout=json.loads(path.read_text())
 for index,row in enumerate(layout['fields']):
  for label in {x for x in row if isinstance(x,str)and x.startswith('GadgetIcons_')}:
   key=f'{filename_hash("Textures"+chr(92)+label+".ddt"):08x}';matches=[r for r in images if r['key']==key];assert matches
   binding=bindings.setdefault(label,dict(label=label,key=key,paths=[r['path']for r in matches],source_rows=[]));binding['source_rows'].append(dict(layout=filename,row=index,values=row,layout_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(SOURCE/'native-avatar-icon-bindings.json').write_text(json.dumps(dict(bindings=list(bindings.values()),limits=['Exact typed source operands and filename hashes; no inferred category-art substitutions.']),indent=2)+'\n');print(len(bindings),'source creator icon bindings; no runtime writes')
