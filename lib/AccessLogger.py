import logging
from logging.handlers import RotatingFileHandler

class AccessLogger:

    def __init__(self, filename):
        log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
        logFile = filename
        my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=10**7, encoding=None, delay=0)
        my_handler.setFormatter(log_formatter)
        my_handler.setLevel(logging.INFO)
        self.app_log = logging.getLogger('root')
        self.app_log.setLevel(logging.INFO)
        self.app_log.addHandler(my_handler)

    def log(self, message):
        self.app_log.info(message)