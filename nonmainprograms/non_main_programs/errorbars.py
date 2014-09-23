import os
import pyfits
import matplotlib.pyplot as plt
import numpy as np
import functions as f
import time as t

kplr_id = '008191672'
kplr_file = 'kplr008191672-2010355172524_llc.fits'

#Given the kplr ID and filename, open the FITS file and extract the data.
jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)

time, flux, flux_err = f.fix_data(lightdata)

flux, flux_median = f.convert_to_relative(flux)
variance = f.propagated_error(flux_err, flux_median)
error = variance ** 0.5

plt.errorbar(time, flux, error, fmt = ',k')
plt.show()