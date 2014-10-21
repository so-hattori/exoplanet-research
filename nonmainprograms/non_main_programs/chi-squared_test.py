import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

kplr_id = '008191672'
# kplr_id = raw_input('Input kepler id:')
path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
os.chdir(path)

#Code to allow the user to decide which FITS format file to generate light curve.
# filename = raw_input('Input FITS file to use: ')
filename = 'kplr008191672-2009322144938_slc.fits'

FITSfile = pyfits.open(filename)
dataheader = FITSfile[1].header
topheader = FITSfile[0].header
jdadj = str(dataheader["BJDREFI"])
obsobject = str(dataheader["OBJECT"])

lightdata = FITSfile[1].data

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
#This was done so that there are no NaN values in the time-domain array.
#The length variable should be inserted instead of 44100 being hard-coded.
period_time = np.linspace(first, last, 44100) - first
# print period_time[4920], period_time[4939], period_time[4960]

#clean the data and obtain moving average
clean_flux = f.nan_to_median(flux)
# marg_flux = f.marginalize(clean_flux, 200)

#convert to relative brightness
clean_flux = f.convert_to_relative(clean_flux)
# marg_flux = f.convert_to_relative(marg_flux)

#dimension of the flux array that must be the same with the model
length = clean_flux.shape[0]
# print length

#define arguments for the box_model
phase = np.arange(0, 2529)
depth = 0.009
width = np.arange(0, 270)

#This part of the code contains the main functionality.
p_interval = np.arange(4900,11000)
chi_squared_list = []
#Set up a dictionary to assign the selected period to the appropriate chi-squared.
chi_dict = {}
for element in p_interval:
	period = np.arange(0, element)
	box_y = f.box(period, phase, depth, width, length)
	calc_chi_squared = f.sum_chi_squared(clean_flux, box_y)
	chi_squared_list.append(calc_chi_squared)
	chi_dict[calc_chi_squared] = element

#return the lowest value and also the corresponding period.
chi_value_list = chi_dict.keys()
best_fit_period = chi_dict[min(chi_value_list)]
# print best_fit_period
print period_time[best_fit_period]

#The following code will convert the p_interval array into 
#the actual period in days.
period_in_days = []
for i in p_interval:
	period_in_days.append(period_time[i])


fig1 = plt.figure()
sub1 = fig1.add_subplot(121)
sub1.plot(time, clean_flux, color="black", marker=",", linestyle = 'None')
sub1.plot(time, f.box(np.arange(0, best_fit_period), phase, depth, width, length), color="blue", marker=",")

#The following code is to set the labels and title
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
# xlab = 'No Proper Units'
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

sub2 = fig1.add_subplot(122)
sub2.plot(period_in_days, chi_squared_list, color = 'black', marker = '.', markersize = 10)
sub2.ticklabel_format(useOffset = False)
xlab2 = 'Period (days)'
sub2.set_xlabel(xlab2)
ylab = r'$\chi^2$'
sub2.set_ylabel(ylab)
title = r'$\chi^2 = \sum_{i = 1}^N (D_i - M_i)^2$'
sub2.set_title(title)


plt.show()



FITSfile.close()
