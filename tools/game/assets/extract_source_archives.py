"""Extract the original script/UI/avatar archives needed by asset decoders."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text())
with open(inv['iso'],'rb') as iso:
 for row in inv['files']:
  name=row['path'].lower();dest=None
  if name in ['scripts.jfs','scripts.jfshdr']:dest=ROOT/'artifacts/juiced2-recovery'/Path(name).name
  elif Path(name).name in [b+e for b in ['ui','ui_frontend','ui_ingame','textures']for e in ['.jfs','.jfshdr']]:dest=ROOT/'artifacts/juiced2-build/ui'/Path(name).name
  elif name in [f'skinned/{b.lower()}{e}' for b in ['avatar_lo','componentdefs','player01','FE_CommonMale_amf','anm','script','mrp']for e in ['.jfs','.jfshdr']]:dest=ROOT/'artifacts/juiced2-build/characters'/Path(row['path']).name
  if dest:
   dest.parent.mkdir(parents=True,exist_ok=True);iso.seek(row['offset']);data=iso.read(row['size']);assert len(data)==row['size'];dest.write_bytes(data);print(row['path'],len(data))
