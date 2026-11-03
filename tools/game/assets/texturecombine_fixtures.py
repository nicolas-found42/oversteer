"""Execute only the extracted TextureCombine ALU subset on constant texel inputs.

This is a source-check fixture, not a renderer replacement. Texture filtering,
sRGB transfer, render-target quantization and hardware reciprocal precision are
outside this bounded comparison.
"""
import hashlib,json,math,struct,random,colorsys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'artifacts/juiced2-build/characters/texturecombine';programs=json.loads((OUT/'programs.json').read_text())['programs']
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def mul(a,b):return f32(a*b)if a and b else 0.
def execute(name,A,B=None,value=(0,1,1),bounds=(-1,360),trace=False,test_hsv=(0,0,0)):
 p=next(p for p in programs if p['name']==name);code={i['index']:i for i in p['instructions']};c={int(k):v for k,v in p['literal_constants'].items()};c.update({56:list(test_hsv)+[0.],57:list(value)+[0.],58:list(bounds)+[0.,0.]});r=[[0.]*4 for _ in range(64)];output=[0.]*4;predicate=True;ps=0.;steps=[]
 def source(o):
  v=(r[o['index']]if o['register']=='r'else c.get(o['index'],[0.]*4));v=[v[j]for j in o['swizzle']];return[(-1 if o['negate']else 1)*(abs(x)if o['absolute']else x)for x in v]
 for cf in p['control_flow']:
  if cf['opcode']not in[1,2,5,6]:continue
  if cf['opcode']in[5,6]and predicate!=cf['predicate_condition']:continue
  for j in range(cf['count']):
   ins=code[cf['address']+j]
   if ins.get('fetch'):
    v=A if ins['texture_index']==4 else B;assert v is not None
    for k,sw in enumerate(ins['dest_swizzle']):
     if sw<4:r[ins['dest']][k]=f32(v[sw])
     elif sw in[4,5]:r[ins['dest']][k]=float(sw-4)
     else:assert sw==7
    continue
   if ins['predicated']and predicate!=ins['predicate_condition']:continue
   a,b,d=[source(o)for o in ins['sources']];op=ins['vector_opcode'];scalar=ins['scalar_opcode'];dest=output if ins['export']else r[ins['vector_dest']];old_ps=ps
   if op=='max':v=[max(x,y)for x,y in zip(a,b)]
   elif op=='min':v=[min(x,y)for x,y in zip(a,b)]
   elif op=='add':v=[f32(x+y)for x,y in zip(a,b)]
   elif op=='mul':v=[mul(x,y)for x,y in zip(a,b)]
   elif op=='mad':v=[f32(x*y+z)if x and y else z for x,y,z in zip(a,b,d)]
   elif op in['seq','sgt','sge']:v=[float(x==y if op=='seq'else x>y if op=='sgt'else x>=y)for x,y in zip(a,b)]
   elif op in['cndeq','cndgt']:v=[y if(x==0 if op=='cndeq'else x>0)else z for x,y,z in zip(a,b,d)]
   elif op=='setp_ne_push':predicate=a[3]==0 and b[3]!=0;v=[0. if a[0]==0 and b[0]!=0 else f32(a[0]+1)]*4
   else:raise ValueError(op)
   # Scalar operands are read before either co-issued result is committed.
   sa,sb=d[3],d[0]
   if scalar in['mulsc','addsc','subsc']:
    o=ins['sources'][2];neg=-1 if o['negate']else 1;const=c[o['raw_index']][o['swizzle'][3]];index=(int(ins['raw'][0],16)>>26&1)|((int(ins['raw'][2],16)>>29&1)<<1)|(o['raw_swizzle']&0x3c);temp=r[index][o['swizzle'][0]];absolute=bool(int(ins['raw'][0],16)&128);sa=neg*(abs(const)if absolute else const);sb=neg*(abs(temp)if absolute else temp)
   if scalar in['maxs','mins']:ps=max(sa,sb)if scalar=='maxs'else min(sa,sb)
   elif scalar in['adds','addsc']:ps=f32(sa+sb)
   elif scalar=='adds_prev':ps=f32(sa+old_ps)
   elif scalar in['muls','mulsc']:ps=mul(sa,sb)
   elif scalar=='subsc':ps=f32(sa-sb)
   elif scalar=='rcp':ps=f32(1/sa)if sa else math.copysign(math.inf,sa)
   elif scalar=='truncs':ps=float(math.trunc(sa))
   elif scalar=='setp_pop':predicate=f32(sa-1)<=0;ps=0. if predicate else f32(sa-1)
   elif scalar=='setp_inv':predicate=sa==1;ps=0. if predicate else 1. if sa==0 else sa
   elif scalar=='retain_prev':pass
   else:raise ValueError(scalar)
   if ins['vector_clamp']:v=[max(0.,min(1.,x))for x in v]
   if ins['scalar_clamp']:ps=max(0.,min(1.,ps))
   vm,sm=ins['vector_mask'],ins['scalar_mask']
   for k in range(4):
    if ins['export']:
     if(vm>>k&1)and(sm>>k&1):output[k]=1.
     elif vm>>k&1:output[k]=v[k]
     elif sm>>k&1:output[k]=ps
     elif ins['export_zero']:output[k]=0.
    else:
     if vm>>k&1:dest[k]=v[k]
     if sm>>k&1:r[ins['scalar_dest']][k]=ps
   if trace:steps.append(dict(index=ins['index'],predicate=predicate,ps=ps,registers=[list(v)for v in r[:5]]))
 return(output,steps)if trace else output
