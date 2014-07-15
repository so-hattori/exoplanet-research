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
flux, variance = f.rescale(flux, flux_err)
time -= np.median(time)

inj_period = 300.00
inj_offset = 12.0
inj_depth = 0.000336
inj_width = 0.11

flux = f.injection(inj_period,inj_offset,inj_depth,inj_width,time,flux)


width = 0.11
depth = 0.0003336

# offset_interval = np.linspace(time[0], time[-1], 10000)

ln_like_array = [f.ln_like(flux, f.push_box_model(o, depth, width, time), variance) for o in time]
ln_like_flat = f.ln_like(flux, f.flat_model(time), variance)

#subtract the flat model likelihood from the ln_likelihood array
ln_like_array -= ln_like_flat


fig1 = plt.figure()
sub1 = fig1.add_subplot(121)
sub1.plot(time, flux, ',k')
# sub1.vlines(inj_offset + 0.5*inj_width, flux.min(),flux.max(), 'r')

xlab = "Time (days, [Time] - median_Time)"
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

sub2 = fig1.add_subplot(122)
sub2.plot(time, ln_like_array, 'b')
# sub2.vlines(inj_offset, ln_like_array.min()-100,ln_like_array.max()+100, 'r')

xlab = "Offset (days)"
sub2.set_xlabel(xlab)
sub2.set_ylabel('delta ln_Likelihood')
plottitle = r'$\Delta \ln L = \ln L_p - \ln L_f$'
sub2.set_title(plottitle)

plt.show()