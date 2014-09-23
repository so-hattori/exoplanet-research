#This code generates the light curve of a given kepler object.
#Many parts of the code were written with the help from http://yourlocaltautologist.blogspot.com/2012/08/viewing-kepler-light-curves-via.html

import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np

#This short segment of code allows the user to input the kepler ID
#and change the working directory to the proper one. (Given that the proper local data exists)

kplr_id = raw_input('Input kepler id:')
path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
os.chdir(path)

# print path
# print os.getcwd()

#Code to allow the user to decide which FITS format file to generate light curve.
filename = raw_input('Input FITS file to use: ')

FITSfile = pyfits.open(filename)

#FITSfile.info()

dataheader = FITSfile[1].header
topheader = FITSfile[0].header

jdadj = str(dataheader["BJDREFI"])
obsobject = str(dataheader["OBJECT"])

lightdata = FITSfile[1].data

#Convert the data to fractional relative flux
#Currently this code is written to generate graphs for PDCSAP_FLUX.
flux = lightdata.field("PDCSAP_FLUX")
time = lightdata.field('TIME')
print time
assert 0
median = np.median(flux)
# for i, e in enumerate(flux):
# 	#fractional relative flux
# 	flux[i] = ((e - median) / median)

time = lightdata.field("TIME")            #Barycenter corrected Julian date
fig1 = plt.figure()
sub1 = fig1.add_subplot(111)
sub1.plot(time,flux, color="black", marker=",", linestyle = 'None')

#The following code is to set the labels and title
xlab = "Time (days, Kepler Barycentric Julian date - %s)"%jdadj
sub1.set_xlabel(xlab)
sub1.set_ylabel("Relative Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

plt.show()

FITSfile.close()