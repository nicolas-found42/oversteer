"""Bounded candidate hash comparison against known native event-bank content."""
import json,zlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
known=0x28956449
names=['L8_Rookie_Evt.txt','L7_Evt.txt'];prefixes=['','Goals/','Goals\\','scripts/Goals/','scripts\\Goals\\','Scripts/Goals/','./Goals/','data/scripts/Goals/']
def hashes(b):
 out={'adler':zlib.adler32(b),'crc':zlib.crc32(b),'crc_inv':zlib.crc32(b)^0xffffffff}
 for init in [0,0xffffffff]:
  h=init
  for c in b:
   h^=c<<24
   for _ in range(8):h=((h<<1)^(0x04c11db7 if h&0x80000000 else 0))&0xffffffff
  out['normal'+str(init)]=h;out['normalinv'+str(init)]=h^0xffffffff
 h=0;fnv=2166136261;elf=0;rs=0;ra=63689;js=1315423911
 for c in b:
  h=(h+c)&0xffffffff;h=(h+(h<<10))&0xffffffff;h^=h>>6;fnv=((fnv^c)*16777619)&0xffffffff;elf=(elf<<4)+c;high=elf&0xf0000000
  if high:elf^=high>>24;elf&=~high
  rs=(rs*ra+c)&0xffffffff;ra=ra*378551&0xffffffff;js^=((js<<5)+c+(js>>2))&0xffffffff
 h=(h+(h<<3))&0xffffffff;h^=h>>11;h=(h+(h<<15))&0xffffffff;out.update(joaat=h,fnv=fnv,elf=elf,rs=rs,js=js&0xffffffff)
 for multiplier in [31,33,37,39,131,1313,13131,131313,65599]:
  for seed in [0,5381]:
   h=seed
   for c in b:h=(h*multiplier+c)&0xffffffff
   out[f'poly{multiplier}_{seed}']=h
 return out
for prefix in prefixes:
 for n in names:
  for s in [prefix+n,(prefix+n).lower(),(prefix+n).upper()]:
   for enc in ['utf8','utf-16-le','utf-16-be']:
    for zero in [False,True]:
     data=s.encode(enc)+(b'\0'if zero else b'')
     for alg,h in hashes(data).items():
      if h in [known,0xcba6a787]:print(alg,enc,zero,s,f'{h:08x}')
