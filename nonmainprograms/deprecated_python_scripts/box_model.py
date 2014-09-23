#file to contain all the functions

import numpy as np
import matplotlib.pyplot as plt

# x_list = np.arange(0,100,0.5)

#define period as an array
period = np.arange(0, 4500)

#work on phase later
phase = np.arange(0, 2530)
#depth is just in integer
depth = 0.01

#define width to also be an array
width = np.arange(0, 270)

#depth is dimensionless
#all other arguments have dimensions of days
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
			if len(y_list) >= length:
				run = False
		for elements in period:
			y_list.append(fixed_y)
			if len(y_list) >= length:
				run = False
	return y_list

y_list =  box(period, phase, depth, width, 44100)
#define the length of x?
# x_list = np.arange(0, y_length)
# print x_list.shape
# plt.plot(x_list, y_list)

plt.plot(y_list)
plt.ylim(-0.015, 0.01)
plt.vlines(phase[-1],-0.015,0.01)
plt.show()