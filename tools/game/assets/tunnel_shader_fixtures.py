"""Compare decoded original tunnel PS ALU with independent RGB equations."""
import json,math,random,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/tunnel-shaders';programs=json.loads((OUT/'programs.json').read_text())['programs']
def f32(v):return struct.unpack('f',struct.pack('f',v))[0]
def execute(program,textures,constants):
 c={int(k):v for k,v in program['literal_constants'].items()};c.update(constants);r=[[0.]*4 for _ in range(64)];out=[0.]*4;ps=0
 def src(o):
  value=r[o['index']]if o['register']=='r'else c.get(o['index'],[0.]*4)
  return [(-1 if o['negate']else 1)*(abs(value[i])if o['absolute']else value[i])for i in o['swizzle']]
 for ins in program['instructions']:
  if ins.get('fetch'):
   assert ins['fetch_opcode']==1;value=textures[ins['texture_index']]
   for k,sw in enumerate(ins['dest_swizzle']):
    if sw<4:r[ins['dest']][k]=f32(value[sw])
    elif sw in [4,5]:r[ins['dest']][k]=sw-4
    else:assert sw==7
   continue
  assert not ins['predicated'];a,b,d=[src(o)for o in ins['sources']];op=ins['vector_opcode'];old_ps=ps
  if op=='mul':v=[f32(x*y)for x,y in zip(a,b)]
  elif op=='mad':v=[f32(x*y+z)for x,y,z in zip(a,b,d)]
  elif op=='add':v=[f32(x+y)for x,y in zip(a,b)]
  elif op=='max':v=[max(x,y)for x,y in zip(a,b)]
  elif op=='dp3':v=[f32(sum(x*y for x,y in zip(a[:3],b[:3])))]*4
  elif op=='cndeq':v=[y if x==0 else z for x,y,z in zip(a,b,d)]
  else:raise ValueError(op)
  scalar=ins['scalar_opcode'];sa,sb=d[3],d[0]
  if scalar=='mulsc':
   o=ins['sources'][2];rawa=int(ins['raw'][0],16);rawc=int(ins['raw'][2],16);index=((rawa>>26)&1)|(((rawc>>29)&1)<<1)|(o['raw_swizzle']&0x3c);sa=c[o['raw_index']][o['swizzle'][3]];sb=r[index][o['swizzle'][0]]
   if o['negate']:sa,sb=-sa,-sb
  if scalar=='maxs':ps=max(sa,sb)
  elif scalar in ['muls','mulsc']:ps=f32(sa*sb)
  elif scalar=='muls_prev':ps=f32(sa*old_ps)
  elif scalar=='rcp':ps=f32(1/sa)
  elif scalar=='retain_prev':pass
  else:raise ValueError(scalar)
  assert not ins['vector_clamp']and not ins['scalar_clamp']
  vm,sm=ins['vector_mask'],ins['scalar_mask']
  for k in range(4):
   if ins['export']:
    if vm>>k&1 and sm>>k&1:out[k]=1.
    elif vm>>k&1:out[k]=v[k]
    elif sm>>k&1:out[k]=ps
    elif ins['export_zero']:out[k]=0.
   else:
    if vm>>k&1:r[ins['vector_dest']][k]=v[k]
    if sm>>k&1:r[ins['scalar_dest']][k]=ps
 return out
def grade(rgb,exp1,exp2):
 luma=f32(.33000001311302185)*sum(rgb)
 value=[(luma+(v-luma)*exp2[0])*exp2[3]+exp2[2]for v in rgb]
 denominator=max(*value,exp1[1])*exp1[2]+exp1[3]
 return [v/denominator for v in value]
selected=[next(p for p in programs if p['id']==ident)for ident in ['simpleGradient-Simple_3-pixel-694','luminousScroll-Luminous_2-pixel-660','backLightScroll-Normal_3-pixel-82']]
rng=random.Random(7305);errors={p['id']:0 for p in selected};fixtures=[]
for sample in range(5000):
 texture=[rng.random()for _ in range(4)];base=[rng.random()for _ in range(4)];colors=[[rng.random()*3 for _ in range(3)]+[0]for _ in range(3)];brightness=rng.random()*6;strength=rng.random()*5;multiplier=rng.random()*3
 exp1=[0,.01,rng.random()*.5,.5+rng.random()];exp2=[rng.random()*2,0,rng.random()*.1,rng.random()*2]
 constants={15:exp2,17:exp1,56:colors[2],57:colors[0],58:[brightness]*4,59:colors[1]}
 rgb=[brightness*sum(texture[j]*colors[j][i]for j in range(3))for i in range(3)];g=grade(rgb,exp1,exp2);expected=[g+[1],grade([texture[i]*strength*base[i]for i in range(3)],exp1,exp2)+[base[3]],[1,1,1,texture[3]*multiplier]]
 actual=[execute(selected[0],{4:texture},constants),execute(selected[1],{4:texture,5:base},{15:exp2,17:exp1,56:[strength]*4}),execute(selected[2],{4:texture},{56:[multiplier]*4})]
 for program,a,e in zip(selected,actual,expected):
  error=max(abs(x-y)for x,y in zip(a,e));errors[program['id']]=max(errors[program['id']],error);assert error<2e-5,(sample,program['id'],a,e)
 if sample<3:fixtures.append(dict(texture=texture,base=base,palette=colors,brightness=brightness,lum_strength=strength,multiplier=multiplier,exp1=exp1,exp2=exp2,outputs=actual))
report=dict(cases=15000,max_abs_error=errors,fixtures=fixtures,equations=dict(simpleGradient='rgb=brightness*(T.r*colour1+T.g*colour2+T.b*colour3);out.rgb=grade(rgb);out.a=1',luminousScroll='out.rgb=grade(lumTexture.rgb*lumStrength*baseTexture.rgb);out.a=baseTexture.a',backLightScroll='out.rgb=(1,1,1);out.a=baseTexture.a*multiplier',grade='l=.33000001311302185*(R+G+B);q=(l+(rgb-l)*exp2.x)*exp2.w+exp2.z;out=q/(max(q.r,q.g,q.b,exp1.y)*exp1.z+exp1.w)'),limits=['Explicitfixtureconstants—notnativeexposuredefaults.','CPUf32approximationvsindependenthighlevelequations,notnativeGPUprecision.','TextureinputsareSHADER-SAMPLEDvalues;samplertransfer/formatclampsremainseparate.'])
(OUT/'fixtures.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['cases'],errors)
