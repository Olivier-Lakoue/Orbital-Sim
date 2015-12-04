import math
import numpy as np
from jplephem.spk import SPK
import os


class Craft(object):
	# Gravitational constant (6.67408*10-11 N*(m/kg)2)
	GRAVITATIONAL_CONSTANT = 6.67408 * 10**-11

	def __init__(self, delt_t, x=0.0, y=0.0, z=0.0,
				v_x=0.0, v_y=0.0, v_z=0.0, mass=0):
		"""Units:
		Position: km
		Volume: km/s
		Mass: kg
		Delta_t: days
		"""
		self.pos = np.array([np.longdouble(x),
							np.longdouble(y),
							np.longdouble(z)])

		self.vol = np.array([np.longdouble(v_x),
							np.longdouble(v_y),
							np.longdouble(v_z)])

		self.mass = mass

		self.del_t = np.longdouble(delt_t) * 86400

		# Initilize non input vars
		# Initilize history of positions
		self.hist = [[np.longdouble(x)],
					[np.longdouble(y)],
					[np.longdouble(z)]]
		# Initilize force array
		self.force = np.zeros(3, dtype=np.longdouble)
		# Initilize constants
		self.VELOCITY_FACTOR = self.del_t / self.mass / 1000
		self.FORCE_FACTOR = self.GRAVITATIONAL_CONSTANT * self.mass / 1000000

	def force_g(self, body):
		"""Updates the force the body has on this craft."""

		dist = self.pos - body.pos
		gravity_component = (self.FORCE_FACTOR * body.mass /
							((dist[0]**2 + dist[1]**2 + dist[2]**2)**1.5))

		# Update forces array
		self.force -= np.dot(dist, gravity_component)

	# Function to step simulation based on force caculations
	def update(self):
		"""Steps up simulation based on force calculations."""
		# Step velocity
		self.vol += np.dot(self.force, self.VELOCITY_FACTOR)
		# Step position
		self.pos += np.dot(self.vol, self.del_t)

		# Reset force profile
		self.force = np.zeros(3, dtype=np.longdouble)

	def VV_update(self):
		"""Parameters:
		r is a numpy array giving the current position vector
		v is a numpy array giving the current velocity vector
		dt is a float value giving the length of the integration time step
		a is a function which takes x as a parameter and returns
		the acceleration vector as an array"""
		r_new = r + v * dt + a(r) * dt**2 / 2
		v_new = v + (a(r) + a(r_new)) / 2 * dt

	def dist(self, body_x=0.0, body_y=0.0, body_z=0.0):
		return math.sqrt(((self.pos[0] - body_x)**2) +
						((self.pos[1] - body_y)**2) +
						((self.pos[2] - body_z)**2))

	def log(self):
		self.hist[0].append(self.pos[0])
		self.hist[1].append(self.pos[1])
		self.hist[2].append(self.pos[2])


class CelestialBody(object):

	def __init__(self, mass, position=None):
		if not os.path.isfile('de430.bsp'):
			raise ValueError('de430.bsp Was not found!')
		self.kernel = SPK.open('de430.bsp')

		self.mass = np.longdouble(mass)
		self.hist = [[], [], []]
		if position is not None:
			self.pos = position
		else:
			self.pos = []

	def get_position(self, time):
		"""Returns the position relative to the solar system barycentere"""
		return self.kernel[3, self.KERNAL_CONSTANT].compute(time)

	def log_position(self):
		"""log current position"""
		self.hist[0].append(self.pos[0])
		self.hist[1].append(self.pos[1])
		self.hist[2].append(self.pos[2])


class Earth(CelestialBody):

	KERNAL_CONSTANT = 399

	def __init__(self):
		super(Earth, self).__init__(5.9721986 * 10**24)

	def update_rel_position(self, time):
		"""Returns relitive position of the earth (which is the origin
		in an earth moon system)"""

		self.pos = np.zeros(3, dtype=np.longdouble)
		return self.pos


class Moon(CelestialBody):

	KERNAL_CONSTANT = 301

	def __init__(self):
		super(Moon, self).__init__(7.34767309 * 10**22)

	def update_rel_position(self, time):
		"""Returns relitive position of the moon (relative to the earth)"""
		self.pos = self.get_position(time) - self.kernel[3, 399].compute(time)
		return np.array([np.longdouble(self.pos[0]),
						np.longdouble(self.pos[1]),
						np.longdouble(self.pos[2])])
