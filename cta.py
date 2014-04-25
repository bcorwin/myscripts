#General: http://www.transitchicago.com/assets/1/developer_center/BusTime_Developer_API_Guide.pdf
#Bus guide: http://www.transitchicago.com/developers/bustracker.aspx
#Train guide: http://www.transitchicago.com/developers/traintracker.aspx

from urllib.request import urlopen
from xml.dom.minidom import parseString
from datetime import datetime
from time import sleep
from time import time


busKey = "LmmzwVvRCti3wm9F7HPXMCpuU"
trainKey = "e980207d0e7d46e185512b2813e3bb06"

import win32com.client
speaker = win32com.client.Dispatch("SAPI.SpVoice")
#Get time
# file = urlopen('http://www.ctabustracker.com/bustime/api/v1/gettime?key='+busKey)
# data = file.read()
# file.close()

# dom = parseString(data)
# xmlTag = dom.getElementsByTagName('tm')[0].toxml()
# xmlData=xmlTag.replace('<tm>','').replace('</tm>','')
# print(xmlData)

#Get Routes
# file = urlopen('http://www.ctabustracker.com/bustime/api/v1/getroutes?key='+busKey)
# data = file.read()
# file.close()

# dom = parseString(data)
# xmlTag = dom.getElementsByTagName('rt')[27].toxml()
# xmlData=xmlTag.replace('<rt>','').replace('</rt>','')
# print(xmlData)

#Get directions
# file = urlopen('http://www.ctabustracker.com/bustime/api/v1/getdirections?key='+busKey+'&rt=36')
# data = file.read()
# file.close()

# dom = parseString(data)
# xmlTag = dom.getElementsByTagName('dir')[0].toxml()
# xmlData=xmlTag.replace('<dir>','').replace('</dir>','')
# print(xmlData)

#Convert Tag to Variable:
def tag2var(elmlist,tagname):
	out = elmlist.getElementsByTagName(tagname)[0].toxml().replace('<'+tagname+'>','').replace('</'+tagname+'>','')
	return out

#Get stops
def get_stopList(rt,dir):
	output = []
	file = urlopen('http://www.ctabustracker.com/bustime/api/v1/getstops?key='+busKey+'&rt='+rt+'&dir='+dir)
	data = file.read()
	file.close()

	allStops = parseString(data)
	stopTags = allStops.getElementsByTagName('stop')
	for stopTag in stopTags:
		stpid = tag2var(stopTag,'stpid')
		stpnm = tag2var(stopTag,'stpnm')
		stpnm = stpnm.replace('&amp;', '&')
		output.append([stpid,stpnm])
	return output

def get_stopTimes(stpid, rt):
	file = urlopen('http://www.ctabustracker.com/bustime/api/v1/getpredictions?key='+busKey+'&rt='+rt+'&stpid='+stpid)
	data = file.read()
	file.close()

	allTimes = parseString(data)
	timeTags = allTimes.getElementsByTagName('prd')
	
	for timeTag in timeTags:
		tmstmp = tag2var(timeTag, 'tmstmp')
		typ = tag2var(timeTag, 'typ')
		stpid = tag2var(timeTag, 'stpid')
		stpnm = tag2var(timeTag, 'stpnm')
		vid = tag2var(timeTag, 'vid')
		dstp = tag2var(timeTag, 'dstp')
		rt = tag2var(timeTag, 'rt')
		rtdir = tag2var(timeTag, 'rtdir')
		#rtdst = tag2var(timeTag, 'rtdst')
		prdtm = tag2var(timeTag, 'prdtm')
		
		wait = datetime.strptime(prdtm, "%Y%m%d %H:%M") - datetime.strptime(tmstmp, "%Y%m%d %H:%M")
		wait = int(wait.seconds / 60)
		keep = [typ, rtdir, wait]
		print(keep)

