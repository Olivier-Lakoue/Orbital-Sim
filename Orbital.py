import time as t
import math

from astropy.time import Time
from jplephem.spk import SPK
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

#open planatary position files
kernel = SPK.open('de430.bsp')

#Constants
del_t = np.longdouble(1.0)/(24.0*60.0*60.0) #Delta time for simulations (in days)
earth_mass = np.longdouble(5972198600000000000000000) #mass of earth
moon_mass = np.longdouble(7.34767309*10**22) #mass of the moon
moon_t = np.longdouble(1.0)/(24.0) #moon pos update rate

# Generate output for plotting a sphere
def drawSphere(xCenter, yCenter, zCenter, r):
    #draw sphere
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x=np.cos(u)*np.sin(v)
    y=np.sin(u)*np.sin(v)
    z=np.cos(v)
    # shift and scale sphere
    x = r*x + xCenter
    y = r*y + yCenter
    z = r*z + zCenter
    return (x,y,z)

class Craft(object):
	def __init__(self, delt_t, x=0.0, y=0.0, z=0.0, 
				 v_x=0.0, v_y=0.0, v_z=0.0, mass=0):
		#pos is in km
		self.pos = np.array([np.longdouble(x), 
							 np.longdouble(y), 
							 np.longdouble(z)])
		#vol is in km/s
		self.vol = np.array([np.longdouble(v_x), 
							 np.longdouble(v_y), 
							 np.longdouble(v_z)])
		#mass is in kg
		self.mass = mass
		#deltat is in days
		self.del_t = np.longdouble(delt_t)*86400

			#initilize non input vars
		#initilize history of positions
		self.hist = [[np.longdouble(x)],
					 [np.longdouble(y)],
					 [np.longdouble(z)]]
		#initilize force array
		self.f = np.array([np.longdouble(0),
						   np.longdouble(0), 
						   np.longdouble(0)])
			#Initilize constants
		#gravitational constant (6.674*10-11 N*(m/kg)2)
		self.G_const = np.longdouble(0.00000000006674)
		
	def force_g(self, body_mass,body_x=0.0,body_y=0.0,body_z=0.0):
		#Caculate x, y, z distances
		xdist = (self.pos[0]-body_x)
		ydist = (self.pos[1]-body_y)
		zdist = (self.pos[2]-body_z)
		#Caculate vector distance
		d = math.sqrt( (xdist**2) + (ydist**2) + (zdist**2))*1000
		#Caculate comman force of gravity
		g_com = ((self.G_const*body_mass*self.mass)/(d**3))
		
		#Update forces array
		self.f -= np.array([
		g_com*(xdist*1000),
		g_com*(ydist*1000),
		g_com*(zdist*1000)])
	
	#Function to step simulation based on force caculations
	def update(self):
		#Step velocity
		self.vol += np.array([
		(((self.f[0]/self.mass)*self.del_t))/1000,
		(((self.f[1]/self.mass)*self.del_t))/1000,
		(((self.f[2]/self.mass)*self.del_t))/1000])
		#Step position
		self.pos += np.array([
		(self.del_t*self.vol[0]),
		(self.del_t*self.vol[1]),
		(self.del_t*self.vol[2])])
		#Reset force profile
		self.f = np.array([np.longdouble(0), 
						   np.longdouble(0), 
						   np.longdouble(0)])
	
	def dist(self,body_x=0.0,body_y=0.0,body_z=0.0):
		return math.sqrt( ((self.pos[0]-body_x)**2) + 
						  ((self.pos[1]-body_y)**2) + 
						  ((self.pos[2]-body_z)**2))
	
	def log(self):
		self.hist[0].append(self.pos[0])
		self.hist[1].append(self.pos[1])
		self.hist[2].append(self.pos[2])


#Initilize plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X Km')
ax.set_ylabel('Y Km')
ax.set_zlabel('Z Km')
ax.set_xlim3d(-500000, 500000)
ax.set_ylim3d(-500000, 500000)
ax.set_zlim3d(-500000, 500000)

ship = Craft(del_t,x=35786,y=1,z=1,v_x=0, v_y=4.5, v_z=0, mass=12)
#Initilize pos arrays [[x],[y],[z]] (km)
moon_pos = [[],[],[]]
#Initilize simulation time
start_time = Time('2015-09-10T00:00:00.123456789')
end_time = Time('2016-09-10T00:00:00.123456789')
#22
#Initilize start date/time (Julian)
time = start_time.jd

#caculate moon update rate 
moon_del_t = int(math.ceil((((end_time.jd-start_time.jd)/del_t)/
				((end_time.jd-start_time.jd)/moon_t)) / 10.0)) * 10

#Run sim
i = 0
now = t.time()
print time
moon_curr_pos = kernel[3,301].compute(time) - kernel[3,399].compute(time)
print moon_del_t
while (time < end_time.jd):
	if (i%moon_del_t == 0):
		# Caculate final position (moon-earth barycentere)
		moon_curr_pos = kernel[3,301].compute(time) - kernel[3,399].compute(time)
		moon_pos[0].append(moon_curr_pos[0])
		moon_pos[1].append(moon_curr_pos[1])
		moon_pos[2].append(moon_curr_pos[2])
	#Update craft_vol
	ship.force_g(earth_mass)
	ship.force_g(moon_mass,moon_curr_pos[0],moon_curr_pos[1],moon_curr_pos[2])
	ship.update()
	
	if (i % 1000) == 0:
		#append the position to the lists
		ship.log()
	
	if (i % 100000) == 0:
		print end_time.jd-time
		print "Dist:",ship.dist()
	i += 1
	time += del_t
print ship.hist[0][-1],ship.hist[1][-1],ship.hist[2][-1]
print ((end_time.jd-start_time.jd)/del_t)/(t.time()-now)

ax.plot(xs=ship.hist[0][0::10], 
		ys=ship.hist[1][0::10], 
		zs=ship.hist[2][0::10], 
		zdir='z', label='ys=0, zdir=z')
	
#Plot moon trajectory
ax.plot(xs=moon_pos[0], 
		ys=moon_pos[1], 
		zs=moon_pos[2], 
		zdir='z', label='ys=0, zdir=z')

#Plot Earth (plot is moon position relative to earth)
#also plotting to scale
(xs,ys,zs) = drawSphere(0,0,0,6367.4447)
ax.plot_wireframe(xs, ys, zs, color="r")

plt.show()