#_*_coding:utf-8_*_

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#   print(BASE_DIR)
USER_HOME = "%s/home" % BASE_DIR
LOG_DIR = "%s/log" % BASE_DIR
LOG_LEVEL = "DEBUG"
 
ACCOUNT_FILE = "%s/conf/account.cfg" % BASE_DIR

HOST = '127.0.0.1'
PORT = 9999