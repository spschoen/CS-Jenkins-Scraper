# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 pmdUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
# 0. pmdUpload.py
# 1. WORKSPACE  : /path/to/test-reports/
# 2. PROJECT_ID : PW-XYZ
# 3. GIT_COMMIT : [40 char commit hash]

import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

try:
    pmd = xml.dom.minidom.parse(FILE_DIR + '/pmd.xml')
except:
    print("ERROR: Could not interact with file", FILE_DIR + '/pmd.xml')
    print("Script exiting.")
    sys.exit()

# Getting commitUID info
repoID = sys.argv[2]
hash = sys.argv[3]

#root is the first <> element in the XML file.
root = pmd.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
connection = pymysql.connect(host="152.46.20.243", user="root", passwd="", db="repoinfo")
cur = connection.cursor()

#CommitUID getting
CUID = -1
commitUIDSelect = "SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s"
cur.execute(commitUIDSelect, (hash, repoID) )
if cur.rowcount == 0:
    try:
        cur.execute("INSERT INTO commitUID(commitUID, Hexsha, Repo) VALUES \
                        (NULL, %s, %s)", (hash, repoID) )
        cur.execute(commitUIDSelect, (hash, repoID) )
        CUID = cur.fetchone()[0]
    except e:
        print(e[0] + "|" + e[1])
        connection.rollback()
else:
    CUID = int(cur.fetchone()[0])

if CUID == -1:
    print("Could not get CUID")
    sys.exit()

package = ""
className = ""
method = ""
line = 0
rule = ""
ruleset = ""

#A basic for loop, to look at all the nodes (<> elements) inside the file node
#(which is now the root node) and print out their information to the DB.
#.childNodes is a list of nodes that the root has as children.
for file in root.childNodes:
    if file.nodeType != file.TEXT_NODE:
        for node in file.childNodes:
            if node.nodeType != node.TEXT_NODE:
                if node.hasAttribute("beginline"):
                    line = int(node.getAttribute("beginline"))
                if node.hasAttribute("rule"):
                    rule = node.getAttribute("rule")
                if node.hasAttribute("ruleset"):
                    ruleset = node.getAttribute("ruleset")
                if node.hasAttribute("package"):
                    package = node.getAttribute("package").split('.')[-1]
                if node.hasAttribute("class"):
                    className = node.getAttribute("class")
                if node.hasAttribute("method"):
                    method = node.getAttribute("method")

    # holy FRAK it fits on the 100 limit!
    if package == "" or className == "" or method == "" or rule == "" or ruleset == "" or line == 0:
        #print("Could not find an attribute.  Rerun with print debugging.")
        continue

    # Class UID
    cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s", (package, className) )
    classUID = -1
    if cur.rowcount == 0:
        insertClassUID = "INSERT INTO classUID(classUID, Package, Class) VALUES (NULL, %s, %s)"
        try:
            cur.execute(insertClassUID, (package, className) )
        except:
            for error in sys.exec_info():
                print(error)
            sys.exit()

    cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s", (package, className) )
    classUID = int(cur.fetchone()[0])

    # Method UID
    cur.execute("SELECT * FROM methodUID WHERE ClassUID = %s and Method = %s", (classUID, method) )
    methodUID = -1
    if cur.rowcount == 0:
        insertMethodUID = "INSERT INTO methodUID(methodUID, ClasUID, Method) VALUES (NULL, %s, %s)"
        try:
            cur.execute(insertMethodUID, (classUID, method) )
        except:
            for error in sys.exec_info():
                print(error)
            sys.exit()

    cur.execute("SELECT * FROM methodUID WHERE ClassUID = %s and Method = %s", (classUID, method) )
    methodUID = int(cur.fetchone()[0])

    # PMD time!
    insertPMD = "INSERT INTO PMD(CommitUID, MethodUID, Ruleset, Rule, Line) "
    insertPMD += "VALUES ( %s, %d, %s, %s, %d )"

    try:
        cur.execute(insertPMD, ( CUID, methodUID, ruleset, rule, line) )
    except:
        #for error in sys.exec_info():
        #    print(error)
        print(sys.exec_info())
        sys.exit()

# Closing connection
connection.close()
