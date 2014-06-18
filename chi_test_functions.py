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
clean_flux = f.nan_to_median(flux)
clean_flux = f.convert_to_relative(clean_flux)
length = clean_flux.shape[0]
period_time = np.linspace(first, last, 44100) - first

#define arguments for the box_model
period = np.arange(0, 4939)
phase = np.arange(0, 2529)
depth = 0.006
width = np.arange(0, 270)

#Create an empty list to store the values of chi for plotting
period_chi_value_list = []
phase_chi_value_list = []
depth_chi_value_list = []
width_chi_value_list = []

period_interval = np.arange(4900, 5000)
phase_interval = np.arange(2500, 2600)
depth_interval = np.arange(0.005, 0.020, 0.001)
width_interval = np.arange(250, 500)

period_chi_dict = f.period_search(period_chi_value_list, period_interval, phase, depth, width, length, clean_flux)
period_best_fit = f.best_parameter(period_chi_dict, period_chi_value_list)
print period_best_fit
print period_time[period_best_fit]

#Once the best fit parameter is found, update the parameters
period = np.arange(0, period_best_fit)

period_in_days = []
for i in period_interval:
	period_in_days.append(period_time[i])


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
sub2.plot(period_in_days, period_chi_value_list, color = 'black', marker = '.', markersize = 10)
sub2.ticklabel_format(useOffset = False)
xlab2 = 'Period (days)'
sub2.set_xlabel(xlab2)
ylab = r'$\chi^2$'
sub2.set_ylabel(ylab)
title = r'$\chi^2 = \sum_{i = 1}^N (D_i - M_i)^2$'
sub2.set_title(title)


plt.show()



FITSfile.close()
