import numpy as np
from jplephem.spk import SPK
import os

if not os.path.isfile('de430.bsp'):
	raise ValueError('de430.bsp Was not found!')
kernel = SPK.open('de430.bsp')
# Initilize mass
mass = np.longdouble(5972198600000000000000000)
# Initilize history of positions
hist = [[], [], []]
pos = np.array([np.longdouble(0),
				np.longdouble(0),
				np.longdouble(0)])


def getPos(time):
	"""Returns the earths position relative to the solar system barycentere
	"""
	return kernel[3, 399].compute(time)


def getRelPos(time):
	global pos
	"""Returns relitive position of the earth (which is the origin
	in an earth moon system)"""
	pos = np.array([np.longdouble(0),
					np.longdouble(0),
					np.longdouble(0)])
	return pos


def log():
	global pos
	"""log current position"""
	hist[0].append(pos[0])
	hist[1].append(pos[1])
	hist[2].append(pos[2])
