import functions as f
import matplotlib.pyplot as plt
import numpy as np
import time as t

t0 = t.clock()

kplr_id = '008191672'
kplr_file = 'kplr008191672-2009322144938_slc.fits'
jdadj, obsobject, lightdata = f.openfile(kplr_id, kplr_file)

time, flux, flux_err = f.fix_data(lightdata)
flux, variance = f.rescale(flux, flux_err)
time -= np.min(time)

depth = 0.00650010001
width = 0.177046694669

period_interval = np.arange(2.00, 8.0, 0.03)
offset_intervals = np.arange(0.00, 7.2, 0.01)

#Change to numpy arrays to optimize.
z = [[f.sum_chi_squared(flux, f.box(p,o,depth,width,time),variance) for o in offset_intervals]
for p in period_interval]

#print the time
print t.clock() - t0

z = np.asarray(z)
plt.imshow(z, cmap = 'gray', extent = [offset_intervals[0], offset_intervals[-1], period_interval[0], period_interval[-1]], origin = 'lower', interpolation='nearest')
plt.colorbar()
plt.xlabel('Offset (days)')
plt.ylabel('Period (days)')
plt.show()