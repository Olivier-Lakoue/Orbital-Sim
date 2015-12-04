import time as t
import math
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.time import Time
import numpy as np

# Import Objects
import Objects


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


def plot(ship, planets):
	"""3d plots earth/moon/ship interaction"""
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
		ax.plot(xs=planet.hist[0],
				ys=planet.hist[1],
				zs=planet.hist[2],
				zdir='z', label='ys=0, zdir=z')

	# Plot Earth (plot is moon position relative to earth)
	# also plotting to scale
	xs, ys, zs = drawSphere(0, 0, 0, 6367.4447)
	ax.plot_wireframe(xs, ys, zs, color="r")

	plt.show()


def run_simulation(start_time, end_time, step, ship, planets):
	"""Runs orbital simulation given ship and planet objects
	as well as start/stop times"""

	# Caculate moon planet update rate (1/10th as often as the craft)
	plan_step = int(math.ceil(((end_time - start_time) / step) / 100))

	# Initilize positions of planets
	for planet in planets:
				planet.update_rel_position(start_time)
				planet.log_position()

	print"Starting: {:6.2f} days of simulation".format(end_time - start_time)

	start = t.time()
	for i, time in enumerate(np.arange(start_time, end_time, step)):
		# Every plan_step update the position estmation
		if (i % plan_step == 0):
			for planet in planets:
				planet.update_rel_position(time)
				planet.log_position()

		# Update craft velocity and force vectors related to planets
		for planet in planets:
			ship.force_g(planet)

		# Update ship position according to sum of affecting forces
		ship.update()

		# Log the position of the ship every 1000 steps
		if (i % 1000) == 0:
			# Append the position to the lists
			ship.log()

		# Print status update every 100,000 steps
		if (i % 100000) == 0:
			if t.time() - start > 1:
				print ("Days remaining: {0:.2f}, ({1:.2f}% left)"
						.format((end_time - time),
						((1 - ((time - start_time) /
						(end_time - start_time))) * 100)))
				# Caculate estmated time remaining
				# Total tics
				total_tics = int((end_time - start_time) / step)
				# Tics per second till now
				tics_s = int(math.ceil(i / (t.time() - start)))
				# Estmated remaining seconds
				sec_rem = (total_tics - i) / tics_s
				m, s = divmod(sec_rem, 60)
				h, m = divmod(m, 60)
				print ("Tics per second: {0} est time remaining: {1:0>2}:{2:0>2}:{3:0>2}"
				.format(tics_s, h, m, s))
	print ("Total Tics per second: {0:.2f}"
	.format(((end_time - start_time) / step) / (t.time() - start)))
	tot_s = t.time() - start
	m, s = divmod(tot_s, 60)
	h, m = divmod(m, 60)
	print "Total time: {0:0>2.0f}:{1:0>2.0f}:{2:0>2.0f}".format(h, m, s)

if __name__ == "__main__":

	# Delta time for simulations (in days)
	del_t = np.longdouble(1.0) / (24.0 * 60.0 * 60.0)

	# Initilize objects
	ship = Objects.Craft(del_t, x=35786, y=1, z=1, v_x=0, v_y=4.5, v_z=0, mass=12)
	earth = Objects.Earth()
	moon = Objects.Moon()
	planets = [earth, moon]

	# Initilize simulation time
	start_time = Time('2015-09-10T00:00:00')
	end_time = Time('2015-10-10T00:00:00')

	# Initilize start date/time (Julian)
	time = start_time.jd
	run_simulation(start_time.jd, end_time.jd, del_t, ship, planets)

	plot(ship, [moon])
