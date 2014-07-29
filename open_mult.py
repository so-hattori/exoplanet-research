import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

import time as t
t0 = t.clock()

kplr_id = '002973073'
kplr_filename_list = ('kplr002973073-2009131105131_llc.fits',
						'kplr002973073-2009166043257_llc.fits',
						'kplr002973073-2009259160929_llc.fits',
						'kplr002973073-2009350155506_llc.fits',
						'kplr002973073-2010078095331_llc.fits',
						'kplr002973073-2010174085026_llc.fits',
						'kplr002973073-2010265121752_llc.fits',
						'kplr002973073-2010355172524_llc.fits'
						)

lightdata_list = f.comb_openfile(kplr_id, kplr_filename_list)
time, flux, variance = f.comb_data(lightdata_list)
# print time.shape
# assert 0
time -= np.median(time)

#The following 5 lines of code create a fake transit signal inside the data.
# inj_period = 100.00
# inj_offset = -12.0
# inj_depth = 0.000336
# inj_width = 0.54
# flux = f.raw_injection(inj_period,inj_offset,inj_depth,inj_width,time,flux)

# flux, variance = f.rescale(flux, flux_err)

width = 1.5
depth = 0.000336
 
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
sub1.plot(time, flux, ',k')
sub1.set_ylim(-0.002, 0.002)
# sub1.plot(time, f.push_box_model(found_offset,depth,width,time))
# sub1.vlines(inj_offset + 0.5*inj_width, flux.min(),flux.max(), 'r')

xlab = "Time (days, [Time] - median_Time)"
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve"
sub1.set_title(plottitle)

# fig2 = plt.figure()
sub2 = fig1.add_subplot(212)
sub2.plot(time, ln_like_array, 'b', label = r'$\Delta \ln L = \ln L_p - \ln L_f$')
sub2.legend(loc=0)
# sub2.vlines(inj_offset, ln_like_array.min()-100,ln_like_array.max()+100, 'r')

xlab = "Offset (days)"
sub2.set_xlabel(xlab)
sub2.set_ylabel('delta ln_Likelihood')
plottitle = r'$\Delta \ln L = \ln L_p - \ln L_f$'
sub2.set_title(plottitle)

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