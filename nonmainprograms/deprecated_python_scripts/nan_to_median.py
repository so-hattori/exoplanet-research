#The following short code is to convert all the nan values to the median.
#At this point, I am unsure whether converting to the median is the proper approach.
import numpy as np

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

# x = np.array([0,1,2,3,np.nan])

# print x
# print check(x)

# xnew = nan_to_median(x)
# print xnew
# print check(xnew)
