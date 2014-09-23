import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

import time as t
t0 = t.clock()

kplr_id = '002973073'
kplr_file = 'kplr002973073-2013011073258_llc.fits'

jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)
time, flux, flux_err = f.fix_data(lightdata)
time -= np.median(time)

flux, variance = f.rescale(flux, flux_err)

width = 1.0
depth = 0.000236
 
# offset_interval = np.linspace(time[0], time[-1], 10000)

ln_like_perfect = np.asarray([f.ln_like(flux, f.push_box_model(o, depth, width, time), variance) for o in time])
ln_like_flat = f.ln_like(flux, f.flat_model(time), variance)

#subtract the flat model likelihood from the ln_likelihood array
ln_like_array = ln_like_perfect - ln_like_flat

index_max_like = np.argmax(ln_like_array)
found_offset = time[index_max_like]
print found_offset

fig1 = plt.figure()
sub1 = fig1.add_subplot(211)
sub1.plot(time, flux, '.k')
sub1.plot(time, f.push_box_model(found_offset,depth,width,time))
# sub1.vlines(inj_offset + 0.5*inj_width, flux.min(),flux.max(), 'r')

xlab = "Time (days, [Time] - median_Time)"
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

sub2 = fig1.add_subplot(212)
sub2.plot(time, ln_like_array, 'b', label = r'$\Delta \ln L = \ln L_p - \ln L_f$')
sub2.legend(loc=0)
# sub2.vlines(inj_offset, ln_like_array.min()-100,ln_like_array.max()+100, 'r')

xlab = "Offset (days)"
sub2.set_xlabel(xlab)
sub2.set_ylabel('delta ln_Likelihood')
# plottitle = r'$\Delta \ln L = \ln L_p - \ln L_f$'
# sub2.set_title(plottitle)

# #Start the imperfects on a second figure
# fig2 = plt.figure()
# sub1 = fig2.add_subplot(111)

# width_interval = [0.08]
# for w in width_interval:
# 	ln_like_array = np.asarray([f.ln_like(flux, f.push_box_model(o, depth, w, time), variance) for o in time])
# 	sub1.plot(time, ln_like_perfect - ln_like_array, 'b')
# 	# sub1.plot(time, ln_like_array, 'r')

print t.clock() - t0

plt.show()