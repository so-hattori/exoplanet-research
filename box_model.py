#file to contain all the functions

import numpy as np
import matplotlib.pyplot as plt

# x_list = np.arange(0,100,0.5)

#define period as an array
period = np.arange(0, 365)

#work on phase later

#depth is just in integer
depth = 0.2

#define width to also be an array
width = np.arange(0, 25)

#depth is dimensionless
#all other arguments have dimensions of days
def box(period, phase, depth, width):
	#test with a list instead of an numpy array first
	y_list = []
	fixed_y = 2.0
	#create a variable to keep the loop running for now
	run = 0
	while run <= 5:
		for elements in period:
			y_list.append(fixed_y)
		for elements in width:
			y_list.append(fixed_y - depth)
		run += 1
	return y_list

y_list =  box(period, 0, depth, width)
#define the length of x?
# x_list = np.arange(0, y_length)
# print x_list.shape
# plt.plot(x_list, y_list)

plt.plot(y_list)
plt.ylim(1.0, 2.5)
plt.show()