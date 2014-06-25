import functions as f
import matplotlib.pyplot as plt
import numpy as np
import time as t

t0 = t.clock()

kplr_id = '008191672'
kplr_file = 'kplr008191672-2009322144938_slc.fits'
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
# period = np.arange(0, 4935)
# phase = np.arange(0, 2521)
depth = 0.006
width = np.arange(0, 270)

period_range = np.arange(2000, 12000, 10)
phase_range = np.arange(2000, 10000, 10)

#Convert the data point index to units in days.
x_tick = []
for x in period_range:
	# print x
	# print period_time[x]
	x_tick.append(period_time[x])
x_tick = np.asarray(x_tick)

period_days = []
for period in period_range:
	period_days.append(period_time[period])
period_days = np.asarray(period_days)
# y_tick = []
# for y in phase_range:
# 	y_tick.append(period_time[y])
# y_tick = np.asarray(y_tick)

phase_days = []
for phase in phase_range:
	# print phase
	# print period_time[phase]
	phase_days.append(period_time[phase])
phase_days = np.asarray(phase_days)

z = []
for i in period_range:
	line = []
	for j in phase_range:
		print i, j
		line.append(f.sum_chi_squared(clean_flux, f.box(np.arange(0, i), np.arange(0, j), depth, width, length)))
	z.append(line)
z = np.asarray(z)

t1 = t.clock()
print t1 - t0

plt.imshow(z, cmap = 'gray', aspect = 'auto', extent = (phase_days[0], phase_days[-1], period_days[0], period_days[-1]), origin = 'lower', interpolation = 'nearest')
# plt.ticklabel_format(useOffset = False)
x_label = 'Phase (days)'
plt.xlabel(x_label)
y_label = 'Period (days)'
plt.ylabel(y_label)
plt.colorbar()
plt.show()
