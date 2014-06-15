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
flux_type = '2'
# flux_type = raw_input('PDCSAP[1], SAP[2]:' )
flux = 0
if flux_type == '1':
	flux = lightdata.field("PDCSAP_FLUX")
elif flux_type == '2':
	flux = lightdata.field('SAP_FLUX')

#time array contains NaN values
# time = lightdata.field("TIME")            #Barycenter corrected Julian date

#clean the data and obtain moving average
clean_flux = f.nan_to_median(flux)
# marg_flux = f.marginalize(clean_flux, 200)

#convert to relative brightness
clean_flux = f.convert_to_relative(clean_flux)
# marg_flux = f.convert_to_relative(marg_flux)

#dimension of the flux array that must be the same with the model
length = clean_flux.shape[0]
print length
#define arguments for the box_model
phase = np.arange(0, 2530)
depth = 0.009
width = np.arange(0, 270)

p_interval = np.arange(4935,4945)
chi_squared_list = []
for element in p_interval:
	period = np.arange(0, element)
	box_y = f.box(period, phase, depth, width, length)
	calc_chi_squared = f.sum_chi_squared(clean_flux, box_y)
	chi_squared_list.append(calc_chi_squared)
plt.plot(p_interval, chi_squared_list, color = 'black', marker = '.', markersize = 10)
# plt.xlim(p_interval[0], p_interval[-1])
plt.ticklabel_format(useOffset = False)
plt.show()
# fig1 = plt.figure()
# sub1 = fig1.add_subplot(111)
# sub1.plot(flux, color="black", marker=",", linestyle = 'None')
# sub1.plot(box_y, color="blue", marker=",")

# #The following code is to set the labels and title
# # xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
# xlab = 'No Proper Units'
# sub1.set_xlabel(xlab)
# sub1.set_ylabel("Relative Brightness (electron flux)")
# plottitle="Light Curve for %s"%obsobject
# sub1.set_title(plottitle)

# plt.show()



FITSfile.close()
