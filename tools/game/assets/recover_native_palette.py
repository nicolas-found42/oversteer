"""Recover exact native ColourChart palette bytes and original UI layout bounds."""
import hashlib,json,re,struct,sys
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/ui';data_path=ROOT/'artifacts/juiced2-recovery/recompiled-handling/decoded-sections/824A0000-.data.bin';raw=data_path.read_bytes();address=0x824CB7F8;offset=address-0x824A0000;cells=[]
for column in range(24):
 for row in range(11):
  alpha,red,green,blue=raw[offset+4*(column*11+row):offset+4*(column*11+row)+4];cells.append(dict(column=column,row=row,rgba=[red,green,blue,alpha]))
manifest=json.loads((ROOT/'godot/assets/ui/native/manifest.json').read_text());art=[]
for label in ['ColourChart_Overlay','GadgetIcons_Colour']:
 key=f'{filename_hash("Textures"+chr(92)+label+".ddt"):08x}';matches=[r for r in manifest if r['key']==key];art.append(dict(native_label=label,key=key,paths=[r['path']for r in matches]))
report=dict(columns=24,rows=11,order='column-major',cells=cells,layout=dict(source='ui-17099544',gadget='COLOUR',rect_normalized=[.09063000231981277,.6416699886322021,.32813000679016113,.21875]),art=art,source=dict(address=f'{address:08X}',data_sha256=hashlib.sha256(raw).hexdigest(),begin_callback='823556D8',constructor='82344C80',draw_consumer='82345160'),limits=['Exact original default 24x11 chart bytes; alternate flag356 row skipping retained as unresolved separate mode.','Reference color-wheel interaction and native shading/material parameters are separate from this original grid.'])
(SOURCE/'native-colour-chart.json').write_text(json.dumps(report,indent=2)+'\n')
for va in ['823556D8','82344C80','82345160','82344E68']:
 for p in (ROOT/'artifacts/juiced2-recovery/recompiled-handling/generated/default').glob('*.cpp'):
  m=re.search(r'DEFINE_REX_FUNC\(sub_'+va+r'\).*?(?=\nDEFINE_REX_FUNC|\Z)',p.read_text(),re.S)
  if m:(SOURCE/f'native-colour-chart-{va}.cpp').write_text(m.group());break
print('Recovered264exactnativeRGBAcells',art)

if "--publish"in sys.argv:
 for target in ["data/juiced2/native-colour-chart.json","godot/assets/ui/native/colour-chart.json"]:(ROOT/target).write_bytes((SOURCE/"native-colour-chart.json").read_bytes())
 print("Published exact original chart JSON")
