'''
This python script is to contain the numpy optimized functions.
While the functionality of all the functions will be the same as
the functions file, I have created a new python file for clarity.
I intend to make this script the main one and remove the functions file.
'''
import numpy as np

#1. Calculate the sum of chi2
#Both the data_array and model_array must be in the form 
#of numpy arrays.
def sum_chi2(data_array, model_array):
	chi2_array = (data_array - model_array)**2
	return np.sum(chi2_array)

