#File to contain the functions used in other files.

import numpy as np
import os
import pyfits
import kplr

#Function to return multiple arrays of the required values.
#The input is the ID of the star and also the size of the 
#median filtering.
def return_arrays(kplr_id, filter_size):
	client = kplr.API()
	star = client.star(kplr_id)
	lcs = star.get_light_curves(short_cadence=False)
	#Figure out the number of data sets so that the size of the
	#array can be set.
	size = len(lcs)
	time_array = np.zeros(size)
	flux_array = np.zeros(size)
	ferr_array = np.zeros(size)
	var_array = np.zeros(size)
	med_flux_array = np.zeros(size)
	#To use in indexing the array
	i = 0
	for lc in lcs:
		with lc.open() as f:
			hdu_data = f[1].data
			time, flux, ferr = fix_data(hdu_data)
			time_array[i] = time
			flux_array[i] = flux
			median = median_filter(flux, filter_size)
			ferr_array[i] = ferr/median
			var_array[i] = (ferr/median)**2
			med_flux_array[i] = flux/median
		i += 1
	time = np.concatenate(time_array)
	flux = np.concatenate(flux_array)
	med_flux = np.concatenate(med_flux_array)
	variance = np.concatenate(var_array)
	ferr = np.concatenate(ferr_array)
	return time, flux, med_flux, variance, ferr


#function to open the FITS format file given kepler id and filename.
def openfile(kplr_id, kplr_file):
	path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
	os.chdir(path)

	FITSfile = pyfits.open(kplr_file)
	dataheader = FITSfile[1].header
	topheader = FITSfile[0].header
	jdadj = str(dataheader['BJDREFI']) # the part that needs to be subtracted for julian date
	obsobject = str(dataheader['OBJECT']) # the ID of the observed object
	lightdata = FITSfile[1].data #the part of the FITS file where all the data is stored.
	FITSfile.close()	
	#Choose the data you want returned by commenting out either of the next two lines.
	return jdadj, obsobject, lightdata
	# return lightdata

def comb_openfile(kplr_id, kplr_filenamelist):
	path = '/Users/SHattori/.kplr/data/lightcurves/%s' %kplr_id
	os.chdir(path)

	lightdata_list = []
	for kplr_file in kplr_filenamelist:
		FITSfile = pyfits.open(kplr_file)
		dataheader = FITSfile[1].header
		topheader = FITSfile[0].header
		jdadj = str(dataheader['BJDREFI']) # the part that needs to be subtracted for julian date
		obsobject = str(dataheader['OBJECT']) # the ID of the observed object
		lightdata = FITSfile[1].data #the part of the FITS file where all the data is stored.
		lightdata_list.append(lightdata)
		FITSfile.close()
	return lightdata_list

#Create an optimized version of obtaining kplr data with only the ID.
def kplr_list(kplr_id):
	client = kplr.API()
	star = client.star(kplr_id)
	lcs = star.get_lightcurves(short_cadence = False)
	time, flux, flux_err = [], [], []
	for lc in lcs:
		with lc.open() as f:
		# The lightcurve data are in the first FITS HDU.
			hdu_data = f[1].data
			time.append(hdu_data["time"])
			flux.append(hdu_data["pdcsap_flux"])
			flux_err.append(hdu_data["pdcsap_flux_err"])
	return time, flux, flux_err



#function to handle removing Nan values in the arrays
def fix_data(lightdata):
	time = lightdata.field('TIME')
	flux = lightdata.field('PDCSAP_FLUX')
	flux_err = lightdata.field('PDCSAP_FLUX_ERR')
	m = np.isfinite(time) * np.isfinite(flux) * np.isfinite(flux_err)
	flux = flux[m]
	time = time[m]
	flux_err = flux_err[m]
	return time, flux, flux_err

def remove_nan(time, flux, ferr):
	m = np.isfinite(time) * np.isfinite(flux) * np.isfinite(ferr)
	flux = flux[m]
	time = time[m]
	ferr = ferr[m]
	return time, flux, ferr

def comb_data(lightdata_list):
	time_list = []
	flux_list = []
	variance_list = []
	for lightdata in lightdata_list:
		time, flux, flux_err = fix_data(lightdata)
		#rescale the flux and convert to flux_err
		flux, variance = rescale(flux, flux_err)
		time_list.append(time)
		flux_list.append(flux)
		variance_list.append(variance)
	comb_time = np.concatenate(time_list)
	comb_flux = np.concatenate(flux_list)
	comb_variance = np.concatenate(variance_list)
	return comb_time, comb_flux, comb_variance

#Create a function that combines the data without normalization.
def nonnorm_data(lightdata_list):
	time_list = []
	flux_list = []
	variance_list = []
	for lightdata in lightdata_list:
		time, flux, flux_err = fix_data(lightdata)
		#rescale the flux and convert to flux_err
		# flux, variance = rescale(flux, flux_err)
		time_list.append(time)
		flux_list.append(flux)
		variance_list.append((flux_err**2))
	comb_time = np.concatenate(time_list)
	comb_flux = np.concatenate(flux_list)
	comb_variance = np.concatenate(variance_list)
	return comb_time, comb_flux, comb_variance


