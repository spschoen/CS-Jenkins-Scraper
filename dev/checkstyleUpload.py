"""
Reads checkstyle error file (checkstyle.xml) and uploads any records to the given Database.

Requirements:
    MySQL_Func.py - library for interaction with databases must be available in the same directory as this file.
    config.txt    - file specifying database information.

Args:
    1. WORKSPACE  - Absolute path to the location of test-reports/, which contains the test XML files.
    2. PROJECT_ID - 17 char string representing class, section, project, and unique ID of the current project.
                    For example: csc216-002-P2-096
    3. GIT_COMMIT - 40 Character commit hash.

Returns:
    N/A

Authors:
    Renata Ann Zeitler
    Samuel Schoeneberger
"""

import xml.dom.minidom
import sys
import os
import pymysql
import MySQL_Func

if len(sys.argv) != 4:
    print("Incorrect number of arguments.  Exiting.")
    sys.exit()

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    # print(FILE_DIR)

if not os.path.exists(FILE_DIR + '/checkstyle.xml'):
    # checkstyle.xml doesn't exist.  Don't run.
    # print("Could not access checkstyle.xml, exiting.")
    sys.exit()

try:
    checkstalio = xml.dom.minidom.parse(FILE_DIR + '/checkstyle.xml')
except:
    # This is commented out, because checkstyle XML can be not created for a lot of reasons.
    '''ErrorString = sys.exc_info()[0] + "\n----------\n"
    ErrorString += sys.exc_info()[1] + "\n----------\n"
    ErrorString += sys.exc_info()[2]
    MySQL_Func.sendFailEmail("Failed to read checkstyle.xml", "The following command failed:",
                                "checkstalio = xml.dom.minidom.parse(FILE_DIR + '/checkstyle.xml')",
                                "With the following variables (FILE_DIR)",
                                ErrorString, FILE_DIR)'''
    sys.exit()

# root is the first <> element in the XML file.
root = checkstalio.documentElement

# We're now set up to read XML

# Now, we begin reading the config file.
if not os.path.exists('config.txt'):
    # config.txt doesn't exist.  Don't run.
    # print("Could not access config.txt, exiting.")
    sys.exit()

configFile = open("config.txt", "r")
lines = list(configFile)
if len(lines) != 4:
    # incorrect config file
    # print("config.txt contains incorrect number of records.")
    sys.exit()

# Setting up the DB connection
IP = lines[0].replace("\n", "")
user = lines[1].replace("\n", "")
pw = lines[2].replace("\n", "")
DB = lines[3].replace("\n", "")

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()
# Connection setup

repoID = sys.argv[2]
hash = sys.argv[3]

# CommitUID getting
CUID = MySQL_Func.getCommitUID(
    IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

# A basic for loop, to look at all the nodes (<> elements) inside the file node
# (which is now the root node) and print out their information to the DB.
# .childNodes is a list of nodes that the root has as children.
package = ""
className = ""
line = 0
col = 0
sev = ""
mess = ""
source = ""

for first in root.childNodes:
    if first.nodeType != first.TEXT_NODE:
        if first.hasAttribute("name"):
            package = first.getAttribute("name")
            className = package.split('/')[-1]
            className = className.split('.')[0]
            package = package.split('/')[-2]
        for node in first.childNodes:
            # Some errors do not have a column number, so they will print as a
            # -1
            col = -1
            # Ignores TEXT_NODES because they cause problems
            if node.nodeType != node.TEXT_NODE:
                if node.hasAttribute("line"):
                    line = int(node.getAttribute("line"))
                if node.hasAttribute("column"):
                    col = int(node.getAttribute("column"))
                if node.hasAttribute("severity"):
                    sev = node.getAttribute("severity")
                if node.hasAttribute("message"):
                    mess = node.getAttribute("message")
                    mess = mess.replace("\\", "\\\\").replace(
                        '\'', '\\\'')[:50]
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
                    cur.execute(add_checkstyle, (CUID, classUID,
                                                 source, sev, mess, line, col))
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
