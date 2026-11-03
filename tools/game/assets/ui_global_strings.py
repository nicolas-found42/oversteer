"""Recover complete native English strings, loading tips and Xbox360 credits."""
import json,struct,zlib,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];source=ROOT/'artifacts/juiced2-recovery';h=(source/'scripts.jfshdr').read_bytes();a=(source/'scripts.jfs').read_bytes();key=0x9108c6c7
for index in range(struct.unpack_from('>I',h)[0]):
 k,o,n,u,*_=struct.unpack_from('>6I',h,4+index*24)
 if k==key:break
else:raise ValueError('native English table missing')
b=a[o:o+n]if n==u else zlib.decompress(a[o:o+n]);text=b.decode('utf-16');entries={m[1]:m[2]for m in re.finditer(r'(?ms)^([A-Z0-9_]+)\s*=\s*(.*?)¤',text)};provenance=dict(bank='scripts.jfs',member=index,key=f'{key:08x}',sha256=hashlib.sha256(b).hexdigest(),text_encoding='UTF16BE BOM, native¤terminatedkey/valueentries')
base=ROOT/'godot/assets/ui/native';base.mkdir(parents=True,exist_ok=True);(base/'english-strings.json').write_text(json.dumps(dict(language='en',entries=entries,source=provenance),indent=2,ensure_ascii=False)+'\n');tips=[dict(id=k,text=v)for k,v in entries.items()if k.startswith('TIP_')];(base/'loading-tips.json').write_text(json.dumps(dict(tips=[t['text']for t in tips],records=tips,source=provenance),indent=2,ensure_ascii=False)+'\n')
keys=[k for k in entries if k.startswith('CREDITS_')and not any(v in k for v in ['_PS2','_PS3','_PSP','_PC'])];sections=[dict(key=k,text=entries[k])for k in keys];lines=[]
for section in sections:lines.extend(section['text'].strip().splitlines());lines.extend(['',''])
credits=dict(lines=lines,sections=sections,source={**provenance,'language':'English','platform_sections':'Xbox360+common'},layout_source='ui_frontend59244e31 BeginTextTEXT AutoScroll HIN_Text nativebox[.15625,.17708,.6875,.68333]');(ROOT/'godot/assets/credits.json').write_text(json.dumps(credits,indent=2,ensure_ascii=False)+'\n');(ROOT/'data/juiced2/credits.json').write_text(json.dumps(credits,indent=2,ensure_ascii=False)+'\n');print(len(entries),'originalEnglishentries;',len(tips),'originaltips;',len(lines),'originalcreditlines')
