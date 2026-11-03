"""Publish the reviewed tree material batch only when runtime assets are idle."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'artifacts/juiced2-build/tree-materials';DEST=ROOT/'godot/assets/worlds';rows=json.loads((SOURCE/'manifest.json').read_text())
for row in rows:
 assert hashlib.sha256((DEST/row['file']).read_bytes()).hexdigest()==row['before_sha256'],row['file']
 assert hashlib.sha256((SOURCE/row['file']).read_bytes()).hexdigest()==row['staged_sha256'],row['file']
for row in rows:(DEST/row['file']).write_bytes((SOURCE/row['file']).read_bytes())
(SOURCE/'published.json').write_text(json.dumps(dict(files=[dict(file=r['file'],sha256=r['staged_sha256'])for r in rows]),indent=2)+'\n')
print('Published',len(rows),'exact tree texture binding world scenes')
