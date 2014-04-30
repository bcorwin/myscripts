import datetime
import math
import matplotlib.pyplot as plt
from matplotlib import animation


 
#Source: http://www.stargazing.net/kepler/circle.html

#Epoch JD 2450320.5 - 0h UT 25th August 1996
#Format: n (daily motion), L (epoch), a (semi-major axis), symbol
orbitalElements = {
"MERCURY" : [4.092385,281.18017,0.3870975, u'\u263F'],
"VENUS" : [1.602159,20.17002,0.7233235, u'\u2640'],
"EARTH" : [0.9855931,333.58600,1.0000108, u'\u2295'],
"MARS" : [0.5240218,73.77336,1.5237131, u'\u2642'],
"JUPITER" : [0.08310024,292.64251,5.202427, u'\u2643'],
"SATURN" : [0.03333857,8.91324,9.561943, u'\u2644'],
"URANUS" : [0.01162075,298.87491,19.30425, "U"],
"NEPTUNE" : [0.005916098,297.58472,30.27750, "N"]}

zodiac = {
'ARIES'			: [0, 'AR', u'\u2648'],
'TAURUS'		: [30, 'TA', u'\u2649'],
'GEMINI'		: [60, 'GE', u'\u264A'],
'CANCER'		: [90, 'CA', u'\u264B'],
'LEO'			: [120, 'LE', u'\u264C'],
'VIRGO'			: [150, 'VI', u'\u264D'],
'LIBRA'			: [180, 'LI', u'\u264E'],
'SCORPIO'		: [210, 'SC', u'\u264F'],
'SAGITTARIUS'	: [240, 'SA', u'\u2650'],
'CAPRICORN'		: [270, 'CA', u'\u2651'],
'AQUARIUS'		: [300, 'AQ', u'\u2652'],
'PISCES'		: [330, 'PI', u'\u2653']}


# hle - is the heliocentric longitude of the Earth
# ne  - is the daily motion of the Earth
# D   - is the number of days since the epoch of the elements
# Le  - is the longitude of the Earth at the epoch of the elements
# Degrees = ne * D + Le mod 360

def daysSinceEpoch(date, epoch = datetime.datetime(1996,8,25)):
	out = date - epoch
	return out.days

def getHelioPos(planet = "EARTH", date=""):
	n = orbitalElements[planet.upper()][0]
	d = daysSinceEpoch(date=date)
	l = orbitalElements[planet.upper()][1]
	degs = (n*d + l) % 360
	return degs

def getPos(date = ""):
	global helioPos
	helioPos = {}
	if date == "":
		date = datetime.datetime.utcnow()
	helioPos["VENUS"] = getHelioPos(planet = "VENUS", date = date)
	helioPos["MERCURY"] = getHelioPos(planet = "MERCURY", date = date)
	helioPos["EARTH"] = getHelioPos(planet = "EARTH", date = date)
	helioPos["MARS"] = getHelioPos(planet = "MARS", date = date)
	# helioPos["JUPITER"] = getHelioPos(planet = "JUPITER", date = date)
	# helioPos["SATURN"] = getHelioPos(planet = "SATURN", date = date)
	return date

def plotPos(date=""):
	date = getPos(date=date)

	fig = plt.figure()
	ax = plt.axes(polar = True)
		
	xticks = []
	for z in zodiac:
		xticks.append(math.pi*zodiac[z][0]/180)
		centerRad = math.pi*(zodiac[z][0] + 15)/180
		xval = (.94*math.cos(centerRad) + 1)/2
		yval = (.94*math.sin(centerRad) + 1)/2
		ax.annotate(zodiac[z][2],
            xy=(0, 0),
            xytext=(xval, yval),
            textcoords='axes fraction',
			fontsize = 16,
			fontname = 'ARIAL UNICODE MS',
            horizontalalignment='center',
            verticalalignment='center',
			rotation = zodiac[z][0] - 75
            )
	#ax.axes.set_xticks(xticks)
	ax.axes.set_xticks([])
	ax.axes.set_xticklabels([])
	ax.axes.set_yticklabels([])
	
	plt.polar(0,0, marker = "", ls = ".")
	plt.text(0, 0, u'\u2609', fontname='ARIAL UNICODE MS', size=16, va='center', ha='center', clip_on=True)
	yticks = []
	for curr in helioPos:
		r = orbitalElements[curr.upper()][2]
		yticks.append(r)
		theta = helioPos[curr.upper()]*math.pi/180
		plt.polar(theta,r, marker = "", ls = ".")
		plt.text(theta, r, orbitalElements[curr][3], fontname='ARIAL UNICODE MS', size=16, va='center', ha='center', clip_on=True)

	ax.set_ylim((0, max(yticks) + .4))
	ax.axes.set_yticks(yticks)
	title = date.strftime("%Y-%m-%d %Z")
	plt.title(title)
	plt.show()

def prompt():
	print("Type 'exit' to stop.")
	while 1==1:
		indate = input("Enter date or leave blank for today (YYYYMMDD):")
		if indate != "":
			if indate.lower() == "exit":
				print("Exiting...")
				break
			try:	
				indate = datetime.datetime(int(indate[0:4]), int(indate[4:6]), int(indate[6:8]))
				plotPos(date = indate)
			except:
				print("Invalid input. Try again.")
		else:
			plotPos()
prompt()

#Animate
# stdt = datetime.datetime.utcnow()
# getPos(date = stdt)
# fig = plt.figure()
# ax = plt.axes(polar = True)

# yticks = []
# for curr in helioPos:
	# yticks.append(orbitalElements[curr.upper()][2])
# ax.set_ylim((0, max(yticks) + .4))
# ax.axes.set_yticks(yticks)
# ax.axes.set_yticklabels([])

# ax.axes.set_xticks([])
# ax.axes.set_xticklabels([])


# ss, = ax.plot([], [], marker = "o", ls = ".")

def getvalues(date = ""):
	getPos(date = date)
	r=[0]
	theta=[0]
	symbol = [u'\u2609']
	for curr in helioPos:
		rAdd = orbitalElements[curr.upper()][2]
		thetaAdd = helioPos[curr.upper()]*math.pi/180
		
		r.append(rAdd)
		theta.append(thetaAdd)
		symbol.append(orbitalElements[curr.upper()][3])
	return theta, r, symbol

def init():
	ss.set_data([], [])
	return ss,

def animate(i):
	plotDate = stdt + datetime.timedelta(days = i)
	theta,r, symbol = getvalues(date = plotDate)
	ss.set_data(theta, r)
	title = plotDate.strftime("%Y-%m-%d %Z")
	return ss,

#anim = animation.FuncAnimation(fig, animate, init_func=init, frames=30, interval=1, blit=True)
#plt.show()