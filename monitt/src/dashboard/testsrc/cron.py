from crontab import CronTab
import subprocess, os, makelog

mylogger = makelog.get_logger('cron')

# execute cron jobs using crontab
def executeCron(timeslices, command):
	mylogger.info('Register new cron job: %s %s' % (timeslices, command))

	os.system("crontab -l > /tmp/curcronfile.txt")
	cmd = "echo " + "\'" + timeslices + " " + command + "\'" + " >> /tmp/curcronfile.txt\n"
	os.system(cmd)
	os.system("crontab < /tmp/curcronfile.txt")
	os.system("rm /tmp/curcronfile.txt")

# judge whether the cron of test case already exists
def testCron(timeslices, filepath):
	test_path = os.getcwd()
	command = "/usr/bin/python " + test_path + "/dashboard/testsrc/blackbox.py " + filepath
	pipe = subprocess.Popen(('crontab', '-l'), stdout=subprocess.PIPE)
	result = pipe.communicate()[0]
	lines = result.splitlines(True)
	line = timeslices + " " + command + "\n"

	if not lines:	# empty
		executeCron(timeslices, command)
	else:	# not empty
		if line not in lines:
			executeCron(timeslices, command)

# remove cron job (uncompleted)
def removeCron(timeslices, filepath):
	fulljob = timeslices + " /usr/bin/python /Users/a5001941/easyapitest/src/dashboard/testsrc/blackbox.py " + filepath
	print fulljob