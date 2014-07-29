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

#Rescale the flux and the error.
#The 1 sigma error given by the kepler data is converted to variance.
def rescale(flux, flux_err):
	median = np.median(flux)
	scaled_flux = (flux / median) - 1
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
	pb_model = np.zeros_like(time)
	pb_model[transit] -= depth
	return pb_model

def unity_push_box(offset, depth, width, time):


def flat_model(time):
	return np.zeros_like(time)

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
def ln_like(data_array, model_array, variance):
	chi2 = ((data_array - model_array)**2) / (variance) 
	return (-1/2)*np.sum(chi2)


#returns the sum of the chi_squared values
def sum_chi_squared(data_array, model_array, variance):
	chi2_array = ((data_array - model_array)**2) / (variance) 
	return np.sum(chi2_array)

def pre_sum(data_array, model_array):
	chi2_array = (data_array - model_array) **2
	return np.sum(chi2_array)
