# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

from __future__ import print_function
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

try:
    findbuggies = xml.dom.minidom.parse('../ExampleXML/findbugs.xml')
except:
    print("ERROR: Could not interact with file", FILE_DIR + '/findbugs.xml')
    print("Script exiting.")
    sys.exit()

#root is the first <> element in the XML file.
root = findbuggies.documentElement