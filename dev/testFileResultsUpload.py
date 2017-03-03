# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 testFileResultsUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
# 0. testFileResultsUpload.py
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

#Getting to the right directory
if "test-reports" not in FILE_DIR:
    filesListed = os.listdir(FILE_DIR + '/test-reports/');

# Directory to XML set up.

# Getting commitUID info
repoID = sys.argv[2]
hash = sys.argv[3]

# Setting up the DB connection
# Future people: change this to your master IP
# Or wherever your DB is.
# FIXME: Change these to whatever your production DB is at.
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()

#CommitUID getting
CUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

count = 0

#Initialize variables
package = ""
method = ""
className = ""
testName = ""
passing = ""

while (count < len(filesListed)):
    if (filesListed[count] != '.DS_Store'):
        try:
            DOMTree = xml.dom.minidom.parse(FILE_DIR + '/test-reports/' + filesListed[count])
        except:
            print("ERROR: Could not interact with file", FILE_DIR + '/' + filesListed[count] + '.xml')
            print("Script exiting.")
            sys.exit()

        #root is the first <> element in the XML file.
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

                    find = "SELECT * FROM testTable WHERE CommitUID = %s AND testMethodUID = %s "
                    find += "AND Passing = %s"

                    cur.execute(find, (CUID, testMethodUID, passing) )

                    if cur.rowcount == 0:
                        testInsert = "INSERT INTO testTable(CommitUID, testMethodUID, Passing) "
                        testInsert += "VALUES (%s, %s, %s)"
                        try:
                            cur.execute(testInsert, (CUID, testMethodUID, passing) )
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
                                                        str(CUID), str(methodUID), str(ruleset),
                                                        str(rule), str(line))
    count += 1

# Closing connection
connection.close()
