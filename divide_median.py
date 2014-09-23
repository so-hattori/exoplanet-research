import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

import time as t
t0 = t.clock()

#This is terrible, figure out a way to do this automatically and without writing out all the files....
kplr_id = '002973073'
kplr_filename_list = ('kplr002973073-2009131105131_llc.fits',
						'kplr002973073-2009166043257_llc.fits',
						'kplr002973073-2009259160929_llc.fits',
						'kplr002973073-2009350155506_llc.fits',
						'kplr002973073-2010078095331_llc.fits',
						'kplr002973073-2010174085026_llc.fits',
						'kplr002973073-2010265121752_llc.fits',
						'kplr002973073-2010355172524_llc.fits',
						'kplr002973073-2011073133259_llc.fits',
						'kplr002973073-2011177032512_llc.fits',
						'kplr002973073-2011271113734_llc.fits',
						'kplr002973073-2012004120508_llc.fits',
						'kplr002973073-2012088054726_llc.fits',
						'kplr002973073-2012179063303_llc.fits',
						'kplr002973073-2012277125453_llc.fits',
						'kplr002973073-2013011073258_llc.fits',
						'kplr002973073-2013098041711_llc.fits',
						'kplr002973073-2013131215648_llc.fits'
						)

lightdata_list = f.comb_openfile(kplr_id, kplr_filename_list)
#The following normalizes and also combines the data.
# time, flux, variance = f.comb_data(lightdata_list)

#The following does NOT normalize the data but combines it.
time, flux, variance = f.nonnorm_data(lightdata_list)
# print time.shape
# assert 0
time -= np.median(time)

# The following 5 lines of code create a fake transit signal inside the data.
inj_period = 200.00
inj_offset = 0.0
inj_depth = 0.00989188
inj_width = 1.21325
flux = f.raw_injection(inj_period,inj_offset,inj_depth,inj_width,time,flux)
med_flux = f.median_filter(flux, 80)

#Now we need to divide the "raw" data with the median filter to divide out noise.
new_flux = flux / med_flux

fig1 = plt.figure()
sub1 = fig1.add_subplot(111)
sub1.plot(time, flux, ',k')
# ylim_range = 0.015
# ylim_limits = [1-ylim_range,1+0.5*(ylim_range)]
# sub1.set_ylim(ylim_limits[0],ylim_limits[-1])
sub1.ticklabel_format(useOffset = False)

# fig2 = plt.figure()
# sub2 = fig2.add_subplot(111)
# sub2.plot(time, med_flux, ',k')
# ylim_range = 0.01
# ylim_limits = [1-ylim_range,1+ylim_range]
# sub2.set_ylim(ylim_limits[0],ylim_limits[-1])
# sub2.ticklabel_format(useOffset = False)

fig3 = plt.figure()
sub3 = fig3.add_subplot(111)
sub3.plot(time, new_flux, ',k')
# ylim_range = 0.015
# ylim_limits = [1-ylim_range,1+0.5*(ylim_range)]
# sub3.set_ylim(ylim_limits[0],ylim_limits[-1])
sub3.ticklabel_format(useOffset = False)
plt.show()
