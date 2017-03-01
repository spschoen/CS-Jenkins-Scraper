#Building custom Checkstyle parser since none exist. RIP @me
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

import xml.dom.minidom
import sys
import os
import pymysql
import MySQL_Func

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
    #TODO: error email
    print("ERROR: Could not interact with file", FILE_DIR + '/checkstyle.xml')
    print("Script exiting.")
    sys.exit()

#root is the first <> element in the XML file.
root = checkstalio.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
# TODO: CHANGE THESE IN PRODUCTION
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()
# Connection setup

repoID = sys.argv[2]
hash = sys.argv[3]

#CommitUID getting
CUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

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
                    mess = mess.replace("\\","\\\\").replace('\'','\\\'')[:50]
                if node.hasAttribute("source"):
                    source = node.getAttribute("source").split('.')[-1]

                # Gets information ready to be added to DB
                classUID = MySQL_Func.getClassUID(IP=IP, user=user, pw=pw, DB=DB,
                                        className=className, package=package)

                search = "SELECT * FROM checkstyle WHERE CommitUID = %s AND ClassUID = %s AND "
                search += "ErrorType = %s AND Severity = %s AND Line = %s and Col = %s"

                cur.execute(search, (CUID, classUID, source, sev, line, col))
                if cur.rowcount != 0:
                    continue

                # Attempts to insert information into database.
                # If it doesn't match, it catches in the except and prints it.
                add_checkstyle = "INSERT INTO checkstyle (CommitUID, ClassUID, ErrorType, "
                add_checkstyle += "Severity, ErrorMessage, Line, Col) VALUES "
                add_checkstyle += " (%s, %s, %s, %s, %s, %s, %s)"
                try:
                    cur.execute(add_checkstyle, (CUID, classUID, source, sev, mess, line, col))
                except:
                    connection.rollback()
                    ErrorString = sys.exc_info()[0] + "\n----------\n"
                    ErrorString += sys.exc_info()[1] + "\n----------\n"
                    ErrorString += sys.exc_info()[2]

                    v_list = "(CommitUID, ClassUID, ErrorType, Severity, ErrorMessage, Line, Col)"
                    MySQL_Func.sendFailEmail("Failed to insert into checkstyle table!",
                                                "The following insert failed:",
                                                add_checkstyle,
                                                v_list,
                                                ErrorString,
                                                CUID, classUID, source, sev, mess, line, col)

# Closing connection
connection.close()
