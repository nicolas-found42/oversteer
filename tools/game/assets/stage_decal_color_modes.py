"""Stage exact monochrome mask metadata while preserving original artwork bytes."""
import json,collections,sys
from pathlib import Path
from PIL import Image
from decal_color_mode import classify
ROOT=Path(__file__).resolve().parents[3];catalog=json.loads((ROOT/'godot/assets/decals/catalog.json').read_text());counts=collections.Counter()
for design in catalog['designs']:
 path=ROOT/'godot'/design['texture_path'][6:];fields=classify(Image.open(path));design.update(fields);counts[fields['color_mode']]+=1
catalog['limits']=[line for line in catalog['limits']if not line.startswith('Artwork RGB')];catalog['limits'].append('Exact constant black/white visible source RGB classified as alpha mask; chosen-color fill is an explicit renderer adaptation until native compositor translation is proven.')
out=ROOT/'artifacts/juiced2-build/decals/color-modes';out.mkdir(exist_ok=True);(out/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n');(out/'verification.json').write_text(json.dumps(dict(designs=len(catalog['designs']),counts=dict(counts),original_pngs_modified=False),indent=2)+'\n');print(dict(counts),'staged; runtime unchanged')

if "--publish"in sys.argv:
 for target in ["godot/assets/decals/catalog.json","data/juiced2/decals.json"]:(ROOT/target).write_bytes((out/"catalog.json").read_bytes())
 print("Published catalog metadata only; original PNG bytes unchanged")
