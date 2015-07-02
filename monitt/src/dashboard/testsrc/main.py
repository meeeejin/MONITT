import cron, blackbox, makelog
import yaml, os, sys, time, base64
import MySQLdb

db = MySQLdb.connect(host="localhost", user="root", passwd="qwer1234", db="blackbox")
cur = db.cursor()
mylogger = makelog.get_logger('main')

def executeBlackbox(filepath):
	test_path = os.getcwd()
	command = "/usr/bin/python " + test_path + "/dashboard/testsrc/blackbox.py " + filepath
	os.system(command)

def executeOnce(frequency, times, types, filepath):
	mylogger.info('Execute the job %s times. One cycle: %s %s' % (times, frequency, types))

	if types == 'minutes':
		frequency = frequency * 60

	mylogger.info('>> execute 1 cycle')
	executeBlackbox(filepath)
	for i in range(int(times)-1):
		mylogger.info('>> execute %s cycle' % (i+2))
		time.sleep(float(frequency))
		executeBlackbox(filepath)

def needScheduling(obj, filepath, userid, testcaseid, testcasename, request_method, request_url):
	for method, detail in obj.items():
		if method == 'Once':
			unit = blackbox.parseByDot(detail, 'Unit')
			frequency = blackbox.parseByDot(detail, 'Frequency')
			times = blackbox.parseByDot(detail, 'Times')
			sql = "INSERT INTO schedulings (user_id, testcase_id, method, frequency, times, testcase_name, request_method, request_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			cur.execute(sql, (userid, testcaseid, method, frequency, times, testcasename, request_method, request_url))
			db.commit()
			cur.close()
			db.close()
			executeOnce(frequency, times, unit, filepath)
		elif method == 'Periodically':
			cronvalue = ['*']*5
			for item in detail:
				unit = blackbox.parseByDot(item, 'Unit')
				frequency = blackbox.parseByDot(item, 'Frequency')
				if unit == 'MINUTES':
					cronvalue[0] = frequency
				elif unit == 'HOURS':
					cronvalue[1] = frequency
				elif unit == 'DAYOFMONTH':
					cronvalue[2] = frequency
				elif unit == 'MONTHS':
					cronvalue[3] = frequency
				elif unit == 'DAYOFWEEK':
					cronvalue[4] = frequency
			for i in range(5):
				if i == 0:
					cronval = cronvalue[0]
				else:
					cronval = cronval + ' ' + cronvalue[i]
			sql = "INSERT INTO schedulings (user_id, testcase_id, method, frequency, testcase_name, request_method, request_url) VALUES (%s, %s, %s, %s, %s, %s, %s)"
			cur.execute(sql, (userid, testcaseid, method, cronval, testcasename, request_method, request_url))
			db.commit()
			cur.close()
			db.close()
			cron.testCron(cronval, filepath)
			
			

def main():
	mylogger.info('Preparing Blackbox Testing & Monitoring ABC... >> %s' % sys.argv[1].split('/')[-1])

	f = blackbox.readFile(sys.argv[1])
	scheduling_val = blackbox.parseByDot(f, 'Scheduling')
	
	userid = blackbox.parseByDot(f, 'UserID')
	testcase = blackbox.parseByDot(f, 'TestcaseName')
	testcasename = userid + ":" + testcase
	testcaseid = base64.encodestring(testcasename).strip()
	
	request_method = blackbox.parseByDot(f, 'Req.Method')
	request_url = blackbox.parseByDot(f, 'Req.URL')

	if scheduling_val == 'NONE':
		executeBlackbox(sys.argv[1])
	else:
		needScheduling(scheduling_val, sys.argv[1], userid, testcaseid, testcase, request_method, request_url)

if __name__ == "__main__":
	main()
