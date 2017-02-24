#Custom TestFile parser
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
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

#Getting to the right directory
filesListed = os.listdir(FILE_DIR + '/test-reports/');

# Setting up the DB connection
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = connection.cursor()


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

                    # If we get any records returned, then it's already in the table. Otherwise, if there are no returned records,
                    # then we need to insert them into the table.
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
                            print(e[0] + "|" + e[1])
                            connection.rollback()
                    #By now the classUID and methodUID should exist, and things should be all peachy.
                    try:
                        #Execute yet again so we can get the new classUID if it was created above
                        #TODO: get commitUID
                        add_testTable = ("INSERT INTO testTable (CommitUID, testClassUID, Name, Passing) " \
                              "VALUES ( '%d', '%s', '%s', '%s')" % ( -1, classUID, testName, passing))

                    except:
                        print("Messup", sys.exc_info())
                        connection.rollback()

                    # Attempts to insert information into database. If it doesn't match, it catches in the except and prints it.
                    try:
                        cur.execute(add_testTable)
                    except:
                        print("Error in committing", sys.exc_info())
    count += 1

# Closing connection
connection.close()
