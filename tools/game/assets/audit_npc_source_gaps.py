"""Check exact source NPC gap filenames against every original JFS header."""
import hashlib,json,struct,zlib
from pathlib import Path
from jfs_hash import filename_hash
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters/npc-appearances';OUT.mkdir(parents=True,exist_ok=True)
inv=json.loads((ROOT/'artifacts/juiced2-recovery/xdvdfs-inventory.json').read_text());files={r['path'].lower():r for r in inv['files']}
names=['Judge01.def','Judge02.def','dancer01.jsm','dancer02.jsm','Combats.jsm','BSHairNoScalp.jsm'];keys={filename_hash(name):name for name in names};banks=[];matches=[]
with open(inv['iso'],'rb')as iso:
 for header in inv['files']:
  if not header['path'].lower().endswith('.jfshdr'):continue
  iso.seek(header['offset']);raw_header=iso.read(header['size']);count=struct.unpack_from('>I',raw_header)[0];assert len(raw_header)==4+24*count
  banks.append(dict(path=header['path'],sha256=hashlib.sha256(raw_header).hexdigest(),entries=count))
  for index in range(count):
   key,offset,packed,size,*rest=struct.unpack_from('>6I',raw_header,4+24*index)
   if key not in keys:continue
   archive=header['path'][:-7]+'.jfs';iso.seek(files[archive.lower()]['offset']+offset);raw=iso.read(packed);raw=raw if packed==size else zlib.decompress(raw);assert len(raw)==size
   path=OUT/(Path(archive).stem+'-'+keys[key]+'.bin');path.write_bytes(raw);matches.append(dict(filename=keys[key],archive=archive,key=f'{key:08x}',member=index,sha256=hashlib.sha256(raw).hexdigest(),path=str(path.relative_to(ROOT)),size=size))
report=dict(exact_source_names=names,banks=banks,matches=matches,missing=[name for name in names if not any(m['filename']==name for m in matches)],limits=['Exact supplied-disc source names checked against all244JFSheaderbanks, not invented naming hypotheses.','Missing hash proves absence only for this filename/hash domain; alternate source-selected names remain separate.','Combats resolves existing component name combats through proven823DC190ASCIIcase-insensitive equality; it does not require a Combats.jsm filename.','Dancer.def names skeleton dancer01 versus common player basemesh; rig equivalence is not established by matching component names.','BSHairNoScalp component name remains absent from recovered component rules; no alias invented.'])
assert len(banks)==244
(OUT/'global-bank-gap-audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Checked244headers;',len(matches),'exactsourcegeometrymatches')
