#!/usr/bin/env python
import sys
import requests
import urllib
import time
import datetime
import subprocess
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
# run this script with screen, you can put in rc.local like: /usr/bin/screen -dmS Website /usr/bin/python /root/reboot.py
# for sid and vmname, you can find this info by clicking the "i" info tab - sid is "server id" and the vmname is the 'c' string on the main screen of panel.cloudatcost.
# if you've renamed the server, click "console" on the server you'd like to use in this script as soon as the box pops up, look for "sid" and "vmname" and 
# the initial popup box url should be something like: https://panel.cloudatcost.com/console5/ or along those lines
sid = '' # see above
vmname = '' # see above
username = ''  # make sure you sub %40 for @, so: yourname%40gmail.com
password = ''
OURL = '' # site to monitor, include https://
alertemail = '' # gmail email address to send alerts on, may need to configure your gmail
alertpass = '' # gmail password
alertto = '' # what email do you want to send alerts to? Can be the same as alert email
####################################
# do not change things below here: #
####################################
csrftoken = ''
zcsrftoken = ''
headers = {'Host': 'panel.cloudatcost.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Referer': 'https://panel.cloudatcost.com/login.php', 'Cookie': 'THISISNOTTHECOOKIE'}
def getcloudatcostCookie():
	try:
		global csrftoken
		global zcsrftoken
		global headers
		global username
		global password
		zheaders = {'Host': 'panel.cloudatcost.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Referer': 'https://panel.cloudatcost.com/login.php', 'Content-Type': 'application/x-www-form-urlencoded'}
		client = requests.session()
		login_data = 'username=' + username + '&password=' + password + '&failedpage=login-failed-2.php&submit=Login'# Fill in your email and password here
		URL = 'https://panel.cloudatcost.com/manage-check2.php' #URL to get cookies
#		URL = 'http://127.0.0.1/manage-check2.php'
		try:
			client.post(URL, data=login_data, headers=zheaders)
		except:
			time.sleep(240)
			try:
				client.post(URL, data=login_data, headers=zheaders)
			except:
				zzzfile = open("RebootLog.txt","a+")
				zzzfile.write("panel.cloudatcost.com is down, exiting... " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n")
				zzzfile.close()
				print "panel.cloudatcost.com is down, exiting..."
				sys.exit()
		if 'PHPSESSID' in client.cookies: # search for cookie 
			csrftoken = client.cookies['PHPSESSID'] # pulls cookie data and assigns to csrftoken
		zcsrftoken = 'PHPSESSID=' + csrftoken + '; path=/' # In this case the cookie is in the headers, so have to build on top of Cookie:, looks like: Cookie: PHPSESSID=lkjsdflkjsdfoiwe88u; but in headers
		headers['Cookie'] = zcsrftoken # updates dictionary with new cookie 
		return 1
	except:
		return 2
def doreboot():
	global headers
	global vmname
	global sid
	SURL = 'https://panel.cloudatcost.com/panel/_config/powerCycle.php?sid=' + sid + '&vmname=' + vmname + '&cycle=2' #URL to do reboot
#	SURL = 'http://127.0.0.1' 
	client = requests.session()
	try:
		client.get(SURL, headers=headers)
	except:
		time.sleep(240)
		try:
			client.get(SURL, headers=headers)
		except:
			qqqfile = open("RebootLog.txt","a+")
			qqqfile.write("panel.cloudatcost.com is down, exiting... " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n")
			qqqfile.close()
			print "panel.cloudatcost.com is down, exiting..."
			sys.exit()
	time.sleep(1)
	return True
def main(self):
	global OURL
	global alertemail
	global alertpass
	global alertto
	fail = self
	client = requests.session()
	try:
		r = client.get(OURL)
	except:
		fail += 1
		if fail == 2:
			cdtnfile = open("RebootLog.txt","a+")
			cdtnfile.write("Reboot Time: " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n")
			cdtnfile.close()
			try:
				fromaddr = alertemail
				toaddr = alertto
				msg = MIMEMultipart()
				msg['From'] = fromaddr
				msg['To'] = toaddr
				msg['Subject'] = "Website Reboot Occurring"
				body = "Reboot Time: " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n"
				msg.attach(MIMEText(body, 'plain'))
				server = smtplib.SMTP('smtp.gmail.com', 587)
				server.starttls()
				server.login(fromaddr, alertpass)
				text = msg.as_string()
				server.sendmail(fromaddr, toaddr, text)
				server.quit()
			except:
				rtndfile = open("RebootLog.txt","a+")
				rtndfile.write("Email Attempt Failed: " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n")
				rtndfile.close()
			if getcloudatcostCookie() == 1:
				doreboot()
			else:
				dtndfile = open("RebootLog.txt","a+")
				dtndfile.write("Reboot Attempt Failed: " + datetime.datetime.now().strftime("%I:%M:%S %p") + " trying one more time" + "\n")
				dtndfile.close()
				time.sleep(240) #240
				if getcloudatcostCookie() == 1:
					doreboot()
			fail = 0
			time.sleep(900) #900
		time.sleep(240) #240
		main(fail)
	if r.status_code == 200:
#		print "200"
		fail = 0
		print "returned 200 " + datetime.datetime.now().strftime("%I:%M:%S %p")
		time.sleep(10) #10
	else:
		fail += 1
#		print "fail"
	if fail == 2:
		ctnfile = open("RebootLog.txt","a+")
		ctnfile.write("Reboot Time: " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n")
		ctnfile.close()
		try:
			fromaddr = alertemail
			toaddr = alertto
			msg = MIMEMultipart()
			msg['From'] = fromaddr
			msg['To'] = toaddr
			msg['Subject'] = "Website Reboot Occurring"
			body = "Reboot Time: " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n"
			msg.attach(MIMEText(body, 'plain'))
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login(fromaddr, alertpass)
			text = msg.as_string()
			server.sendmail(fromaddr, toaddr, text)
			server.quit()
		except:
			rtnfile = open("RebootLog.txt","a+")
			rtnfile.write("Email Attempt Failed: " + datetime.datetime.now().strftime("%I:%M:%S %p") + "\n")
			rtnfile.close()
		if getcloudatcostCookie() == 1:
			doreboot()
		else:
			dtnfile = open("RebootLog.txt","a+")
			dtnfile.write("Reboot Attempt Failed: " + datetime.datetime.now().strftime("%I:%M:%S %p") + " trying one more time" + "\n")
			dtnfile.close()
			time.sleep(240) #240
			if getcloudatcostCookie() == 1:
				doreboot()
		fail = 0
#		print "Fail loop"
		time.sleep(900) #900
	time.sleep(290) #290
	main(fail)
main(0)
