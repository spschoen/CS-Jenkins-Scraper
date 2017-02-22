#Building custom TestFile parser since none exist. RIP @me
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
    #debug
    #print(FILE_DIR)

filesListed = os.listdir(FILE_DIR + '/test-reports/');

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = connection.cursor()


count = 0

#Initialize variables
className = ""
testName = ""
passing = ""

while (count < len(filesListed)):
    #print(filesListed[count])
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
            className = root.getAttribute("name").split(".")[-1]
            #print(className)
            for node in root.childNodes:
                if node.nodeName == "testcase":
                    if node.hasAttribute("name"):
                        testName = node.getAttribute("name")
                        #print(testName)
                    if len(node.childNodes) != 0:
                        passing = "F"
                    else:
                        passing = "P"
                    #print(passing)

                    #If we get any records returned, then obviously it's already in the table we don't
                    #have to insert.  Otherwise, if there are no returned records, then we need to
                    #insert them into the table.
                    cur.execute("SELECT * FROM testTable WHERE Package = %s and Class = %s and \
                                        Method = %s",(currentPacka, currentClass, item))
                    if cur.rowcount == 0:
                        #debug
                        #print("PKG: " + currentPacka.ljust(20) + " | CLS: " + currentClass.ljust(30) + \
                        #        " | MTD: " + item.ljust(40) + " | Adding to DB.")
                        try:
                            cur.execute("INSERT INTO methodUID(methodUID, Package, Class, Method) VALUES \
                                            (NULL, %s, %s, %s)",(currentPacka, currentClass, item))
                        except e:
                            #debug
                            print(e[0] + "|" + e[1])
                            connection.rollback()
                    else:
                        pass
                        #debug
                        #print("PKG: " + currentPacka.ljust(20) + " | CLS: " + currentClass.ljust(30) + \
                        #        " | MTD: " + item.ljust(40) + " | Already exists in DB.")
                    # Gets information ready to be added to DB
                    # This one goes to testTable
                    try:

                        add_testTable = ("INSERT INTO testTable (CommitUID, Class, Name, Passing) " \
                              "VALUES ( '%d', '%s', '%s', '%s')" % ( -1, className, testName, passing))

                        #Checking, delete print
                        #print(add_testTable)
                    except:
                        print("Messup", sys.exc_info())
                    # Attempts to insert information into database. If it doesn't match, it catches in the except and prints it.
                    try:
                        cur.execute(add_testTable)
                    except:
                        print("Error in committing", sys.exc_info())
    count += 1

# Closing connection
connection.close()
