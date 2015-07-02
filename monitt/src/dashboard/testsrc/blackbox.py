# -*- coding: utf-8 -*-

import sys, yaml, requests, json, re, os, base64, datetime
import MySQLdb, random, string
import logging
import notification, cron, makelog

db = MySQLdb.connect(host="localhost", user="root", passwd="qwer1234", db="blackbox")
cur = db.cursor()
fail_list = []
test_info = []
mylogger = makelog.get_logger('blackbox')

# read a test case file from command line argument
def readFile(filepath):
	mylogger.info('Reading test case...')

	try:
		f = open(filepath).read()
	except:
		mylogger.error('Cannot find file %s', filepath)
		sys.exit(-1)
	mylogger.info('Success to read %s', filepath)

	f = f.replace('\t', '')
	js = yaml.load(f)

	fileExtension = os.path.splitext(filepath)[1]
	if fileExtension != '.json':
		mylogger.error('Unproper file format: %s', filepath)
		sys.exit(-1)

	return js

# parse the given test case json by dot 
def parseByDot(obj, ref):
	val = obj
	for key in ref.split('.'):
			val = val[key]
	return val

# parse nested json
def parseNested(obj, ref):
	tmp = {}
	extract(obj, tmp)

	for k, v in tmp.iteritems():
		if k == ref:
			v = v.replace("\\", "").replace("\'", "").replace("\"", "")
			return v

# extract a dictionary (key, value) from nested json
def extract(DictIn, Dictout):
    for key, value in DictIn.iteritems():
        if isinstance(value, dict): # If value itself is dictionary
            extract(value, Dictout)
        elif isinstance(value, list): # If value itself is list
            for i in value:
            	if type(i) == str:
            		Dictout[key] = i
                else:
                	extract(i, Dictout)
        else:
			if key in Dictout:
				Dictout[key] = repr(Dictout[key]) + '|' + repr(value)
			else:
				Dictout[key] = repr(value)

# send actual request using parsed request data
def request(obj, secretkey):
	mylogger.info('Preparing API request...')

	method = parseByDot(obj, 'Req.Method')
	url = parseByDot(obj, 'Req.URL')
	parameter = parseByDot(obj, 'Req.URLParameter')
	header = parseByDot(obj, 'Req.Header')
	body = parseByDot(obj, 'Req.Body')
	timeout = float(parseByDot(obj, 'ExpectedRes.ResponseTime'))/float(1000)
	failcheck = 0

	# save in mysql database
	sql = "INSERT INTO requests (test_id, method, url, url_parameter, header, body) VALUES ((SELECT test_id FROM test_history WHERE secret_key=%s), %s, %s, %s, %s, %s)"
	cur.execute(sql, (secretkey, method, url, json.dumps(parameter), json.dumps(header), json.dumps(body)))
	mylogger.info('The content of API request is saved in the database')
	
	mylogger.info('API request is started')
	if method == 'POST':
		if body != 'NONE':
			try:
				start = datetime.datetime.now()
				res = requests.post(url, data=json.dumps(parameter), headers=header, json=body, timeout=timeout)
			except Exception, e:
				end = datetime.datetime.now()
				mylogger.error('Failed to request API', exc_info=True)
				saveFailList('Request', 'none', 'none', 'none', e)
				failcheck = 1
		else:
			try:
				start = datetime.datetime.now()
				res = requests.post(url, data=json.dumps(parameter), headers=header, timeout=timeout)
			except Exception, e:
				end = datetime.datetime.now()
				mylogger.error('Failed to request API', exc_info=True)
				saveFailList('Request', 'none', 'none', 'none', e)
				failcheck = 1
	elif method == 'PUT':
		if body != 'NONE':
			try:
				start = datetime.datetime.now()
				res = requests.put(url, data=json.dumps(parameter), headers=header, json=body, timeout=timeout)
			except Exception, e:
				end = datetime.datetime.now()
				mylogger.error('Failed to request API', exc_info=True)
				saveFailList('Request', 'none', 'none', 'none', e)
				failcheck = 1
		else:
			try:
				start = datetime.datetime.now()
				res = requests.put(url, data=json.dumps(parameter), headers=header, timeout=timeout)
			except Exception, e:
				end = datetime.datetime.now()
				mylogger.error('Failed to request API', exc_info=True)
				saveFailList('Request', 'none', 'none', 'none', e)
				failcheck = 1
	elif method == 'GET':
		if parameter == 'NONE':
			try:
				start = datetime.datetime.now()
				res = requests.get(url, headers=header, timeout=timeout)
			except Exception, e:
				end = datetime.datetime.now()
				mylogger.error('Failed to request API', exc_info=True)
				saveFailList('Request', 'none', 'none', 'none', e)
				failcheck = 1
		else:
			try:
				start = datetime.datetime.now()
				res = requests.get(url, params=parameter, headers=header, timeout=timeout)
			except Exception, e:
				end = datetime.datetime.now()
				mylogger.error('Failed to request API', exc_info=True)
				saveFailList('Request', 'none', 'none', 'none', e)
				failcheck = 1
	elif method == '__DELETE__':
		try:
			start = datetime.datetime.now()
			res = requests.delete(url, headers=header, timeout=timeout)
		except Exception, e:
			end = datetime.datetime.now()
			mylogger.error('Failed to request API', exc_info=True)
			saveFailList('Request', 'none', 'none', 'none', e)
			failcheck = 1

	#curtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	now = datetime.datetime.now()
	curtime = now + datetime.timedelta(hours=9)
	test_info.append(curtime)

	if failcheck == 0:
		mylogger.info('API request is finished')
		test_info.append(method + ' ' + res.url)
	else:
		test_info.append(method + ' ' + url)
		tmptime = end - start
		global fail_response_time
		fail_response_time = timedelta2ms(tmptime)
		res = 'fail'

	return res

