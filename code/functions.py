#File to contain the functions used in other files.

import numpy as np
import os
import pyfits
import kplr
import copy
import matplotlib.pyplot as plt

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
			'''Consult Hogg if this is the proper fix'''
			value = 1.0
			''''''
			depth = 0.0
		else:
			depth = 1.0 - value
	#Calculate the chi2 when inside the transit window
	chi2 = (data_in_transit - value)**2 - (data_in_transit-1.0)**2
	ln_like = -0.5*np.sum(chi2*inv_var_in_transit)
	return depth, depth_variance, ln_like

#Return the transit boolean
def get_transit_boolean(offset, width, complete_time):
	ll = offset < complete_time+width/2.0
	ul = complete_time < (offset+width/2.0)
	return ll*ul

#Return a model given the depth, transit_window, and complete_time
def return_model(depth, transit_window, complete_time):
	model = np.ones(len(complete_time))
	model[transit_window] -= depth
	return model


#median filter
def median_filter(array, box_width):
	new_array = np.zeros([array.shape[0]])
	for i, e in enumerate(array):
		box = array[max(0, i-box_width) : min(i+box_width, len(array))]
		value = np.median(box)
		new_array[i] = value
	print new_array.shape
	return new_array

# #injection function
# def injection(period, offset, depth, width, time, flux):
# 	in_transit = (time - offset) % period < width
# 	flux[in_transit] -= depth
# 	return flux

# def raw_injection(period, offset, depth, width, time, flux):
# 	in_transit = (time - offset) % period < width
# 	flux[in_transit] = flux[in_transit] * (1-depth)
# 	return flux

# #log likelihood
# def ln_like(data_array, model_array, inv_variance):
# 	chi2 = ((data_array - model_array)**2)*(inv_variance)
# 	return (-1/2)*np.sum(chi2)

#Function to return the window of peaks.
#For now, this will be trivially implemented by
#finding the peaks in the likelihood array, removing that window of data points
#from the array, and repeating the process.
#The inputs are the ln_likelihood array, complete time array,time_grid array, 
#the width of the window, and the number of peaks to find.
#The output should be a list containing the "transit window" boolean arrays, and the peaks. 
def peak_finder(likelihood_array, complete_time_array, time_grid_array, width, depth_array):
	complete_time_list_of_boolean_arrays = []
	time_grid_list_of_boolean_arrays = []
	peaks = []
	peak_index = []
	tol_depth = 10.0**(-3)
	#Create a deepcopy of the likelihood array.
	copy_likelihood_array = copy.copy(likelihood_array)
	while True:
		index_of_max_likelihood = np.argmax(copy_likelihood_array)
		#Suppress the rest of the code if the depth is too small (d < (10^-3)) THIS MAY BE CHANGED LATER.
		if (depth_array[index_of_max_likelihood] < tol_depth):
			# print "DEPTH IS TOO SMALL"
			break
		else:
			time_at_max_likelihood = time_grid_array[index_of_max_likelihood]
			#Just for sake, let's store the peak values in an array.
			peaks.append(time_at_max_likelihood)
			peak_index.append(index_of_max_likelihood)
			#Since the two lines above will find the peak in the likelihood array,
			#We now need to find the corresponding time windows for both the 
			#complete time array, and also the coarse time_grid array.
			complete_time_lower_end = complete_time_array < (time_at_max_likelihood+width)
			complete_time_upper_end = (time_at_max_likelihood-width) < complete_time_array
			complete_time_transit_boolean = complete_time_lower_end*complete_time_upper_end
			# complete_time_transit_window = complete_time_array[complete_time_transit_window]
			complete_time_list_of_boolean_arrays.append(complete_time_transit_boolean)

			time_grid_lower_end = time_grid_array < (time_at_max_likelihood+width)
			time_grid_upper_end = (time_at_max_likelihood-width) < time_grid_array
			time_grid_transit_boolean = time_grid_lower_end*time_grid_upper_end
			# time_grid_transit_window = time_grid_array[time_grid_transit_boolean]
			time_grid_list_of_boolean_arrays.append(time_grid_transit_boolean)

			#Now we need to modify the likelihood array so that the interval around the previously
			#found peaks are NOT found again.
			#A trivial implementation of this (possible need to modify later)
			#can be easily done by setting all the values found inside the "transit window"
			#to be 0.
			#There is a huge problem with using this trivial method for small widths.
			#The problem is that there is still a chance that the second best peak is still
			#within the area around the largest transit dip.
			copy_likelihood_array[time_grid_transit_boolean] = 0

	return np.array(complete_time_list_of_boolean_arrays), np.array(time_grid_list_of_boolean_arrays), peaks, peak_index

