import os
import pyfits
import matplotlib.pyplot as plt

#This short segment of code allows the user to input the kepler ID
#and change the working directory to the proper one. (Given that the proper local data exists)

kplr_id = raw_input('Input kepler id:')
#Hardcode for now
#kplr_id = '012506954'
path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
os.chdir(path)

# print path
# print os.getcwd()

#Code to allow the user to decide which FIT format file to generate light curve.
filename = raw_input('Input FITS file to use: ')

#Hardcode for now
#filename = 'kplr012506954-2009166043257_llc.fits'
FITSfile = pyfits.open(filename)

FITSfile.info()

dataheader = FITSfile[1].header
topheader = FITSfile[0].header
jdadj = str(dataheader["BJDREFI"])
obsobject = str(dataheader["OBJECT"])

lightdata = FITSfile[1].data

flux = lightdata.field("PDCSAP_FLUX")     

time = lightdata.field("TIME")            #Barycenter corrected Julian date

fig1 = plt.figure()
sub1 = fig1.add_subplot(111)
sub1.plot(time , flux, color="black", marker=",")
xlab = "Time (days, Julian date - %s)"%jdadj
sub1.set_xlabel(xlab)
sub1.set_ylabel("Brightness (electron flux)")
plottitle="Light Curve for %s"%obsobject
sub1.set_title(plottitle)

plt.show()

FITSfile.close()