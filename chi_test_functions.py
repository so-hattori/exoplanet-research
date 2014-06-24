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
kplr_file = 'kplr008191672-2009322144938_slc.fits'

#Given the kplr ID and filename, open the FITS file and extract the data.
jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)

#Allows the user to choose between PDCSAP or SAP to generate light curve.
flux_type = '1'
# flux_type = raw_input('PDCSAP[1], SAP[2]:' )
flux = 0
if flux_type == '1':
	flux = lightdata.field("PDCSAP_FLUX")
elif flux_type == '2':
	flux = lightdata.field('SAP_FLUX')

#time array contains NaN values
time = lightdata.field("TIME")            #Barycenter corrected Julian date
first, last = time[0], time[-1]
clean_flux = f.nan_to_median(flux)
clean_flux = f.convert_to_relative(clean_flux)
length = clean_flux.shape[0]
period_time = np.linspace(first, last, length) - first

#define arguments for the box_model
period = np.arange(0, 4935)
phase = np.arange(0, 2600)
depth = 0.006
width = np.arange(0, 261)

#Create an empty list to store the values of chi for plotting
period_chi_value_list = []
phase_chi_value_list = []
depth_chi_value_list = []
width_chi_value_list = []

period_interval = np.arange(4700, 10000)
phase_interval = np.arange(2400, 5000)
depth_interval = np.arange(-0.020, 0.020, 0.001)
width_interval = np.arange(250, 10000)

#Used in plotting the x label
x_tick = []
xlab2 = 0

#Refactoring to if/elif for the 4 parameters. This part should be heavily optimized later.
choose_parameter = raw_input('Period[1], Phase[2], Depth[3], Width[4]: ')
if choose_parameter == '1':
	#Period 
	period_chi_dict = f.period_search(period_chi_value_list, period_interval, phase, depth, width, length, clean_flux)
	period_best_fit = f.best_parameter(period_chi_dict, period_chi_value_list)
	print 'Best fit data point-wise: ', period_best_fit
	print 'Best fit in days: ', period_time[period_best_fit]
	period = np.arange(0, period_best_fit)
	chi_value_list = period_chi_value_list
	for i in period_interval:
		x_tick.append(period_time[i])
	xlab2 = 'Period (days)'

elif choose_parameter == '2':
	#Phase
	phase_chi_dict = f.phase_search(phase_chi_value_list, phase_interval, phase, depth, width, length, clean_flux)
	phase_best_fit = f.best_parameter(phase_chi_dict, phase_chi_value_list)
	print 'Best fit data point-wise: ', phase_best_fit
	print 'Best fit in days:', period_time[phase_best_fit]
	phase = np.arange(0, phase_best_fit)
	chi_value_list = phase_chi_value_list
	for i in phase_interval:
		x_tick.append(period_time[i])
	xlab2 = 'Phase (days)'

elif choose_parameter == '3':
	#Depth
	depth_chi_dict = f.depth_search(depth_chi_value_list, depth_interval, period, phase, width, length, clean_flux)
	depth_best_fit = f.best_parameter(depth_chi_dict, depth_chi_value_list)
	print depth_best_fit
	depth = depth_best_fit
	chi_value_list = depth_chi_value_list
	for i in depth_interval:
		x_tick.append(i)
	xlab2 = 'Depth (unitless)'

elif choose_parameter == '4':
	#Width
	width_chi_dict = f.width_search(width_chi_value_list, width_interval, period, phase, depth, length, clean_flux)
	width_best_fit = f.best_parameter(width_chi_dict, width_chi_value_list)
	print width_best_fit
	print period_time[width_best_fit]
	width = np.arange(0, width_best_fit)
	chi_value_list = width_chi_value_list
	for i in width_interval:
		x_tick.append(period_time[i])
	xlab2 = 'Width (days)'

#Once the best fit parameter is found, update the parameters
# period = np.arange(0, period_best_fit)
# phase = np.arange(0, phase_best_fit)
# depth = depth_best_fit
# width = np.arange(0, width_best_fit)

# period_in_days = []
# for i in period_interval:
# 	period_in_days.append(period_time[i])


fig1 = plt.figure()
sub1 = fig1.add_subplot(121)
sub1.plot(time, clean_flux, color="black", marker=",", linestyle = 'None')
sub1.plot(time, f.box(period, phase, depth, width, length), color="blue", marker=",")

#The following code is to set the labels and title
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
# xlab = 'No Proper Units'
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

sub2 = fig1.add_subplot(122)
#Refactor the second argument of the following line so that it simplifies.
sub2.plot(x_tick, chi_value_list, color = 'black', marker = '.', markersize = 10)
sub2.ticklabel_format(useOffset = False)
# xlab2 = 'Period (days)'
sub2.set_xlabel(xlab2)
ylab = r'$\chi^2$'
sub2.set_ylabel(ylab)
title = r'$\chi^2 = \sum_{i = 1}^N (D_i - M_i)^2$'
sub2.set_title(title)

t1 = t.clock()
endt = t1 - t0
print endt

plt.show()