#Function to graph the peaks
def plot_peaks(complete_boolean_list, grid_boolean_list, time, med_flux, ferr, time_grid, ln_like_array, depth_array, transit_boolean_array, peak_index, pp):
	for i in xrange(len(complete_boolean_list)):
		# print i
		transit_complete_time = time[complete_boolean_list[i]]
		transit_flux = med_flux[complete_boolean_list[i]]
		transit_error = ferr[complete_boolean_list[i]]

		transit_grid_time = time_grid[grid_boolean_list[i]]
		transit_likelihood = ln_like_array[grid_boolean_list[i]]
		x_lims= [transit_grid_time[0], transit_grid_time[-1]]

		best_depth = depth_array[peak_index[i]]
		# print best_depth
		best_transit_window = transit_boolean_array[peak_index[i]]
		best_model = return_model(best_depth, best_transit_window, time)
		window_best_model = best_model[complete_boolean_list[i]]

		fig = plt.figure()
		graph_flux = fig.add_subplot(211)
		graph_flux.errorbar(transit_complete_time, transit_flux, yerr=transit_error, fmt = '.')
		graph_flux.plot(transit_complete_time, window_best_model, 'r')		
		graph_flux.set_xlabel("Days")
		graph_flux.set_ylabel("Median-filtered Flux")
		graph_flux.set_title("Peak: {0}".format(i+1))
		graph_flux.set_xlim(x_lims)
		graph_flux.grid()
		graph_flux.locator_params(axis = 'x', nbins = 8)

		graph_like = fig.add_subplot(212)
		graph_like.plot(transit_grid_time, transit_likelihood, '.b')
		graph_like.set_xlabel("Days")
		graph_like.set_ylabel("Ln_Likelihood")
		graph_like.set_xlim(x_lims)
		graph_like.grid()
		graph_like.locator_params(axis = 'x', nbins = 8)
		pp.savefig()

def find_nearest_index(array, value):
	idx = (np.abs(array-value)).argmin()
	return idx

def mid_points(complete_time_array, width, peaks):
	midpoint = (peaks[0]+peaks[1])/2
	mid_index = find_nearest_index(complete_time_array, midpoint)

	mid_complete_time_value = complete_time_array[mid_index]

	complete_time_lower_end = complete_time_array < (mid_complete_time_value+10*width)
	complete_time_upper_end = (mid_complete_time_value-10*width) < complete_time_array
	complete_time_mid_boolean = complete_time_lower_end*complete_time_upper_end

	return complete_time_mid_boolean, midpoint

def plot_midpoint(complete_time_mid_boolean, time, med_flux, ferr, pp, midpoint):
		mid_complete_time = time[complete_time_mid_boolean]
		mid_flux = med_flux[complete_time_mid_boolean]
		mid_error = ferr[complete_time_mid_boolean]

		fig = plt.figure()
		sub = fig.add_subplot(111)
		sub.errorbar(mid_complete_time, mid_flux, yerr=mid_error, fmt = '.', alpha=0.7)
		sub.vlines(midpoint,mid_flux.min(), mid_flux.max(),linewidth=1, color='r')
		sub.set_xlabel("Day")
		sub.set_ylabel("Median-Filtered Flux")
		sub.set_title("Possbile Occultation(Flux around midpoint between 2 transit events.)")
		sub.grid()
		pp.savefig()
