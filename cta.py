#General: http://www.transitchicago.com/assets/1/developer_center/BusTime_Developer_API_Guide.pdf
#Bus guide: http://www.transitchicago.com/developers/bustracker.aspx

from urllib.request import urlopen
from xml.dom.minidom import parseString
from datetime import datetime

busKey = "LmmzwVvRCti3wm9F7HPXMCpuU"
trainKey = "e980207d0e7d46e185512b2813e3bb06"

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


#print(get_stopList("36", "Southbound"))
get_stopTimes("14454", "36")
	