def get_trainArrivals(mapid="", stpid="", max = 10):
	if stpid != "":
		url = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=" + trainKey + "&stpid=" + str(stpid) + "&max=" + str(max)
	elif mapid != "":
		url = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=" + trainKey + "&mapid=" + str(mapid) + "&max=" + str(max)
	else:
		print("ERROR: Missing required input")
		return
	
	file = urlopen(url)
	data = file.read()
	file.close()
	dir1 = [[-1,""]]
	dir2 = [[-1,""]]
	
	allTimes = parseString(data)
	timeTags = allTimes.getElementsByTagName('eta')
	tmst = tag2var(allTimes, 'tmst')
	
	for timeTag in timeTags:
		arrT = tag2var(timeTag, 'arrT')
		destNm = tag2var(timeTag, 'destNm')
		destSt = tag2var(timeTag, 'destSt')
		flags = tag2var(timeTag, 'flags')
		heading = tag2var(timeTag, 'heading')
		isApp = tag2var(timeTag, 'isApp')
		isDly = tag2var(timeTag, 'isDly')
		isFlt = tag2var(timeTag, 'isFlt')
		isSch = tag2var(timeTag, 'isSch')
		lat = tag2var(timeTag, 'lat')
		lon = tag2var(timeTag, 'lon')
		prdt = tag2var(timeTag, 'prdt')
		rn = tag2var(timeTag, 'rn')
		rt = tag2var(timeTag, 'rt')
		staId = tag2var(timeTag, 'staId')
		staNm = tag2var(timeTag, 'staNm')
		stpDe = tag2var(timeTag, 'stpDe')
		stpId = tag2var(timeTag, 'stpId')
		trDr = tag2var(timeTag, 'trDr')
		
		waitTm = datetime.strptime(arrT, "%Y%m%d %H:%M:%S") - datetime.strptime(tmst, "%Y%m%d %H:%M:%S")
		waitTm = str(round(waitTm.seconds / 60))
		keep = [waitTm, isApp, isDly, isFlt, isSch]
		if dir1[0][0] in [-1, trDr]:
			dir1[0][0] = trDr
			dir1[0][1] = stpDe
			dir1.append(keep)
		elif dir2[0][0] in [-1, trDr]:
			dir2[0][0] = trDr
			dir2[0][1] = stpDe
			dir2.append(keep)
		else:
			print("Error")
	return [staNm, dir1, dir2]


#print(get_stopList("36", "Southbound"))
#get_stopTimes("14454", "36")
def show_trainArrivals(mapid="", stpid=""):
	nextTrains = get_trainArrivals(mapid=mapid, stpid=stpid)
	print("")
	print(nextTrains[0])
	print("-", nextTrains[1][0][1])
	for tr in nextTrains[1][1:]:
		text = "-- "
		if tr[1] == "1":
			text += "Due"
		elif tr[2] == "1":
			text += "Delayed"
		else:
			text += tr[0] + " mins"
		if tr[4] == "1":
			text += "*"
		print(text)
	if len(nextTrains[2][0][1]) > 0:
		print("-", nextTrains[2][0][1])
		for tr in nextTrains[2][1:]:
			text = "-- "
			if tr[1] == "1":
				text += "Due"
			elif tr[2] == "1":
				text += "Delayed"
			else:
				text += tr[0] + " mins"
			if tr[4] == "1":
				text += "*"
			print(text)
	print("")
	print(nextTrains)

def say_nextArrival(stpid="", last=""):
	#Add a 'followed by' message
	nextTrains = get_trainArrivals(stpid=stpid, max = 1)
	text = "Next train from " + nextTrains[0] + " with " + nextTrains[1][0][1] + " "
	end = ""
	waitTm, isApp, isDly, isFlt, isSch = nextTrains[1][1]
	if isSch == "1":
		end += "is scheduled to arrive in "
		if int(waitTm) != 1:
			end += waitTm + " minutes"
		else:
			end += waitTm + " minute"
	elif isApp == "1":
		end += "is due"
	elif isDly == "1":
		end += "is delayed"
	else:
		if int(waitTm) != 1:
			end += "is in " + waitTm + " minutes"
		else:
			end += "is in " + waitTm + " minute"
	text += end
	if last != end.upper():
		speaker.Speak(text)
	return end.upper()
	
	

#show_trainArrivals(mapid="41200")
#show_trainArrivals(stpid="30229")
start = time()
last = ""

while time() <= start + 60*10:
	#last = say_nextArrival(stpid="30229", last = last)
	last = say_nextArrival(stpid="30011", last = last)
	sleep(5)
speaker.Speak("Train announcements turned off.")
