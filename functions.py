#File to contain the functions used in other files.

import numpy as np
import os
import pyfits

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
	
	return jdadj, obsobject, lightdata

#Function to convert the data points to a value that is relative to the 
#median of the data.
def convert_to_relative(array):
	median = np.median(array)
	return ((array / median) - 1), median

#Function to take in the flux error and return the propagated variance.
def propagated_error(array, flux_median):
	median = flux_median
	prop_var = (array / median) ** 2
	return prop_var


#Data clean-up
#The following short code is to convert all the nan values to the median.
#At this point, I am unsure whether converting to the median is the proper approach.

#box model
#period, phase are arrays from 0 to the number of
#the data point you want to generate the model.
#depth is an integer.
#width, length are arrays from 0 to the number of the data point.
def box(period, offset, depth, width, time):
	in_transit = (time - offset) % period < width
	model = np.zeros_like(time)
	model[in_transit] -= depth
	return model

#returns the sum of the chi_squared values
def sum_chi_squared(data_array, model_array, variance):
	chi2_array = ((data_array - model_array)**2) / (variance) 
	return np.sum(chi2_array)

def parameter_search():
	period = np.linspace(2.5, 7.0, 10000)
	sum_chi_squared(flux, )


#For now, the parameter serach will be defined as different functions 
#depending on the parameter for simplicity.
def period_search(chi_value_list, interval, phase, depth, width, length, clean_flux):
	chi_dict = {}
	for element in interval:
		print element
		period = np.arange(0, element)
		box_y = box(period, phase, depth, width, length)
		chi_squared_value = sum_chi_squared(clean_flux, box_y)
		chi_value_list.append(chi_squared_value)
		chi_dict[chi_squared_value] = element
	return chi_dict

#phase parameter search
def phase_search(chi_value_list, interval, period, depth, width, length, clean_flux):
	chi_dict = {}
	for element in interval:
		print element
		phase = np.arange(0, element)
		box_y = box(period, phase, depth, width, length)
		chi_squared_value = sum_chi_squared(clean_flux, box_y)
		chi_value_list.append(chi_squared_value)
		chi_dict[chi_squared_value] = element
	return chi_dict

#depth parameter search
def depth_search(chi_value_list, interval, period, phase, width, length, clean_flux):
	chi_dict = {}
	for element in interval:
		print element
		depth = element
		box_y = box(period, phase, depth, width, length)
		chi_squared_value = sum_chi_squared(clean_flux, box_y)
		chi_value_list.append(chi_squared_value)
		chi_dict[chi_squared_value] = element
	return chi_dict

#width parameter search
def width_search(chi_value_list, interval, period, phase, depth, length, clean_flux):
	chi_dict = {}
	for element in interval:
		print element
		width = np.arange(0, element)
		box_y = box(period, phase, depth, width, length)
		chi_squared_value = sum_chi_squared(clean_flux, box_y)
		chi_value_list.append(chi_squared_value)
		chi_dict[chi_squared_value] = element
	return chi_dict

#Take the chi_dict and return a list of the chi squared values
#Actually this may not work as dictionaries are in random order.
def dict_to_list(chi_dict):
	chi_value_list = chi_dict.keys()
	return chi_value_list

#Return the best fit for the parameter.
def best_parameter(chi_dict, chi_value_list):
	best_fit = chi_dict[min(chi_value_list)]
	return best_fit