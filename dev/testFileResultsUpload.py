"""
Reads student test reports and uploads them to the given Database.

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
    print("Did not get expected arguments.")
    print("$WORKSPACE $PROJECT_ID $GIT_COMMIT")
    sys.exit()

# Setting up the XML to read
FILE_DIR = '/'
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    # print(FILE_DIR)

# Getting to the right directory
if '/test-reports/' not in FILE_DIR:
    FILE_DIR += '/test-reports/'

# print(FILE_DIR)

# Directory to XML set up.

# Getting commitUID info
repoID = sys.argv[2]
commit_hash = sys.argv[3]

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
    print("config.txt contains incorrect number of records.")
    sys.exit()

# Setting up the DB connection
IP = lines[0].replace("\n", "")
user = lines[1].replace("\n", "")
pw = lines[2].replace("\n", "")
DB = lines[3].replace("\n", "")

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()

# CommitUID getting
commit_uid = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=commit_hash, repoID=repoID)

# Initialize variables
package = ""
method = ""
className = ""
testName = ""
passing = ""

for file in os.listdir(FILE_DIR):
    if not (str(file).endswith(".xml")):
        continue
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
        testMethodUID = MySQL_Func.getTestMethodUID(IP=IP, user=user, pw=pw,
                                                    DB=DB, className=className,
                                                    package=package, method=testName)

        for node in root.childNodes:
            message = ""
            if node.nodeName == "testcase":
                if node.hasAttribute("name"):
                    testName = node.getAttribute("name")
                if len(node.childNodes) != 0:
                    passing = "F"
                    for test_case_child in node.childNodes:
                        if test_case_child.nodeType != test_case_child.TEXT_NODE:
                            message = test_case_child.getAttribute("message")
                else:
                    passing = "P"

                # If we get any records returned, then it's already in the table.
                # Otherwise, if there are no returned records, then we need to insert
                # them into the table.
                find = "SELECT * FROM testTable WHERE CommitUID = %s AND testMethodUID = %s "
                find += "AND Passing = %s"

                cur.execute(find, (commit_uid, testMethodUID, passing))

                if cur.rowcount == 0:
                    testInsert = "INSERT INTO testTable(CommitUID, testMethodUID, Passing, Message) \
                                  VALUES (%s, %s, %s, %s)"
                    try:
                        cur.execute(testInsert, (commit_uid, testMethodUID, passing, message))
                    except:
                        connection.rollback()
                        ErrorString = sys.exc_info()[0] + "\n----------\n"
                        ErrorString += sys.exc_info()[1] + "\n----------\n"
                        ErrorString += sys.exc_info()[2]

                        v_list = "(CommitUID, testMethodUID, Passing, Message)"
                        MySQL_Func.sendFailEmail("Failed to insert into test Results table!",
                                                 "The following insert failed:",
                                                 testInsert, v_list, ErrorString,
                                                 str(commit_uid), str(testMethodUID), str(passing), str(message))

connection.close()
