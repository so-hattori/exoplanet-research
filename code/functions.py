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
	time_list, flux_list, med_flux_list, var_list, ferr_list = [], [], [], [], []
	for lc in lcs:
		with lc.open() as f:
			hdu_data = f[1].data
			time, flux, ferr = fix_data(hdu_data)
			time_list.append(time)
			flux_list.append(flux)
			median = median_filter(flux, filter_size)
			ferr_list.append(ferr/median)
			var_list.append((ferr / median)**2)
			med_flux_list.append(flux / median)
			time = np.concatenate(time_list)
	flux = np.concatenate(flux_list)
	med_flux = np.concatenate(med_flux_list)
	variance = np.concatenate(var_list)
	ferr = np.concatenate(ferr_list)
	return time, flux, med_flux, variance, ferr


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
		value = 1.0
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
