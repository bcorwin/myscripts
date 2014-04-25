import datetime
import time
import serial
import smtplib
import httplib2
import msvcrt
import random
import csv

beerName = "White House Honey Ale"
lightMax = 50
ambTempMin = 64
ambTempMax = 70
contactTempMin = 68
contactTempMax = 72

emailUpdateFreq = 2 #Hours between update emails
minEmailFreq = 60 #Minimum minutes between error emails
minLog = 5 #Number of minutes between logs to google (data under this is aggregated)
 
TO = 'bscorwin@gmail.com'
GMAIL_USER = 'bcoreserver@gmail.com'
GMAIL_PASS = 'bsc0330!'

testMode = input("Test mode? (Y/N) ").upper()
if testMode != "Y":
	comPort = input("Enter COM port: ").upper()
	comPort = "COM" + comPort
	ser = serial.Serial(comPort, 9600)
else:
	beerName = "TEST"

def mainLoop():
	#Clean slate
	currTime = time.time()
	lastFailSent = currTime - 60*minEmailFreq - 1
	lastUpdateSent = currTime - 60*60*emailUpdateFreq - 1
	lastLogAttempt = currTime
	ambTemps = [0,0]
	lightVals = [0,0]
	fileName = genCompLog()
	
	print("Press ESC to cancel or 'c' for more options.")
	while True:
		forceLog = "N"
		forceUpdate = "N"
		keyChk = msvcrt.kbhit()
		if keyChk == 1:
			keyPressed = msvcrt.getch()
			if keyPressed == b'\x1b':
				print("Cancelled.")
				break
			elif keyPressed in [b'c', b'C']:
				print("Press ESC to end logging")
				print("Press 'c' for list of commands")
				print("Press 'm' to view/modify max and mins")
				print("Press 'w' to view/modify wait times")
				print("Press 'l' to log data values currently in memory")
				print("Press 's' to force update email and log <- not working yet")
				print("")
				print("*** Reading Continued ***")
			elif keyPressed in [b'm', b'M']:
				modParms()
				print("")
				print("*** Reading Continued ***")
			elif keyPressed in [b'w', b'W']:
				modWaits()
				print("")
				print("*** Reading Continued 	***")
			elif keyPressed in [b'l', b'L']:
				forceLog = "Y"
			keyChk = 0
		if ambTemps[1] == 0:
			nextLog = datetime.datetime.now() + datetime.timedelta(minutes = minLog)
			if testMode != "Y":
				print("*** Reading (Next log at: ", nextLog.strftime("%H:%M"), ") ***")
			else:
				print("*** TEST MODE ON (Next log at: ", nextLog.strftime("%H:%M"), ") ***")
		
		if testMode != "Y":
			currAmbTemp, currLightVal = readArduino()
		else:
			currAmbTemp, currLightVal = [round(random.gauss(70,20),2), round(random.gauss(10,5),2)]

		ambTemps[0] += currAmbTemp
		lightVals[0] += currLightVal
		ambTemps[1] += 1
		lightVals[1] += 1
		contactTemp = "N"

		ambTemp = round(ambTemps[0]/ambTemps[1],1)
		lightVal = round(lightVals[0]/lightVals[1],1)
		
		currTime = time.time()
		if currTime > (lastLogAttempt + 60*minLog) or forceLog == "Y":
			ambTemps = [0,0]
			lightVals = [0,0]
			
			if lightVal > lightMax or ambTemp < ambTempMin or ambTemp > ambTempMax:
				status = "Fail:"
			else:
				status = "Good"
			if lightVal > lightMax:
				status += " HL"
			if ambTemp < ambTempMin:
				status += " LAT"
			elif ambTemp > ambTempMax:
				status += " HAT"
			
			subject = ""
			body = ""
			if status[0] == "F" and currTime > (lastFailSent + 60*minEmailFreq):
				subject = "Beer vitals ('" + beerName + "') " + status
				body = genBody(beerName, status, lightVal, ambTemp, contactTemp)
				lastFailSent = currTime
				lastUpdateSent = currTime
			elif currTime > (lastUpdateSent + 60*60*emailUpdateFreq):
				subject = "Beer vitals update (" + beerName + ")"
				body = genBody(beerName, status, lightVal, ambTemp, contactTemp)
				lastUpdateSent = currTime
			
			responseStatus, responseReason = logValues2Google(beerName, lightVal, ambTemp, contactTemp, status, lightMax, ambTempMin, ambTempMax, "N", "N")
			lastLogAttempt = currTime
			if responseStatus != 200:
				print("  LOG FAILED, LOGGING LOCALLY")
				log2computer(fileName, beerName, lightVal, ambTemp, contactTemp, status, lightMax, ambTempMin, ambTempMax, "N", "N")
				body = "BEER VITALS FAILED TO BE LOGGED\n\n" + body
			else:
				print(" ", status,[ambTemp, lightVal], "logged")

			##Send Email, check if sent and update status accordingly
			if subject != "" and body != "":
				print("  EMAIL",send_email(subject,body))

		#Log data local too? or only if failed to update online? would have to sync time stamps some how, or not.

