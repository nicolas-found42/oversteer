"""Original Juiced2 filename hash recovered from PPC822AB038/8228BC28.

ASCII-uppercase first (823DD328), pairwise quartic accumulator modulo2^32,
then remainder modulo4000000000. Exact native JSMMHoodedtop key verified.
"""
def filename_hash(name):
 data=name.upper().encode('ascii');result=0
 for i in range(len(data)-1):
  for j in range(i,len(data)):
   a=data[i] if data[i]<128 else data[i]-256;b=data[j]if data[j]<128 else data[j]-256
   result=(result+(b+j)*(b+19)*(a+7)*(a+i))&0xffffffff
 return result%4000000000