# compare expected response and actual response
def compareResponse(obj, res, secretkey, option):
	returncode = parseByDot(obj, 'ExpectedRes.ReturnCode')
	header = parseByDot(obj, 'ExpectedRes.Header')
	body = parseByDot(obj, 'ExpectedRes.Body')
	responsetime = parseByDot(obj, 'ExpectedRes.ResponseTime')

	# save expected response in mysql database
	sql = "INSERT INTO expected_responses (test_id, return_code, response_time, header, body) VALUES ((SELECT test_id FROM test_history WHERE secret_key=%s), %s, %s, %s, %s)"
	cur.execute(sql, (secretkey, returncode, int(responsetime), json.dumps(header), json.dumps(body)))
	mylogger.info('The content of expected API response is saved in the database')

	# save actual response in mysql database
	sql2 = "INSERT INTO actual_responses (test_id, return_code, response_time, header, body) VALUES ((SELECT test_id FROM test_history WHERE secret_key=%s), %s, %s, %s, %s)"
	if option == 'success':
		real_restime = timedelta2ms(res.elapsed)
		cur.execute(sql2, (secretkey, res.status_code, real_restime, res.headers, json.dumps(res.content)))
		test_info.append(str(res.status_code))
		test_info.append(str(real_restime))
	elif option == 'fail':
		cur.execute(sql2, (secretkey, 440, fail_response_time, '{NONE: NONE}', 'NONE'))
		test_info.append('440')
		test_info.append(str(fail_response_time))
	mylogger.info('The content of actual API response is saved in the database')
	
	if option == 'success':
		mylogger.info('Comparing expected response and actual response is started')

		# return code
		if res.status_code != int(returncode):
			saveFailList('Status', 'Return Code', returncode, res.status_code, 'none')

		# header
		if (header != 'NONE') and (res.status_code == 200):
			for hname, hval in header.items():
				resultTemp = parseByDot(res.headers, hname)
				if resultTemp != hval:
					saveFailList('Header', hname, hval, resultTemp, 'none')

		# body
		if (body != 'NONE') and (res.status_code == 200):
			compareResBody(body, res.content)

		mylogger.info('Comparing expected response and actual response is finished')

# convert timedelta to milliseconds
def timedelta2ms(td):
	r = td.microseconds/float(1000) + td.seconds*float(1000) + td.days*float(24*60*60)*float(1000)
	return int(r)

