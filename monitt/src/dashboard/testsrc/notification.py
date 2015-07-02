# -*- coding: utf-8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from email import Utils
from email.header import Header
from email.utils import formataddr
import os, makelog

mylogger = makelog.get_logger('notification')

def send_email(error, info):
	test_path = os.getcwd()
	mylogger.info('Preparing sending email...')
	smtp_server  = "smtp.gmail.com"
	port = 587
	userid = "meeeeejin@gmail.com"
	passwd = "tkfkdgo09"
	to_user = info[1]
	from_user = "no-reply@monitt.com"
	cur_path = os.getcwd()
	html_path = cur_path + "/dashboard/testsrc/templates/mail.html"
	
	author = formataddr((str(Header('MONITT')), from_user))
	msg = MIMEMultipart("alternative")
	msg["From"] = author
	msg["To"] = to_user
	msg["Subject"] = Header(s="[MONITT] %s: %s" % (info[9], info[2]))
	msg["Date"] = Utils.formatdate(localtime = 1)

	html = open(html_path).read()
	html = html.replace("%", "%%").replace("%%s", "%s")
	error = error.split(" ||| ")
	errorstr = error[0]
	
	for i in range(1, len(error)):
		if i % 4 == 3:
			errorstr = errorstr + error[i] + "<br>"
		else:
			errorstr = errorstr + error[i]
	
	html = html % (info[0], info[7], info[8], info[2], info[3], info[2], info[4].encode('utf-8'), info[5], info[6], info[9], info[10], errorstr)

	msg.attach(MIMEText(html, 'html', _charset="utf-8"))
    
	try:
		smtp = smtplib.SMTP(smtp_server, port)
		smtp.ehlo()
		smtp.starttls()
		smtp.login(userid, passwd)
		smtp.sendmail(from_user, to_user, msg.as_string())
		smtp.quit()
		mylogger.info('Success to sene email to %s!' % to_user)
	except:
		mylogger.error('Fail to sene email to %s..' % to_user)