if __name__=='__main__':
 samples=[]
 for name in['Copy','Alpha','MattAlpha','HSV']:
  result=execute(name,[.8,.3,.1,.7],[.2,.6,.9,.4],value=(30,.8,1.2));print(name,result);samples.append(dict(name=name,A=[.8,.3,.1,.7],B=[.2,.6,.9,.4],value=[30,.8,1.2],bounds=[-1,360],output=result))
 (OUT/'sample-fixtures.json').write_text(json.dumps(samples,indent=2,allow_nan=False)+'\n')

def reference_hsv(A,value,bounds):
 R,G,B,alpha=A;maximum=max(R,G,B);minimum=min(R,G,B);delta=maximum-minimum
 saturation=delta/maximum if maximum else 0.;denominator=delta+1.0000000116860974e-7
 if maximum==R:hue=(G-B)/denominator
 elif maximum==G:hue=(B-R)/denominator+2
 else:hue=(R-G)/denominator+4
 hue*=60
 if hue<0:hue+=360
 if maximum==0:hue=-1.
 if not(bounds[0]<hue<bounds[1]):return list(A)
 hue+=value[0];saturation*=value[1];maximum*=value[2]
 if hue==-1 or saturation==0:return[maximum,maximum,maximum,alpha]
 for _ in range(2):
  if hue>=360:hue-=360
  if hue<0:hue+=360
 h6=hue/60;sector=math.trunc(h6);fraction=h6-sector;p=maximum*(1-saturation);q=maximum*(1-saturation*fraction);t=maximum*(1-saturation*(1-fraction))
 rgb={0:(maximum,t,p),1:(q,maximum,p),2:(p,maximum,t),3:(p,q,maximum),4:(t,p,maximum)}.get(sector,(maximum,p,q));return[*rgb,alpha]

def verify():
 rng=random.Random(0x360);worst={name:0. for name in['HSV','Alpha','MattAlpha']};cases=[]
 for _ in range(4000):
  A=[rng.random()for _ in range(4)];B=[rng.random()for _ in range(4)];value=[rng.uniform(-350,350),rng.uniform(0,2),rng.uniform(0,2)];bounds=(-1.,360.);expected=reference_hsv(A,value,bounds);actual=execute('HSV',A,value=value,bounds=bounds);error=max(abs(a-b)for a,b in zip(actual,expected));worst['HSV']=max(worst['HSV'],error);assert error<1e-5,(A,value,actual,expected)
  for name in['Alpha','MattAlpha']:
   expected=[(1-B[3])*A[i]+B[3]*B[i]for i in range(3)]+[A[3]if name=='Alpha'else A[3]*(1-B[3])];actual=execute(name,A,B);error=max(abs(a-b)for a,b in zip(actual,expected));worst[name]=max(worst[name],error);assert error<2e-7
 # Explicit range endpoints, achromatic/black, no pixel-shader saturation, and alpha preservation.
 for A,value,bounds in [([1,0,0,.35],[90,1,1],[0,360]),([1,0,0,.35],[90,1,1],[-1,360]),([0,0,0,.4],[352.8,1.16,.23],[-1,360]),([.4,.4,.4,.8],[10,2,2],[-1,360]),([.8,.2,.1,.2],[30,2,2],[-1,360])]:
  actual=execute('HSV',A,value=value,bounds=bounds);expected=reference_hsv(A,value,bounds);assert max(abs(a-b)for a,b in zip(actual,expected))<1e-5;cases.append(dict(A=A,value=value,bounds=bounds,output=actual))
 result=dict(program_manifest_sha256=hashlib.sha256((OUT/'programs.json').read_bytes()).hexdigest(),fixture_helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),independent_high_level_cases=4000*3,max_abs_error=worst,edge_cases=cases,comparison='Decoded ALU/CF execution comparedwith independentlywrittenhigh-levelRGB/HSV andalpha equations',limits=['Not a hardwareGPUrun; float32ALUmodel andSDKspecifiedopcodes, notexactreciprocalULPs/NaN/denormalclaims.','Raw shaderclampflagsarefalse; render-targetformatclamp/quantization andsamplersRGBtransfer remainseparate.','vValue/boundsfixtures are explicit; testHSV debugoverrideissetzero, nativeeffectdefault/callerbindingneedsseparateproof.'])
 (OUT/'independent-checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result
if __name__=='__main__':print(verify())
