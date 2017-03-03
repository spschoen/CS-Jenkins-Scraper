"""
Custom find bugs xml parser
@authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

Execution: python3 findbugsUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUM
0. findbugsUpload.py
1. WORKSPACE  : /path/to/working/directory
2. PROJECT_ID : PW-XYZ
3. GIT_COMMIT : [40 char commit hash]
"""

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
    #print(FILE_DIR)

try:
    findbuggies = xml.dom.minidom.parse(FILE_DIR + "/findbugs.xml")
except:
    print("ERROR: Could not interact with file", FILE_DIR + "/findbugs.xml")
    print("Script exiting.")
    sys.exit()

# Getting commitUID info
repoID = sys.argv[2]
hash = sys.argv[3]

#root is the first <> element in the XML file.
root = findbuggies.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: CHANGE THESE IN PRODUCTION
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()

#CommitUID getting
CUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

if root.hasAttribute("version"):
    pass
    #print("FindBugs Version : %s" % root.getAttribute("version"))

package = ""
className = ""
method = ""
bugType = ""
priority = 0
rank = 0
cat = ""
line = 0

for node in root.childNodes:
    if node.nodeName == "BugInstance":
        bugType = node.getAttribute("type")
        if node.hasAttribute("priority"):
            priority = int(node.getAttribute("priority"))
        if node.hasAttribute("rank"):
            rank = int(node.getAttribute("rank"))
        if node.hasAttribute("category"):
            cat = node.getAttribute("category")
            for classNode in node.childNodes:
                if classNode.nodeName == "Method" and not classNode.hasAttribute("role"):
                    if classNode.hasAttribute("classname"):
                        string = classNode.getAttribute("classname")
                        package = string.split(".")[-1]
                        className = string.split(".")[-2]
                    if classNode.hasAttribute("name"):
                        method = classNode.getAttribute("name")
                if classNode.nodeName == "SourceLine":
                    if classNode.hasAttribute("start"):
                        line = int(classNode.getAttribute("start"))

        #Grab methodUID for below. By now, it should definitely exist
        methodUID = MySQL_Func.getMethodUID(IP=IP, user=user, pw=pw, DB=DB,
                                            className=className, package=package,
                                            method=method)
        search = "SELECT * FROM findBugs WHERE CommitUID = %s AND MethodUID = %s AND "
        search += "BugType = %s AND Priority = %s AND Rank = %s and Category = %s AND Line = %s"

        cur.execute(search, (CUID, methodUID, bugType, priority, rank, cat, line))
        if cur.rowcount != 0:
            continue

        add_findbugs = "INSERT INTO findBugs(CommitUID, MethodUID, BugType, Priority, "
        add_findbugs += "Rank, Category, Line) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # This one goes to findbugs
        try:
            cur.execute(add_findbugs, (CUID, methodUID, bugType, priority, rank, cat, line))
        except:
            connection.rollback()
            ErrorString = sys.exc_info()[0] + "\n----------\n"
            ErrorString += sys.exc_info()[1] + "\n----------\n"
            ErrorString += sys.exc_info()[2]

            v_list = "(CommitUID, MethodUID, BugType, Priority, Rank, Category, Line)"
            MySQL_Func.sendFailEmail("Failed to insert into findBugs table!",
                                        "The following insert failed:",
                                        add_findbugs,
                                        v_list,
                                        ErrorString,
                                        CUID, methodUID, bugType, priority, rank, cat, line)

# Closing connection
connection.close()
