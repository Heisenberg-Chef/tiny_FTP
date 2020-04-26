#_*_coding:utf-8_*_

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#   print(BASE_DIR)
USER_HOME = "%s/home" % BASE_DIR
LOG_DIR = "%s/log" % BASE_DIR
LOG_LEVEL = "DEBUG"
 
ACCOUNT_FILE = "%s/conf/accounts.cfg" % BASE_DIR

HOST = '108.171.195.131'
PORT = 9999