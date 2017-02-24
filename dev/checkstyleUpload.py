#Building custom Checkstyle parser since none exist. RIP @me
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

from __future__ import print_function
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *
from datetime import date, datetime, timedelta

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    # print(FILE_DIR)

try:
    checkstalio = xml.dom.minidom.parse(FILE_DIR + '/checkstyle.xml')
except:
    print("ERROR: Could not interact with file", FILE_DIR + '/checkstyle.xml')
    print("Script exiting.")
    sys.exit()

#CommitUID getting
CUID = -1
commitUIDSelect = "SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s"
cur.execute(commitUIDSelect, (hash, repoID) )
if cur.rowcount == 0: #UID doesn't exist
    try:
        cur.execute("INSERT INTO commitUID(commitUID, Hexsha, Repo) VALUES \
                        (NULL, %s, %s)", (hash, repoID) )
        cur.execute(commitUIDSelect, (hash, repoID) )
        CUID = cur.fetchone()[0]
    except e:
        print(e[0] + "|" + e[1])
        connection.rollback()
else:
    CUID = cur.fetchone()[0] #Get the actual UID since it exists

if CUID == -1:
    print("Could not get CUID")
    sys.exit()

#root is the first <> element in the XML file.
root = checkstalio.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = connection.cursor()
# Connection setup

#A basic for loop, to look at all the nodes (<> elements) inside the file node
#(which is now the root node) and print out their information to the DB.
#.childNodes is a list of nodes that the root has as children.
package = ""
className = ""
line = 0
col = 0
sev = ""
mess = ""
source = ""

for first in root.childNodes:
    if first.nodeType != first.TEXT_NODE:
        #Ignore messages about tabs
        if first.hasAttribute("name"):
            if first.hasAttribute("name"):
                package = first.getAttribute("name")
                className = package.split('/')[-1]
                className = className.split('.')[0]
                package = package.split('/')[-2]
        for node in first.childNodes:
            #Some errors do not have a column number, so they will print as a -1
            col = -1
            #Ignoes TEXT_NODES because they cause problems
            if node.nodeType != node.TEXT_NODE:
                if node.hasAttribute("line"):
                    line = int(node.getAttribute("line"))
                if node.hasAttribute("column"):
                    col = int(node.getAttribute("column"))
                if node.hasAttribute("severity"):
                    sev = node.getAttribute("severity")
                if node.hasAttribute("message"):
                    mess = node.getAttribute("message")
                if node.hasAttribute("source"):
                    source = node.getAttribute("source").split('.')[-1]

                # Gets information ready to be added to DB
                cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s",(package, className))

                if cur.rowcount == 0: #They don't exist, so add the values into the testMethod and testClass tables
                #Insert into classUID table first to generate the classUID for the testMethodUID table

                    # Try creating a new ClassUID for this
                    try:
                        cur.execute("INSERT INTO classUID(classUID, Package, Class) " \
                            "VALUES (NULL,'%s', '%s')" % ( package, className))
                    except:
                        print("1. Error in committing", sys.exc_info()[0])
                        connection.rollback()

                #By now the classUID should exist, so we call it again to make sure to grab a newly generated classUID
                cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s",(package, className))

                #Checking again, looking to make sure that we uploaded.
                if cur.rowcount == 0:
                    print("Somehow, we inserted and could not insert a classUID.  Exiting.")
                    sys.exit()
                elif cur.rowcount != 1:
                    print("Multiple matches for testClassUID table.  How even?")
                    sys.exit()
                else:
                    #Now we can actually get the number.
                    classUID = int(cur.fetchone()[0])

                # Attempts to insert information into database. If it doesn't match, it catches in the except and prints it.
                try:
                    add_checkstyle = ("INSERT INTO checkstyle (CommitUID, ClassUID, ErrorType, Severity, ErrorMessage, Line, Col) " \
                          "VALUES ( '%d', '%d', '%s', '%s', '%s', '%d', '%d')" % ( 0, classUID, source, sev, mess.replace('\n\n',' - ').replace('\n','').replace('\'','\\\'')[:50], line, col))
                    cur.execute(add_checkstyle)

                    #Checking, delete print
                    #print(add_checkstyle)
                except:
                    print("2. Error in committing", sys.exc_info()[0])
                    connection.rollback();

# Closing connection
connection.close()