# compare actual response body with expected response according to the match method
def compareResBody(expected, actual):
	# convert string or list to dictionary
	actual_body = {}
	if actual[0] == '[':
		actual = '{\'tmpname\': ' + actual
		actual = actual + '}'
	actual_body = yaml.load(actual)

	for method, detail in expected.items():
		for option, variables in detail.items():
			for valname, val in variables.items():
				result = parseNested(actual_body, valname)
				resultlist = result.split('|')
				# Regex(regular expression) : Equal / Not equal
				if method == 'Regex':
					for resultTemp in resultlist:
						r = re.match(val, resultTemp)
						if ((r is None) and (option == 'Equal')) or ((r is not None) and (option == 'NotEqual')):
							saveFailList('Body', valname, val, resultTemp, option)
				# Type(comparing data type) : Equal / Not equal
				elif method == 'Type':
					for resultTemp in resultlist:
						if (type(resultTemp) == val and option == 'Equal') or (type(resultTemp) != val and option == 'NotEqual'):
							print valname + ": OK, " + val + " == " + resultTemp
						else:
							saveFailList('Body', valname, val, resultTemp, option)
				# Value(whether the value of certain variable is equal or not equal with input value)
				# Equal / Not equal / Greater than / Less than
				elif method == 'Value':
					for resultTemp in resultlist:
						if option == 'Equal':
							if resultTemp != val:
								saveFailList('Body', valname, val, resultTemp, option)
						elif option == 'NotEqual':
							if resultTemp == val:
								saveFailList('Body', valname, val, resultTemp, option)
						elif option == 'GreaterThan':
							if (resultTemp < val) or (result == val):
								saveFailList('Body', valname, val, resultTemp, option)
						elif option == 'LessThan':
							if (resultTemp > val) or (result == val):
								saveFailList('Body', valname, val, resultTemp, option)

# save error list
def saveFailList(category, where, expected, actual, option):
	if category == 'Request':
		message = "Request Error : ||| " + " ||| " + " ||| " + str(option) + " ||| "
	elif (option == 'none') or (option == 'Equal'):
		message = "Condition Error, " + category + "/" + where + " : ||| " + str(actual) + "(actual response) ||| " + " is not eqaul to  ||| " + str(expected) + "(expected response)" + " ||| "
	elif option == 'NotEqual':
		message = "Condition Error, " + category + "/" + where + " : ||| " + str(actual) + "(actual response) ||| " + " is equal to  ||| " + str(expected) + "(expected response)" + " ||| "
	elif option == 'GreaterThan':
		message = "Condition Error, " + category + "/" + where + " : ||| " + str(actual) + "(actual response) ||| " + " is less than  ||| " + str(expected) + "(expected response)" + " ||| "
	elif option == 'LessThan':
		message = "Condition Error, " + category + "/" + where + " : ||| " + str(actual) + "(actual response) ||| " + " is greater than  ||| " + str(expected) + "(expected response)" + " ||| "

	fail_list.append(message)

# test whether we have to execute the notification or not
def testNotification(savesql, obj, testcase_id, error, final_status, user_id, tname):
	notification_type = parseByDot(obj, 'Type')
	test_info.append(notification_type)

	if notification_type == 'FAIL_COUNT':
		notification_count = parseByDot(obj, 'FailCount')
		sql = "SELECT fail_count, total_count from notifications where testcase_id=%s"
		cur.execute(sql, (testcase_id))
		curval = cur.fetchone()

		if curval is not None:
			if curval[0] != 0:
				if (final_status == 'SUCCESS') and (curval[0] % int(notification_count) == 0):
					savesql = "INSERT INTO notifications (user_id, testcase_id, notification_type, success_count, total_count, final_status, notification_count, testcase_name) VALUES (%s, %s, %s, %s, %s, 'SUCCESS', %s, %s) ON DUPLICATE KEY UPDATE fail_count=0, success_count=success_count+1, total_count=total_count+1, final_status=%s"
				elif (final_status == 'FAIL') and ((curval[0]+1) % int(notification_count) == 0):
					mylogger.info('Notification occured')
					test_info.append('Test failed %s time(s).' % notification_count)
					notification.send_email(error, test_info)
		
		cur.execute(savesql, (user_id, testcase_id, notification_type, 1, 1, int(notification_count), tname, final_status))
	elif notification_type == 'STATUS_CHANGE':
		sql = "SELECT final_status from notifications where testcase_id=%s"
		cur.execute(sql, (testcase_id))
		curval = cur.fetchone()
		cur.execute(savesql, (user_id, testcase_id, notification_type, 1, 1, 0, tname, final_status))

		if curval is not None:
			if curval[0] != final_status:
				mylogger.info('Notification occured')
				test_info.append('%s → %s' % (curval[0], final_status))
				notification.send_email(error, test_info)
		else:
			if final_status == 'FAIL':
				mylogger.info('Notification occured')
				test_info.append('First test failed.')
				notification.send_email(error, test_info)
				

