import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

import time as t
t0 = t.clock()

kplr_id = '008191672'
# kplr_id = raw_input('Input kepler id:')

# Code to allow the user to decide which FITS format file to generate light curve.
# filename = raw_input('Input FITS file to use: ')
kplr_file = 'kplr008191672-2010355172524_llc.fits'

#Given the kplr ID and filename, open the FITS file and extract the data.
jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)
time, flux, flux_err = f.fix_data(lightdata)
flux, variance = f.rescale(flux, flux_err)
time -= np.min(time)


period = 3.54844624633
offset = 0.061
width = 0.25

depth_interval = np.arange(0.0, 0.02, 0.0001)

chi2 = [f.sum_chi_squared(flux, f.box(period, offset, d, width, time), variance) for d in depth_interval]

update_depth = depth_interval[np.argmin(chi2)]
print update_depth
print np.min(chi2)

upd_depth_int = np.linspace(update_depth-0.001, update_depth+0.001, 10000)
upd_chi2 = [f.sum_chi_squared(flux, f.box(period, offset, d, width, time), variance) for d in upd_depth_int]
best_depth = upd_depth_int[np.argmin(upd_chi2)]
print best_depth
print np.min(upd_chi2)

#Find the interval in the depth array where the chi2 values are (chi2 mimimum) + 10
#Make this part a function later?
minimum_chi2 = np.min(upd_chi2)
x_bool = upd_chi2 < (minimum_chi2 + 10)
x_int = upd_depth_int[x_bool]

upd_chi2 = np.array(upd_chi2)
y_int = upd_chi2[x_bool]


#Generate light curve fro the data and fit the best fitting model given the parameters.
fig1 = plt.figure()
sub1 = fig1.add_subplot(211)
sub1.plot(time, flux, ',k')
sub1.plot(time,f.box(period, offset, best_depth, width, time), 'b')
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

#Compute chi2
sub2 = fig1.add_subplot(212)
sub2.plot(depth_interval, chi2, '.k')
sub2.set_xlabel('Depth (Unitless)')
sub2.set_ylabel(r'$\chi^2$')
sub2_title = 'Depth search from {0} to {1}'.format(depth_interval[0], depth_interval[-1])
sub2.set_title(sub2_title)

#Finer Search for chi2
fig2 = plt.figure()
sub3 = fig2.add_subplot(111)
sub3.plot(x_int, y_int, 'r')
sub3.ticklabel_format(useOffset = False)
sub3.set_ylim(minimum_chi2-1, minimum_chi2+9)
sub3.set_xlabel('Depth (Unitless)')
sub3.set_ylabel(r'$\chi^2$')
sub3_title = 'Finer Depth search from {0} to {1}'.format(upd_depth_int[0], upd_depth_int[-1])
sub3.set_title(sub3_title)
plt.show()