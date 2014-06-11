import numpy as np
import matplotlib.pyplot as plt

#y_array must be given with float elements at this point.
#box_half_width will determine the size of the box.
def marginalize(y_array, box_half_width):
	size = len(y_array)
	y_marg = np.zeros((size))
	for indice, element in enumerate(y_array):
		#Keep the end elements the same as I cannot think of a way to average it now
		y_marg[0] = y_array[0]
		y_marg[-1] = y_array[-1]
		if indice > 0 and indice < 9:
			#averaging around -1 to +1 elements for now
			box_list = y_array[(indice-box_half_width):indice + (box_half_width + 1)]
			box_tot = sum(box_list)
			#Average of the y_elements inside the box
			box_ave = box_tot / len(box_list)
			#Next, we need to add the element(y value) of interest and the box_ave
			# and divide by 2 to obtain the marginalized average
			marg_ave = (y_array[indice] + box_ave) / 2
			y_marg[indice] = marg_ave
	return y_marg


x = np.arange(0,10)
y = np.array([3.,5.,7.,15.,7.,2.,5.,10.,7.,3.])
print y
print marginalize(y,1)
plt.plot(y, color = 'Red')
plt.plot(marginalize(y,1), color = 'Blue')
plt.show()