#Rescale the flux and the error.
#The 1 sigma error given by the kepler data is converted to variance.
def rescale(flux, flux_err):
	median = np.median(flux)
	scaled_flux = (flux / median)
	scaled_variance = (flux_err / median) ** 2
	return scaled_flux, scaled_variance

def unity_normalize(flux, flux_err):
	median = np.median(flux)
	unity_flux = flux / median
	scaled_variance = (flux_err / median) ** 2
	return unity_flux, scaled_variance

#Document later
def box(period, offset, depth, width, time):
	in_transit = (time - offset) % period < width
	model = np.zeros_like(time)
	model[in_transit] -= depth
	return model

#Push box model
def push_box_model(offset, depth, width, time):
	lower_limit = offset < time
	upper_limit = time < offset+width
	transit = lower_limit * upper_limit
	pb_model = np.ones_like(time)
	pb_model[transit] -= depth
	return pb_model

#Create a function that generates a model with the optimal depth
def opt_depth_push_model(data_array, offset, width, time, inverse_variance):
	depth, depth_variance, ln_like = get_depth_and_ln_like(data_array, offset, width, time, inverse_variance)
	pb_model = np.ones_like(time) # Create an array of the same size at time and all values initialzed at one.
	pb_model[transit] -= depth
	return pb_model

def get_depth_and_ln_like(data_array, offset, width, time, inverse_variance):
	ll = offset < time + (width/2.0)
	ul = time < (offset+width/2.0)
	transit = ll*ul #Boolean array with True at transit times
	#We need to find the optimal depth from the above information.
	#This will be done by assigning the depth to be the average value
	#for the values inside the transit window for the data_array.
	data_in_transit = data_array[transit]
	inv_var_in_transit = inverse_variance[transit]
	#I need to ask Hogg or Dan whether it's better to use the average value or the median value.
	depth_variance = 0
	if data_in_transit.shape[0] == 0:
		depth = 0.0
	else:
		#If coincedentally the mean inside the window is
		#larger than 1.0, we need to assign the depth to be 0.
		#value = np.mean(data_in_transit) #Calculate with inverse variance
		depth_variance = 1.0/np.sum(inv_var_in_transit)
		value = np.sum(data_in_transit*inv_var_in_transit) * depth_variance
		if value > 1.0:
			depth = 0.0
		else:
			depth = 1.0 - value
	#Calculate the chi2 when inside the transit window
	chi2 = (data_in_transit - value)**2 - (data_in_transit-1.0)**2
	ln_like = -0.5*np.sum(chi2*inv_var_in_transit)
	return depth, depth_variance, ln_like


#median filter
def median_filter(array, box_width):
	new_array = np.zeros([array.shape[0]])
	for i, e in enumerate(array):
		box = array[max(0, i-box_width) : min(i+box_width, len(array))]
		value = np.median(box)
		new_array[i] = value
	print new_array.shape
	return new_array

#moving average filter
def ma_filter(array, box_width):
	new_array = np.zeros([array.shape[0]])
	for i, e in enumerate(array):
		if i > box_width:
			box = array[i-box_width : i+box_width]
			value = np.sum(box) / box.shape[0]
		else:
			value = e
		new_array[i] = value
	return new_array


def flat_model(time):
	return np.ones_like(time)

#injection function
def injection(period, offset, depth, width, time, flux):
	in_transit = (time - offset) % period < width
	flux[in_transit] -= depth
	return flux

def raw_injection(period, offset, depth, width, time, flux):
	in_transit = (time - offset) % period < width
	flux[in_transit] = flux[in_transit] * (1-depth)
	return flux

#log likelihood
def ln_like(data_array, model_array, inv_variance):
	chi2 = ((data_array - model_array)**2)*(inv_variance)
	return (-1/2)*np.sum(chi2)

#Create a test function to return a relative ln_like without 
#taking into account the variance.
def pre_ln_like(data_array, model_array):
	chi2 = (data_array - model_array)**2
	return (-1/2)*np.sum(chi2)


#returns the sum of the chi_squared values
def sum_chi_squared(data_array, model_array, variance):
	chi2_array = ((data_array - model_array)**2) / (variance) 
	return np.sum(chi2_array)

def pre_sum(data_array, model_array):
	chi2_array = (data_array - model_array) **2
	return np.sum(chi2_array)

#generate vertical lines
def vertical_lines(inj_period, time, plot_designation, inj_width, ylim_limits):
	integers = np.arange(-5,5,1)
	inj_times = integers * inj_period
	low_limit_time = inj_times > time.min()
	high_limit_time = inj_times < time.max()
	time_limits = low_limit_time * high_limit_time
	inj_times = inj_times[time_limits]
	for i in inj_times:
		plot_designation.vlines(i+(inj_width/2), ylim_limits[0], ylim_limits[-1], 'r')
