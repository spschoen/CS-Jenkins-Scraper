from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = cnx.cursor()
# Connection setup

# TODO: Actual code goes here.

# Closing connection
cnx.close()
