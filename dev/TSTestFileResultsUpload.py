"""
Reads test reports and uploads
Requirements:
 - test[blaaaaah].xml must exist.  If not, this script won't read it.
 - MySQL_Func.py for interacting with MySQL.
 - config.txt to read in variables for IP, DB, etc.

Execution:
 - python3 testFileResultsUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
   - Arguments:
     - 0. testFileResultsUpload.py
     - 1. WORKSPACE  : /path/to/test-reports/*.xml (DO NOT INCLUDE *.xml)
     - 2. PROJECT_ID : PW-XYZ
     - 3. GIT_COMMIT : [40 char commit hash]
     - 4. DIRECTORY  : Directory of tests to read.

@author Renata Ann Zeitler
"""

import xml.dom.minidom
import sys
import os
import pymysql
import MySQL_Func

if len(sys.argv) != 5:
    print("Did not get expected arguments.")
    print("$WORKSPACE $PROJECT_ID $GIT_COMMIT $DIRECTORY")
    sys.exit()

# Setting up the XML to read
FILE_DIR = '/'
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    # print(FILE_DIR)

# Getting to the right directory
if '/ts-test-reports/' not in FILE_DIR:
    FILE_DIR += '/ts-test-reports/'

# print(FILE_DIR)

# Directory to XML set up.

# Getting commitUID info
repoID = sys.argv[2]
hash = sys.argv[3]

# Setting up the DB connection
# Future people: change this to your master IP
# Or wherever your DB is.
# Now, we begin reading the config file.
if not os.path.exists('config.txt'):
    # config.txt doesn't exist.  Don't run.
    print("Could not access config.txt, exiting.")
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

# CommitUID getting
CUID = MySQL_Func.getCommitUID(
    IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

count = 0

# Initialize variables
package = ""
method = ""
className = ""
testName = ""
passing = ""

for file in os.listdir(FILE_DIR):
    if file != '.DS_Store':
        try:
            DOMTree = xml.dom.minidom.parse(FILE_DIR + file)
        except:
            print("ERROR: Could not interact with file " + FILE_DIR + file)
            sys.exit()
        root = DOMTree.documentElement

        if root.hasAttribute("name"):
            temp = root.getAttribute("name")
            className = temp.split(".")[-1]
            package = temp.split(".")[-2]
            for node in root.childNodes:
                if node.nodeName == "testcase":
                    if node.hasAttribute("name"):
                        testName = node.getAttribute("name")
                    if len(node.childNodes) != 0:
                        passing = "F"
                    else:
                        passing = "P"

                    # If we get any records returned, then it's already in the table.
                    # Otherwise, if there are no returned records, then we need to insert
                    # them into the table.
                    testMethodUID = MySQL_Func.getTestMethodUID(IP=IP, user=user, pw=pw,
                                                                DB=DB, className=className,
                                                                package=package, method=testName)

                    find = "SELECT * FROM TS_testTable WHERE CommitUID = %s AND testMethodUID = %s "
                    find += "AND Passing = %s"

                    cur.execute(find, (CUID, testMethodUID, passing))

                    if cur.rowcount == 0:
                        testInsert = "INSERT INTO TS_testTable(CommitUID, testMethodUID, Passing) "
                        testInsert += "VALUES (%s, %s, %s)"
                        try:
                            cur.execute(
                                testInsert, (CUID, testMethodUID, passing))
                        except:
                            connection.rollback()
                            ErrorString = sys.exc_info()[0] + "\n----------\n"
                            ErrorString += sys.exc_info()[1] + "\n----------\n"
                            ErrorString += sys.exc_info()[2]

                            v_list = "(CommitUID, testMethodUID, Passing)"
                            MySQL_Func.sendFailEmail("Failed to insert into test Results table!",
                                                     "The following insert failed:",
                                                     insertPMD,
                                                     v_list,
                                                     ErrorString,
                                                     str(CUID), str(
                                                         methodUID), str(ruleset),
                                                     str(rule), str(line))

connection.close()
