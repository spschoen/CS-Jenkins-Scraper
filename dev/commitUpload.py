#Building custom Checkstyle parser since none exist. RIP @me

from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
# Don't forget to
connection = pymysql.connect(host="152.46.18.11")
cur = cnx.cursor()
# Connection setup

# TODO: Actual code goes here.

# Closing connection
cnx.close()