def main():
	mylogger.info('==========================================================')
	mylogger.info('Start Blackbox Testing & Monitoring ABC... >> %s' % sys.argv[1].split('/')[-1])

	f = readFile(sys.argv[1])
	
	userid = parseByDot(f, 'UserID')
	test_info.append(userid)
	email = parseByDot(f, 'Email')
	test_info.append(email)
	testcase = parseByDot(f, 'TestcaseName')
	test_info.append(testcase)
	testcasename = userid + ":" + testcase
	testcase_id = base64.encodestring(testcasename).strip()
	secretkey = ''.join(random.choice(string.digits) for i in range(10))

	# save in mysql database
	sql = "INSERT INTO test_history (testcase_id, user_id, testcase_name, secret_key) VALUES (%s, %s, %s, %s)"
	cur.execute(sql, (testcase_id, userid, testcase, secretkey))
	mylogger.info('The content of test case is saved in the database')
	ncondition = parseByDot(f, 'Notification')

	r = request(f, secretkey)
	if r == 'fail':
		compareResponse(f, r, secretkey, 'fail')
	else:
		compareResponse(f, r, secretkey, 'success')

	# save total result in database
	error_str = ''.join(fail_list)
	if not fail_list:	# success
		mylogger.info('API Test Succeeded!')
		final_status = 'SUCCESS'
		test_info.append('V')
		test_info.append('Succeeded')
		sql2 = "INSERT INTO results (test_id, result, error_list) VALUES ((SELECT test_id FROM test_history WHERE secret_key=%s), 'SUCCESS', 'NONE')"
		cur.execute(sql2, (secretkey))
	else:	# fail
		mylogger.info('API Test failed!')
		final_status = 'FAIL'
		test_info.append('X')
		test_info.append('Failed')
		sql2 = "INSERT INTO results (test_id, result, error_list) VALUES ((SELECT test_id FROM test_history WHERE secret_key=%s), 'FAIL', %s)"
		cur.execute(sql2, (secretkey, error_str))
	
	if ncondition != 'NONE':
		if final_status == 'SUCCESS':
			sql3 = "INSERT INTO notifications (user_id, testcase_id, notification_type, success_count, total_count, final_status, notification_count, testcase_name) VALUES (%s, %s, %s, %s, %s, 'SUCCESS', %s, %s) ON DUPLICATE KEY UPDATE success_count=success_count+1, total_count=total_count+1, final_status=%s"
		elif final_status == 'FAIL':
			sql3 = "INSERT INTO notifications (user_id, testcase_id, notification_type, fail_count, total_count, final_status, notification_count, testcase_name) VALUES (%s, %s, %s, %s, %s, 'FAIL', %s, %s) ON DUPLICATE KEY UPDATE fail_count=fail_count+1, total_count=total_count+1, final_status=%s"
		testNotification(sql3, ncondition, testcase_id, error_str, final_status, userid, testcase)
		mylogger.info('The content of notification is saved in the database')
		
	mylogger.info('The content of result is saved in the database')
		
	db.commit()
	cur.close()
	db.close()

	mylogger.info('Blackbox Testing & Monitoring ABC is finished!... >> %s' % sys.argv[1].split('/')[-1])
	mylogger.info('==========================================================')

if __name__ == "__main__":
	main()
