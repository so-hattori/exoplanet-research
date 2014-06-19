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

#The following function will smoothen a graph by setting each point to
#the value obtained by generating a box around the point and calculating its average.
#array must be given with float elements at this point.
#box_half_width will determine the size of the box.
def marginalize(array, box_half_width):
	size = len(array)
	#Create an array of the same size
	marg_array = np.zeros((size))
	for indice, element in enumerate(array):
		#Maintain original values if box cannot be created around point
		if indice < box_half_width:
			marg_array[indice] = array[indice]
		#Create box around point and set it to the average of the box.
		elif indice > (box_half_width - 1) and indice < size:
			#average inside interval of box
			box_list = array[(indice-box_half_width):indice + (box_half_width + 1)]
			box_tot = sum(box_list)
			# print box_tot
			#Average of the y_elements inside the box
			box_ave = box_tot / len(box_list)
			marg_array[indice] = box_ave
		#Last element stays the same as it cannot be averaged
		marg_array[-1] = array[-1]
	return marg_array

#Function to convert the data points to a value that is relative to the 
#median of the data.
def convert_to_relative(array):
	median = np.median(array)
	for i, e in enumerate(array):
	#fractional relative flux
		array[i] = ((e - median) / median)
	return array

#Data clean-up
#The following short code is to convert all the nan values to the median.
#At this point, I am unsure whether converting to the median is the proper approach.

#The given array must meet the numpy requirements
def nan_to_median(array):
	median = np.median(array)
	#goes through all elements to check and convert np.nan to the median.
	for i, e in enumerate(array):
		if np.isnan(e) == True:
			array[i] = median
		else:
			pass
	return array

#function to check whether or not np.nan exists in an array.
def check(array):
	if np.isnan(np.sum(array)):
		return 'NaN present'
	else:
		return 'no NaN'

#box model
def box(period, phase, depth, width, length):
	#test with a list instead of an numpy array first
	y_list = []
	fixed_y = 0.0
	#insert the phase part of the graph.
	for elements in phase:
		y_list.append(fixed_y)
	#create a variable to keep the loop running for now
	run = True
	while run:
		for elements in width:
			y_list.append(fixed_y - depth)
		for elements in period:
			y_list.append(fixed_y)
		if len(y_list) >= length:
			run = False
	#Just use the following code for now because I can't figure out
	#a way to make the previous loop end when it reaches the length.
	y_end = y_list[0:length]
	return y_end

#returns the sum of the chi_squared values
def sum_chi_squared(data_array, model_array):
	end_result = 0
	chi_squared = 0
	for i, e in enumerate(data_array):
		chi_squared = (data_array[i] - model_array[i])**2
		end_result += chi_squared
	return end_result

#Iterate through and creates a dictionary that assigns the period(in data points) 
#to the appropriate chi-squared value
#poi is the parameter of interest
def parameter_search(poi, chi_value_list, interval, period, phase, depth, width, length, clean_flux):
	chi_dict = {}
	for element in interval:
		print element
		parameter = np.arange(0, element)
		#The following if/elif part can probably be optimized
		if poi == 'period':
			period = parameter
		elif poi == 'phase':
			phase = parameter
		elif poi == 'depth':
			depth = element
		elif poi == 'width':
			width = parameter
		box_y = box(period, phase, depth, width, length)
		chi_squared_value = sum_chi_squared(clean_flux, box_y)
		print chi_squared_value
		chi_value_list.append(chi_squared_value)
		chi_dict[chi_squared_value] = element
	return chi_dict

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