# TODO: WRITE LIBRARY FUNCTIONS TO MAKE THIS TINY.

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
# TODO: CHANGE THESE IN PRODUCTION
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
                    cur.execute("SELECT * FROM testMethodUID WHERE testMethodName = %s", (testName))

                    if cur.rowcount == 0: #The values do not exist in the testMethodUID table

                        #Check if classUID values at least exist, which may not be possible if methodUID doesn't exist, but it's double checking.
                        cur.execute("SELECT * FROM testClassUID WHERE testPackage = %s and testClass = %s",(package, className ))

                        if cur.rowcount == 0: #It don't exist, so add the values into the testClass table

                            #Insert into classUID table first to generate the classUID for the testMethodUID table
                            try:
                                cur.execute("INSERT INTO testClassUID(testClassUID, testClass, testPackage)" \
                                " VALUES (NULL, %s, %s)", (className, package))

                            except e:
                                #TODO: email
                                print(e[0] + "|" + e[1])
                                connection.rollback()

                            #Execute the same select, so we can get the new classUID if there is one and create the methodUID
                            cur.execute("SELECT * FROM testClassUID WHERE testPackage = %s and testClass = %s",(package, className ))
                        #Checking again, looking to make sure that we uploaded.
                        if cur.rowcount == 0:
                            print("Somehow, we inserted and could not insert a testClassUID.  Exiting.")
                            sys.exit()
                        elif cur.rowcount != 1:
                            print("Multiple matches for testClassUID table.  How even?")
                            sys.exit()
                        else:
                            #Now we can actually get the number.
                            classUID = int(cur.fetchone()[0])

                        #Insert into methodUID table
                        try:
                            cur.execute("INSERT INTO testMethodUID(testMethodUID, testClassUID, testMethodName)" \
                            " VALUES (NULL, %s, %s)", (classUID, testName))

                        except e:
                            #TODO: email
                            print(e[0] + "|" + e[1])
                            connection.rollback()
                    #By now the classUID and methodUID should exist, and things should be all peachy.
                    try:
                        #Execute yet again so we can get the new classUID if it was created above
                        cur.execute("SELECT * FROM testClassUID WHERE testPackage = %s and \
                                        testClass = %s", (package, className) )
                        classUID = int(cur.fetchone()[0])

                        find = "SELECT * FROM testTable WHERE CommitUID = %s and testClassUID = %s "
                        find += "and Name = %s and Passing = %s"

                        cur.execute(find, (CUID, classUID, testName, passing) )

                        if cur.rowcount == 0:
                            testInsert = "INSERT INTO testTable(CommitUID, testClassUID, Name, "
                            testInsert += "Passing ) VALUES (%s, %s, %s, %s)"
                            cur.execute(testInsert, (CUID, classUID, testName, passing) )

                    except:
                        #TODO: email
                        for error in sys.exc_info():
                            print(error)
                        connection.rollback()
    count += 1

# Closing connection
connection.close()
