import time as t
import math

from astropy.time import Time
import numpy as np
# Import Objects
from Objects import Craft
import moon
import earth

# Generate output for plotting a sphere
def drawSphere(xCenter, yCenter, zCenter, r):
	# Draw sphere
	u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
	x = np.cos(u) * np.sin(v)
	y = np.sin(u) * np.sin(v)
	z = np.cos(v)
	# Shift and scale sphere
	x = r * x + xCenter
	y = r * y + yCenter
	z = r * z + zCenter
	return (x, y, z)

def plot(ship,planets):
	"""3d plots earth/moon/ship interaction"""
	import matplotlib.pyplot as plt
	from mpl_toolkits.mplot3d import Axes3D
	# Initilize plot
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.set_xlabel('X Km')
	ax.set_ylabel('Y Km')
	ax.set_zlabel('Z Km')
	ax.set_xlim3d(-500000, 500000)
	ax.set_ylim3d(-500000, 500000)
	ax.set_zlim3d(-500000, 500000)
	
	ax.plot(xs=ship.hist[0][0::10],
			ys=ship.hist[1][0::10],
			zs=ship.hist[2][0::10],
			zdir='z', label='ys=0, zdir=z')
	
	# Plot planet trajectory
	for planet in planets:
		ax.plot(xs=moon.hist[0],
				ys=moon.hist[1],
				zs=moon.hist[2],
				zdir='z', label='ys=0, zdir=z')
	
	# Plot Earth (plot is moon position relative to earth)
	# also plotting to scale
	(xs, ys, zs) = drawSphere(0, 0, 0, 6367.4447)
	ax.plot_wireframe(xs, ys, zs, color="r")
	
	plt.show()

def sim(startTime, endTime, step, ship, planets):
	"""Runs orbital simulation given ship and planet objects as well as start/stop times"""

	# Caculate moon planet update rate (1/10th as often as the craft)
	plan_step = int(math.ceil(((endTime - startTime) / step)/100))

	# Initilize positions of planets
	for planet in planets:
				planet.getRelPos(startTime)
				planet.log()

	for i, time in enumerate(np.arange(startTime, endTime, step)):
		# Every plan_step update the position estmation
		if (i % plan_step == 0):
			for planet in planets:
				planet.getRelPos(time)
				planet.log()

		# Update craft_vol
		for planet in planets:
			ship.force_g(planet.mass, planet.pos[0], planet.pos[1], planet.pos[2])
		ship.update()

		# Log the position of the ship every 1000 steps
		if (i % 1000) == 0:
			# Append the position to the lists
			ship.log()

		# Print status update every 100,000 steps
		if (i % 100000) == 0:
			print end_time.jd - time
			print "Dist:", ship.dist()

if __name__ == "__main__":

	# Delta time for simulations (in days)
	del_t = np.longdouble(1.0) / (24.0 * 60.0 * 60.0)

	ship = Craft(del_t, x=35786, y=1, z=1, v_x=0, v_y=4.5, v_z=0, mass=12)
	planets = [earth,moon]

	# Initilize simulation time
	start_time = Time('2015-09-01T00:00:00.123456789')
	end_time = Time('2015-09-10T00:00:00.123456789')

	# Initilize start date/time (Julian)
	time = start_time.jd
	
	sim(start_time.jd, end_time.jd, del_t, ship, planets)
	plot(ship,[moon])