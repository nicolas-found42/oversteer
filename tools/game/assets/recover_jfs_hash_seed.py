"""Test reversible hash families against independently identified native banks."""
import json
from pathlib import Path
MASK=0xffffffff;known={'L7_Evt':0xcba6a787,'L6_Evt':0xca32970d,'L5_Evt':0xc8c48fc7,'L4_Evt':0xc75c8b79,'L3_Evt':0xc5fa83ff,'L2_Evt':0xc49e734d,'L1_Evt':0xc348536f};found=[]
for extension in ['', '.txt','.TXT']:
 for case in ['raw','lower','upper']:
  for enc in ['utf8','utf-16-le','utf-16-be']:
   def encode(name):
    text=name+extension
    if case=='lower':text=text.lower()
    if case=='upper':text=text.upper()
    return text.encode(enc)
   for multiplier in [31,33,37,39,131,1313,13131,131313,65599,16777619]:
    inv=pow(multiplier,-1,1<<32)
    for mode in ['add','xor_after','xor_before']:
     seed=known['L7_Evt']
     for c in reversed(encode('L7_Evt')):
      if mode=='add':seed=((seed-c)*inv)&MASK
      elif mode=='xor_after':seed=((seed^c)*inv)&MASK
      else:seed=((seed*inv)&MASK)^c
     def calc(b):
      h=seed
      for c in b:
       if mode=='add':h=(h*multiplier+c)&MASK
       elif mode=='xor_after':h=((h*multiplier)^c)&MASK
       else:h=((h^c)*multiplier)&MASK
      return h
     matches=sum(calc(encode(name))==value for name,value in known.items())
     if matches>1:print(extension,case,enc,multiplier,mode,hex(seed),matches,flush=True)
     if matches==len(known):found.append(dict(extension=extension,case=case,encoding=enc,multiplier=multiplier,mode=mode,seed=seed))
print('FOUND',found)
Path('artifacts/juiced2-build/jfs-hash-seed-evidence.json').write_text(json.dumps(found,indent=2))
