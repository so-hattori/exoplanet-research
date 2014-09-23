#This is a python script to inject an artificial transit signal.
import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

kplr_id = '006116605'
kplr_file = 'kplr006116605-2009259160929_llc.fits'

jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)
time, flux, flux_err = f.fix_data(lightdata)
flux, variance = f.rescale(flux, flux_err)
time -= np.median(time)

period = 300.00
offset = 20.0
depth = 0.008
width = 0.09

flux = f.raw_injection(period,offset,depth,width,time,flux)

offset_interval = np.arange(0.00, 30.00, 0.01)
chi2 = [f.sum_chi_squared(flux, f.box(period, o, depth, 0.09, time), variance) for o in offset_interval]
best_offset = offset_interval[np.argmin(chi2)]

fig1 = plt.figure()
sub1 = fig1.add_subplot(121)
sub1.plot(time ,flux, color="black", marker=",", linestyle = 'None')
sub1.plot(time , f.box(period, best_offset, depth, 0.9, time), 'r')
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

sub2 = fig1.add_subplot(122)
sub2.plot(offset_interval, chi2, 'b')
sub2.ticklabel_format(style = 'sci')
xlab2 = 'Offset (days)'
sub2.set_xlabel(xlab2)
ylab = r'$\chi^2$'
sub2.set_ylabel(ylab)
title = r'$\chi^2 = \sum_{i = 1}^N \frac{(D_i - M_i)^2}{\sigma^2_i}$'
sub2.set_title(title)

# period_interval = np.linspace(15.00, 22.00, 300)
# offset_interval = np.linspace(0.0, 22.00, 600)

# #Change to numpy arrays to optimize.
# z = [[f.sum_chi_squared(flux, f.box(p,o,depth,width,time),variance) for o in offset_interval]
# for p in period_interval]

# z = np.asarray(z)
# plt.imshow(z, cmap = 'gray', extent = [offset_interval[0], offset_interval[-1], period_interval[0], period_interval[-1]], origin = 'lower', interpolation='nearest')
# plt.colorbar()
# plt.xlabel('Offset (days)')
# plt.ylabel('Period (days)')
# plt.show()

plt.show()