def readArduino():
	fromArduino = ser.readline()
	message = fromArduino.decode("utf-8")
	output = [float(x.strip()) for x in message.split(',')]
	return output

def genBody(beerName, status, lightVal, ambTemp, contactTemp):
	ambTemp = str(ambTemp)
	lightVal = str(lightVal)
	contactTemp = str(contactTemp)
	
	output = "\n"
	output += "Beer      = " + beerName; output += "\n"
	output += "Status    = " + status; output += "\n"
	output += "Light Val = " + lightVal; output += "\n"
	output += "Amb Temp  = " + ambTemp + " (F)"; output += "\n"
	output += "Cont Temp = " + contactTemp + " (F)"; output += "\n"
	return output
	
	
def send_email(subject,body):
	try:
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo
		smtpserver.login(GMAIL_USER, GMAIL_PASS)
		header = 'To:' + TO + '\n' + 'From: ' + GMAIL_USER
		header = header + '\n' + 'Subject:' + subject + '\n'
		msg = header + '\n' + body + ' \n\n'
		smtpserver.sendmail(GMAIL_USER, TO, msg)
		smtpserver.close()
		return "SENT"
	except:
		return "FAILED"

def nToBlank(var):
	var = str(var)
	if var.upper() == "N":
		return ""
	else:
		return var

def logValues2Google(beerName, currentLightval, ambTemp, contactTemp, status,lightMax, ambTempMin, ambTempMax, contactTempMin, contactTempMax):
	c = httplib2.HTTPSConnectionWithTimeout("docs.google.com")
	
	beerName = nToBlank(beerName)
	currentLightval = nToBlank(currentLightval)
	ambTemp = nToBlank(ambTemp)
	contactTemp = nToBlank(contactTemp)
	status = nToBlank(status)
	lightMax = nToBlank(lightMax)
	ambTempMin = nToBlank(ambTempMin)
	ambTempMax = nToBlank(ambTempMax)
	contactTempMin = nToBlank(contactTempMin)
	contactTempMax = nToBlank(contactTempMax)
	
	link = "https://docs.google.com/forms/d/1s2r_OCq0zGwgHM8G0ojLMHeqMt2yFQLq8TEsj_TKhVM/formResponse?draftResponse=%5B%2C%2C%221011733878975383640%22%5D%0D%0A"
	link += "&entry.1326982444=" + beerName.replace(" ", "%20")
	link += "&entry.1465470990=" + currentLightval
	link += "&entry.1559393995=" + contactTemp
	link += "&entry.1874487647=" + ambTemp
	link += "&entry.2063378320=" + status.replace(" ", "%20").replace(":","%3A")
	link += "&entry.211500908=" + ambTempMax
	link += "&entry.581844759=" + lightMax
	link += "&entry.65808140=" + contactTempMax
	link += "&entry.750977427=" + contactTempMin
	link += "&entry.855115684=" + ambTempMin
	link += "&fbzx=1011733878975383640&pageHistory=0"
	
	try:
		c.request("GET", link)
		response = c.getresponse()
		return[response.status, response.reason]
	except:
		return[0, "Unknown Failure"]

