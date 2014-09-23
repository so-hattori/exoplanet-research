import numpy as np
# import matplotlib.pyplot as plt

#y_array must be given with float elements at this point.
#box_half_width will determine the size of the box.
def marginalize(y_array, box_half_width):
	size = len(y_array)
	y_marg = np.zeros((size))
	for indice, element in enumerate(y_array):
		#Keep the first few elements the same if it cannot be averaged with the box width.
		if indice < box_half_width:
			y_marg[indice] = y_array[indice]
		elif indice > (box_half_width - 1) and indice < size:
			#average inside interval of box
			box_list = y_array[(indice-box_half_width):indice + (box_half_width + 1)]
			box_tot = sum(box_list)
			# print box_tot
			#Average of the y_elements inside the box
			box_ave = box_tot / len(box_list)
			y_marg[indice] = box_ave
		#Last element stays the same as it cannot be averaged
		y_marg[-1] = y_array[-1]
	return y_marg

# y = np.array([3.,6.,7.,15.,7.,2.,5.,10.,7.,3.,9.,10.,2.,15.,9.,7.,6.,2.,3.,5.,2.])
# # print y
# # print marginalize(y,4)
# plt.plot(y, color = 'Red')
# plt.plot(marginalize(y,1), color = 'Blue')
# plt.plot(marginalize(y,2), color = 'Green')
# plt.plot(marginalize(y,3), color = 'Black')
# plt.show()

