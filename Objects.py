import math
import numpy as np
from jplephem.spk import SPK
import os

class Craft(object):

	def __init__(self, delt_t, x=0.0, y=0.0, z=0.0,
				v_x=0.0, v_y=0.0, v_z=0.0, mass=0):
		# Pos is in km
		self.pos = np.array([np.longdouble(x),
							np.longdouble(y),
							np.longdouble(z)])
		# Vol is in km/s
		self.vol = np.array([np.longdouble(v_x),
							np.longdouble(v_y),
							np.longdouble(v_z)])
		# Mass is in kg
		self.mass = mass
		# Delta_t is in days
		self.del_t = np.longdouble(delt_t) * 86400

		# Initilize non input vars
		# Initilize history of positions
		self.hist = [[np.longdouble(x)],
					[np.longdouble(y)],
					[np.longdouble(z)]]
		# Initilize force array
		self.f = np.array([np.longdouble(0),
						np.longdouble(0),
						np.longdouble(0)])
		# Initilize constants
		# Gravitational constant (6.674*10-11 N*(m/kg)2)
		self.G_const = np.longdouble(0.00000000006674)

	def force_g(self, body_mass, body_x=0.0, body_y=0.0, body_z=0.0):
		# Caculate x, y, z distances
		xdist = (self.pos[0] - body_x)
		ydist = (self.pos[1] - body_y)
		zdist = (self.pos[2] - body_z)
		# Caculate vector distance
		d = math.sqrt((xdist**2) + (ydist**2) + (zdist**2)) * 1000
		# Caculate comman force of gravity
		g_com = ((self.G_const * body_mass * self.mass) / (d**3))

		# Update forces array
		self.f -= np.array([g_com * (xdist * 1000),
							g_com * (ydist * 1000),
							g_com * (zdist * 1000)])

	# Function to step simulation based on force caculations
	def update(self):
		# Step velocity
		self.vol += np.array([(((self.f[0] / self.mass) * self.del_t)) / 1000,
							(((self.f[1] / self.mass) * self.del_t)) / 1000,
							(((self.f[2] / self.mass) * self.del_t)) / 1000])
		# Step position
		self.pos += np.array([(self.del_t * self.vol[0]),
							(self.del_t * self.vol[1]),
							(self.del_t * self.vol[2])])
		# Reset force profile
		self.f = np.array([np.longdouble(0),
						np.longdouble(0),
						np.longdouble(0)])
	
	def VV_update(self):
		"""Parameters:
		r is a numpy array giving the current position vector
		v is a numpy array giving the current velocity vector
		dt is a float value giving the length of the integration time step
		a is a function which takes x as a parameter and returns the acceleration vector as an array"""
		r_new = r + v*dt + a(r)*dt**2/2
		v_new = v + (a(r) + a(r_new))/2 * dt

	def dist(self, body_x=0.0, body_y=0.0, body_z=0.0):
		return math.sqrt(((self.pos[0] - body_x)**2) +
						((self.pos[1] - body_y)**2) +
						((self.pos[2] - body_z)**2))

	def log(self):
		self.hist[0].append(self.pos[0])
		self.hist[1].append(self.pos[1])
		self.hist[2].append(self.pos[2])
