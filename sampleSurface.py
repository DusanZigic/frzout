from __future__ import print_function
import numpy as np
from scipy import interpolate
import frzout
import json

with open('params.json', 'r') as jsonf: params = json.load(jsonf)

eos = np.loadtxt("eos.dat")
eos_int = interpolate.interp1d(eos[:, 0], eos[:, -1])
Tswitch = eos_int(params['hydro']['Edec'])


species = [('pion', 211), ('kaon', 321), ('proton', 2212)]

hrg_kwargs = dict(species='urqmd', res_width=True)
hrg = frzout.HRG(Tswitch, **hrg_kwargs)

# Surface columns
# 0 Tmid,
# 1 Xmid, 
# 2 Ymid,
# 3 dSigma(0, iSurf),
# 4 dSigma(1, iSurf),
# 5 dSigma(2, iSurf),
# 6 v1mid, 
# 7 v2mid,
# 8 CPi00*HbarC, 
# 9 CPi01*HbarC, 
# 10 CPi02*HbarC,
# 11 CPi11*HbarC, 
# 12 CPi12*HbarC, 
# 13 CPi22*HbarC,
# 14 CPi33*HbarC,
# 15 CPPI*HbarC
surface = np.loadtxt('surface.dat').reshape(-1, 16)

x = surface[:,:3]
sigma = surface[:,3:6]
v = surface[:,6:8]
pidict = {"xx": surface[:,11], "xy": surface[:,12], "yy": surface[:,13]}

surfaceobj = frzout.Surface(x, sigma, v, pi=pidict, Pi=surface[:,15], ymax=2)

maxsamples = params['main']['maxsamples']
file_n = params['main']['num_of_urqmd_jobs']
if file_n == 0: file_n = 1
file_names = [open('particles_in_%d.dat' % i, 'w') for i in range(file_n)]

for nsamples in range(maxsamples):
    f = file_names[nsamples % params['main']['num_of_urqmd_jobs']]
    parts = frzout.sample(surfaceobj, hrg)
    if parts.size == 0:
        continue
    print('#', parts.size, file=f)
    for p in parts:
        print(p['ID'], end=" ", file=f)
        for poscomp in p['x']:
            print(poscomp, end=" ", file=f)
        for ip in range(len(p['p'])-1):
            print(p['p'][ip], end=" ", file=f)
        print(p['p'][len(p['p'])-1], file=f)

for f in file_names: f.close()