import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
from marginalize_function import *
#This short segment of code allows the user to input the kepler ID
#and change the working directory to the proper one. (Given that the proper local data exists)

kplr_id = raw_input('Input kepler id:')
path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
os.chdir(path)

# print path
# print os.getcwd()

#Code to allow the user to decide which FIT format file to generate light curve.
filename = raw_input('Input FITS file to use: ')
FITSfile = pyfits.open(filename)
FITSfile.info()

dataheader = FITSfile[1].header
topheader = FITSfile[0].header
jdadj = str(dataheader["BJDREFI"])
obsobject = str(dataheader["OBJECT"])

lightdata = FITSfile[1].data

flux = lightdata.field("PDCSAP_FLUX")

np.set_printoptions(threshold ='nan')
#print flux

print marginalize(flux, 100)

# plt.plot(flux, color = 'Black', marker = ',', linestyle = 'None')
plt.plot(marginalize(flux, 100), color = 'Red', marker = ',', linestyle = 'None')
plt.show()