def modParms():
	global beerName, lightMax,ambTempMin,ambTempMax,contactTempMin,contactTempMax
	print("Enter new value or press 'ENTER' to keep as default")
	text = "Enter beer name (current = " + beerName + "):"
	key = input(text)
	if key != "":
		beerName = key
		print("New beer name = ", beerName)
	else:
		print("Value not changed")
	text = "Enter max light value (default = " + str(lightMax) + "):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			lightMax = int(key)
			print("New max light value = ", lightMax)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")
	text = "Enter min ambient light value (default = " + str(ambTempMin) +"):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			ambTempMin = int(key)
			print("New min ambient light value = ", ambTempMin)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")
	text = "Enter max ambient temp value (default = " + str(ambTempMax) +"):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			ambTempMax = int(key)
			print("New max ambient temp value = ", ambTempMax)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")
	text = "Enter min contact temp value (default = " + str(contactTempMin) +"):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			contactTempMin = int(key)
			print("New min contact temp value = ", contactTempMin)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")
	text = "Enter max contact temp value (default = " + str(contactTempMax) +"):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			contactTempMax = int(key)
			print("New max contact temp value = ", contactTempMax)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")

def modWaits():
	global emailUpdateFreq, minEmailFreq, minLog
	print("Enter new value or press 'ENTER' to keep as default")
	text = "Enter wait time in HOURS for time between update emails (default = " + str(emailUpdateFreq) + "):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			emailUpdateFreq = int(key)
			print("New update wait time = ", emailUpdateFreq)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")
	text = "Enter wait time in MINUTES for time between out of range emails (default = " + str(minEmailFreq) + "):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			minEmailFreq = int(key)
			print("New update wait time = ", minEmailFreq)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")
	text = "Enter wait time in MINUTES for time between logs to Google (default = " + str(minLog) + "):"
	key = input(text)
	if key.isnumeric():
		if int(key) >= 0:
			minLog = int(key)
			print("New update wait time = ", minLog)
		else:
			print("Not a valid number, no changes made.")
	else:
		print("Value not changed")

def genCompLog():
	fileName = "SENSOR LOG " + str(datetime.datetime.now().strftime("%Y%m%d_%H%M")) + ".csv"
	with open(fileName, 'w', newline='') as csvfile:
		logfile = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		logfile.writerow(['Timestamp'] + ['beerName']+['currentLightval']+['ambTemp']+['contactTemp']+['status']+['lightMax']+['ambTempMin']+['ambTempMax']+['contactTempMin']+['contactTempMax'])
	return fileName

def log2computer(fileName, beerName, currentLightval, ambTemp, contactTemp, status,lightMax, ambTempMin, ambTempMax, contactTempMin, contactTempMax):
	addRow = str(beerName) + "," + str(currentLightval) + "," + str(ambTemp) + "," + str(contactTemp) + "," + str(status) + "," + str(lightMax) + "," + str(ambTempMin) + "," + str(ambTempMax) + "," + str(contactTempMin) + "," + str(contactTempMax) + "\n"
	addRow = str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + "," + addRow
	fd = open(fileName,'a')
	fd.write(addRow)
	fd.close()	

#Future, try to re run code until working
try:
	mainLoop()
except:
	print("Attempting to send email...")
	subject = "!CHECK SENSOR PROGRAM NOT RUNNING DO TO UNKNOWN ERROR!"
	body = ""
	isSent = ""
	while isSent != "SENT":
		isSent = send_email(subject,body)
	print(" EMAIL", isSent)