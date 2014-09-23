import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

import time as t
t0 = t.clock()

kplr_id = '002973073'
kplr_file = 'kplr002973073-2009166043257_llc.fits'

jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)
time, flux, flux_err = f.fix_data(lightdata)
time -= np.median(time)

inj_period = 300.00
inj_offset = -12.0
inj_depth = 0.000336
inj_width = 0.54
flux = f.raw_injection(inj_period,inj_offset,inj_depth,inj_width,time,flux)

flux, variance = f.rescale(flux, flux_err)

depth_interval = np.linspace(0.00,0.001, 200)
width_interval = np.linspace(0.40,0.70, 200)

ln_like_grid = [[f.ln_like(flux, f.push_box_model(inj_offset, d, w, time), variance) for d in depth_interval] for w in width_interval]

ln_like_flat = f.ln_like(flux, f.flat_model(time), variance)
ln_like_grid -= ln_like_flat
#The following two lines would net negatiev likelihood values to NaN
# negative = ln_like_grid < 0
# ln_like_grid[negative] = np.nan

plt.imshow(ln_like_grid, cmap= 'spectral', aspect = 'auto', extent = [depth_interval[0], depth_interval[-1], width_interval[0], width_interval[-1]], origin = 'lower', interpolation = 'nearest')
plt.colorbar()
plt.xlabel('Depth (unitless)')
plt.ylabel('Width (days)')
plt.title(r'$\Delta \ln L = \ln L_m - \ln L_f$')

print t.clock() - t0

plt.show()