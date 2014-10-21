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
kplr_file = 'kplr008191672-2013011073258_llc.fits'

#Given the kplr ID and filename, open the FITS file and extract the data.
jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)
time, flux, flux_err = f.fix_data(lightdata)
flux, variance = f.rescale(flux, flux_err)
time -= np.min(time)


period = 3.54844644464
offset = 1.90818869887
width = 0.177046694669
depth = 0.00650010001

period_interval = np.arange(1.0,8.0,0.001)
offset_interval = np.arange(0.00,8.0,0.001)
width_interval = np.arange(0.00,1.0,0.0001)
depth_interval = np.arange(0.0, 0.02, 0.0001)

# x1 = 0
# first_interval = 0
# upd_int = 0
units = '(Days)'

#Set the search here.
parameter = raw_input('Parameter: ')
if parameter == 'period':
	x1 = period_interval
	first_interval = period_interval
	chi2 = [f.sum_chi_squared(flux, f.box(p, offset, depth, width, time), variance) for p in first_interval]
	update_period = period_interval[np.argmin(chi2)]
	#Generalize this.
	upd_int = np.linspace(update_period-0.001, update_period+0.001, 10000)
	upd_chi2 = [f.sum_chi_squared(flux, f.box(p, offset, depth, width, time), variance) for p in upd_int]
	period = upd_int[np.argmin(upd_chi2)]
	print period
	print np.min(upd_chi2)

elif parameter == 'offset':
	x1 = offset_interval
	first_interval = offset_interval
	chi2 = [f.sum_chi_squared(flux, f.box(period, o, depth, width, time), variance) for o in first_interval]
	update_offset = offset_interval[np.argmin(chi2)]
	upd_int = np.linspace(update_offset-0.001, update_offset+0.001, 10000)
	upd_chi2 = [f.sum_chi_squared(flux, f.box(period, o, depth, width, time), variance) for o in upd_int]
	offset = upd_int[np.argmin(upd_chi2)]
	print offset
	print np.min(upd_chi2)

elif parameter == 'width':
	x1 = width_interval
	first_interval = width_interval
	chi2 = [f.sum_chi_squared(flux, f.box(period, offset, depth, w, time), variance) for w in first_interval]
	update_width = width_interval[np.argmin(chi2)]
	upd_int = np.linspace(update_width-0.001, update_width+0.001, 10000)
	upd_chi2 = [f.sum_chi_squared(flux, f.box(period, offset, depth, w, time), variance) for w in upd_int]
	width = upd_int[np.argmin(upd_chi2)]
	print width
	print np.min(upd_chi2)

elif parameter == 'depth':
	units = '(Unitless)'
	x1 = depth_interval
	first_interval = depth_interval
	chi2 = [f.sum_chi_squared(flux, f.box(period, offset, d, width, time), variance) for d in first_interval]
	update_depth = depth_interval[np.argmin(chi2)]
	upd_int = np.linspace(update_depth-0.001, update_depth+0.001, 10000)
	upd_chi2 = [f.sum_chi_squared(flux, f.box(period, offset, d, width, time), variance) for d in upd_int]
	depth = upd_int[np.argmin(upd_chi2)]
	print depth
	print np.min(upd_chi2)

#Find the interval in the depth array where the chi2 values are (chi2 mimimum) + 10
#Make this part a function later?
minimum_chi2 = np.min(upd_chi2)
x_bool = upd_chi2 < (minimum_chi2 + 10)
x_int = upd_int[x_bool]

upd_chi2 = np.array(upd_chi2)
y_int = upd_chi2[x_bool]

#Generate light curve fro the data and fit the best fitting model given the parameters.
fig1 = plt.figure()
sub1 = fig1.add_subplot(211)
sub1.plot(time, flux, ',k')
print offset
sub1.plot(time,f.box(period, offset, depth, width, time), 'b')
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
plottitle = 'Period:{0} Offset:{1}'.format(period, offset)
sub1.set_title(plottitle)

#Compute chi2
sub2 = fig1.add_subplot(212)
sub2.plot(x1, chi2, 'b')
sub2.set_xlabel('{0} {1}'.format(parameter, units))
sub2.set_ylabel(r'$\chi^2$')

#Finer Search for chi2
fig2 = plt.figure()
sub3 = fig2.add_subplot(111)
sub3.plot(x_int, y_int, 'r')
sub3.ticklabel_format(useOffset = False)
sub3.set_ylim(minimum_chi2-1, minimum_chi2+9)
sub3.set_xlabel('{0}'.format(parameter))
sub3.set_ylabel(r'$\chi^2$')
sub3_title = 'Finer {0} search from {1} to {2}'.format(parameter ,upd_int[0], upd_int[-1])
sub3.set_title(sub3_title)
plt.show()
