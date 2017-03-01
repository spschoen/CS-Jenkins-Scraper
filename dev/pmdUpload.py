# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 pmdUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
# 0. pmdUpload.py
# 1. WORKSPACE  : /path/to/test-reports/
# 2. PROJECT_ID : PW-XYZ
# 3. GIT_COMMIT : [40 char commit hash]

import xml.dom.minidom
import sys
import os
import pymysql
import MySQL_Func

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
# TODO: CHANGE THESE IN PRODUCTION
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()

#CommitUID getting
CUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

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
    else:
        continue

    # holy FRAK it fits on the 100 limit!
    if package == "" or className == "" or method == "" or rule == "" or ruleset == "" or line == 0:
        #print("Could not find an attribute.  Rerun with print debugging.")
        continue

    # Class UID
    methodUID = MySQL_Func.getMethodUID(IP=IP, user=user, pw=pw, DB=DB, className=className,
                                        package=package, method=method)

    search = "SELECT * FROM PMD WHERE CommitUID = %s AND MethodUID = %s AND Ruleset = %s AND "
    search += "Rule = %s AND Line = %s"
    cur.execute(search, (str(CUID), str(methodUID), str(ruleset), str(rule), str(line)))
    if cur.rowcount != 0:
        continue

    # PMD time!
    insertPMD = "INSERT INTO PMD(CommitUID, MethodUID, Ruleset, Rule, Line) "
    insertPMD += "VALUES ( %s, %s, %s, %s, %s )"

    try:
        cur.execute(insertPMD, (str(CUID), str(methodUID), str(ruleset), str(rule), str(line)))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]

        v_list = "(CommitUID, MethodUID, Ruleset, Rule, Line)"
        MySQL_Func.sendFailEmail("Failed to insert into PMD table!",
                                    "The following insert failed:",
                                    insertPMD,
                                    v_list,
                                    ErrorString,
                                    str(CUID), str(methodUID), str(ruleset), str(rule), str(line))

# Closing connection
connection.close()
