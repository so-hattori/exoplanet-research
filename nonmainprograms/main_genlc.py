#This is the updated and compact version of the generate_ligh_curve program.
#The functionality is the same with the added option of choosing PDCSAP or SAP for the flux.

import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
#functions is another python file
import functions as f

kplr_id = raw_input('Input kepler id:')
path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
os.chdir(path)

#Code to allow the user to decide which FITS format file to generate light curve.
filename = raw_input('Input FITS file to use: ')

FITSfile = pyfits.open(filename)
dataheader = FITSfile[1].header
topheader = FITSfile[0].header
jdadj = str(dataheader["BJDREFI"])
obsobject = str(dataheader["OBJECT"])

lightdata = FITSfile[1].data

#Allows the user to choose between PDCSAP or SAP to generate light curve.
flux_type = raw_input('PDCSAP[1], SAP[2]:' )
flux = 0
if flux_type == '1':
	flux = lightdata.field("PDCSAP_FLUX")
elif flux_type == '2':
	flux = lightdata.field('SAP_FLUX')

#time array contains NaN values
time = lightdata.field("TIME")            #Barycenter corrected Julian date

#clean the data and obtain moving average
clean_flux = f.nan_to_median(flux)
marg_flux = f.marginalize(clean_flux, 200)

#convert to relative brightness
clean_flux = f.convert_to_relative(clean_flux)
marg_flux = f.convert_to_relative(marg_flux)

fig1 = plt.figure()
sub1 = fig1.add_subplot(111)
sub1.plot(time, flux, color="black", marker=",", linestyle = 'None')
sub1.plot(time, marg_flux, color="blue", marker=",", linestyle = 'None')

#The following code is to set the labels and title
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

plt.show()

FITSfile.close()
