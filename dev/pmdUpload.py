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

#root is the first <> element in the XML file.
root = pmd.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
connection = pymysql.connect(host="152.46.20.243", user="root", passwd="", db="repoinfo")
cur = connection.cursor()

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

    cur.execute("SELECT * FROM methodUID WHERE ClassUID = %s and Method = %s")
    methodUID = -1
    if cur.rowcount == 0:
        insertClassUID = "INSERT INTO methodUID(methodUID, ClasUID, Method) VALUES (NULL, %s, %s)"
        try:
            cur.execute(insertClassUID, (package, className) )
        except:
            for error in sys.exec_info():
                print(error)
            sys.exit()

    cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s", (package, className) )
    classUID = int(cur.fetchone()[0])

    insertMethodUID = "INSERT INTO methodUID(methodUID, ClassUID, Method) VALUES (NULL, %s, %s)"

    try:

    except:
        for error in sys.exec_info():
            print(error)
        sys.exit()

                # Gets information ready to be added to DB
                # This one is for methodUID
                try:
                    add_methodUID = ("INSERT INTO methodUID(methodUID, ClassUID, Method) " \
                        "VALUES (NULL, '%s', '%s')" % ( -1, method))

                    #print(add_methodUID)
                except:
                    print("Messup 1")

                # This one goes to pmd
                try:
                    add_pmd = ("INSERT INTO PMD(CommitUID, MethodUID, Ruleset, Rule, Line) " \
                          "VALUES ( '%d', '%d', '%s', '%s', '%d')" % ( -1, -1, ruleset, rule, line))

                    #print(add_pmd)
                except:
                    print("Messup 2", sys.exc_info())
                # Attempts to insert information into database. If it doesn't match, it catches in the except and prints it.
                try:
                    cur.execute(add_methodUID)
                    cur.execute(add_pmd)
                except:
                    print("Error in committing", sys.exc_info())

# Closing connection
connection.close()
