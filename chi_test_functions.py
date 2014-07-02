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

print time
assert 0

flux, flux_median = f.convert_to_relative(flux)
variance = f.propagated_error(flux_err, flux_median)

# period = 3.5
# offset = 1.0
depth = 0.007
width = 0.25

period_interval = 10 ** np.linspace(np.log10(2.5), np.log10(10), 700)
offset_intervals = [np.arange(0, p, 0.01) for p in period_interval]

#The following grid is structured in a way where there is a list 
#for all the chi2 values obtained for each period. For EACH period
#there exists a nested list where the values are the chi2 values obtained 
#for each offset it iterates through.
#This structure is equivalent to a 2D array. The rows are the periods and 
#the columns are offsets.
chi2_grid = [[f.sum_chi_squared(flux, f.box(p, o, depth, width, time), variance)
              for o in offsets] for p, offsets in zip(period_interval, offset_intervals)]

#This map function iterates through the chi2_grid and finds the minimum for each period.
#It means it is finding the lowest chi2 for each period, which is equal to selecting
#the chi2 value with the best offset for each period.
#It generates a list(array) of the the lowest chi2 values for each period.
#The length of the list is equal to the number of periods.
chi2_values = map(np.min, chi2_grid)

#Return the index of the lowest chi2 in the chi2_values list.
#This index corresponds to the best period as the first dimension of
#both arrays are the same.
lowest_chi2_index = np.argmin(chi2_values)

#Return the best period.
parameter_best_fit = period_interval[lowest_chi2_index]
period = parameter_best_fit
print 'Best period: ', period

#The first index finds the location of the best offset corresponding to 
#the best period. The second index is the location of the best offset inside the best period.
offset = offset_intervals[lowest_chi2_index][np.argmin(chi2_grid[lowest_chi2_index])]
print 'Best offset: ', offset

fig1 = plt.figure()
sub1 = fig1.add_subplot(221)
sub1.plot(time, flux, ',k')
sub1.plot(time, f.box(period, offset, depth, width, time), 'b')
#The following code is to set the labels and title
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
# xlab = 'No Proper Units'
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

sub2 = fig1.add_subplot(222)
sub2.plot(period_interval, chi2_values, '.')
sub2.ticklabel_format(style = 'sci')
xlab2 = 'Period (days)'
sub2.set_xlabel(xlab2)
ylab = r'$\chi^2$'
sub2.set_ylabel(ylab)
title = r'$\chi^2 = \sum_{i = 1}^N \frac{(D_i - M_i)^2}{\sigma^2_i}$'
sub2.set_title(title)

#Create plot zoomed around the best chi2 value.
dense_period_interval = np.linspace(period-0.003, period+0.001, 1000)
dense_offset_interval = [np.arange(0, p, 0.01) for p in dense_period_interval]

dense_chi2_grid = [[f.sum_chi_squared(flux, f.box(p, o, depth, width, time), variance)
              for o in offsets] for p, offsets in zip(dense_period_interval, dense_offset_interval)]
dense_chi2_values = map(np.min, dense_chi2_grid)
lowest_chi2_index = np.argmin(dense_chi2_values)
period = dense_period_interval[lowest_chi2_index]

#Rewrite this entire section later. Make it into a function.
dense_period_interval = np.linspace(period-0.0001, period+0.0001, 1000)
dense_offset_interval = [np.arange(0, p, 0.01) for p in dense_period_interval]

dense_chi2_grid = [[f.sum_chi_squared(flux, f.box(p, o, depth, width, time), variance)
              for o in offsets] for p, offsets in zip(dense_period_interval, dense_offset_interval)]
dense_chi2_values = map(np.min, dense_chi2_grid)


#Sub3 is a subplot that is a plot that is zoomed around the minimum of the chi2 graph.
sub3 = fig1.add_subplot(223)
sub3.plot(dense_period_interval, dense_chi2_values, 'r')
sub3.ticklabel_format(useOffset = False)
sub3.set_xlabel('Period (days)')
sub3.set_ylabel(r'$\chi^2$')
ymin = np.min(chi2_values) - 1
ymax = ymin + 8

t1 = t.clock()
endt = t1 - t0
print endt

plt.show()
