import numpy as np
from jplephem.spk import SPK
import os

if not os.path.isfile('de430.bsp'):
	raise ValueError('de430.bsp Was not found!')
kernel = SPK.open('de430.bsp')
# Initilize mass
mass = np.longdouble(7.34767309 * 10**22)
# Initilize history of positions
hist = [[],[],[]]
pos = []

def getPos(time):
	"""Returns the moons position relative to the solar system barycentere"""
	global pos
	pos = kernel[3, 301].compute(time)
	return pos
def getRelPos(time):
	"""Returns relitive position of the moon (relative to the earth)"""
	global pos
	pos = kernel[3, 301].compute(time) - kernel[3, 399].compute(time)
	return np.array([np.longdouble(pos[0]),
					np.longdouble(pos[1]),
					np.longdouble(pos[2])])
def log():
	"""log current position"""
	global pos
	global hist
	hist[0].append(pos[0])
	hist[1].append(pos[1])
	hist[2].append(pos[2])