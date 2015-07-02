import logging, os
from logging.handlers import RotatingFileHandler

# get a logger
def get_logger(name):
	LOG_FORMAT = "[%(asctime)-15s] (%(filename)s:%(lineno)d) %(funcName)s - %(message)s"
	LOG_MAXSIZE = 1024 * 1024 # 1MB
	cur_path = os.getcwd()
	LOG_FILE = '/Users/ahnmijin/blackbox.log' # configure your own log path

	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)

	# create a file handler
	handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAXSIZE, backupCount=5)
	handler.setLevel(logging.INFO)

	# create a logging format
	formatter = logging.Formatter(LOG_FORMAT)
	handler.setFormatter(formatter)

	# add the handlers to the logger
	logger.addHandler(handler)

	return logger
