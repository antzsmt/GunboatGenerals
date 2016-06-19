#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/websites/")

from websites import app as application
application.secret_key = 'azulazul'
