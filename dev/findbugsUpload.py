# Custom find bugs xml parser
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 findbugsUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUM
# 0. findbugsUpload.py
# 1. WORKSPACE  : /path/to/working/directory
# 2. PROJECT_ID : PW-XYZ
# 3. GIT_COMMIT : [40 char commit hash]

from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[1].split("/"):
    if arg == "":
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(FILE_DIR)

try:
    findbuggies = xml.dom.minidom.parse(FILE_DIR + '/findbugs.xml')
except:
    print("ERROR: Could not interact with file", FILE_DIR + '/findbugs.xml')
    print("Script exiting.")
    sys.exit()

# Getting commitUID info
repoID = sys.argv[2]
hash = sys.argv[3]

#root is the first <> element in the XML file.
root = findbuggies.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243", user="root", password="", db="repoinfo")
cur = connection.cursor()

#CommitUID getting
CUID = -1
commitUIDSelect = "SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s"
cur.execute(commitUIDSelect, (hash, repoID) )
if cur.rowcount == 0: #UID doesn't exist
    try:
        cur.execute("INSERT INTO commitUID(commitUID, Hexsha, Repo) VALUES \
                        (NULL, %s, %s)", (hash, repoID) )
        cur.execute(commitUIDSelect, (hash, repoID) )
        CUID = cur.fetchone()[0]
    except e:
        print(e[0] + "|" + e[1])
        connection.rollback()
else:
    CUID = cur.fetchone()[0] #Get the actual UID since it exists

if CUID == -1:
    print("Could not get CUID")
    sys.exit()

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
                if classNode.nodeName == "Method":
                    if classNode.hasAttribute("classname"):
                        string = classNode.getAttribute("classname")
                        package = string.split(".")[-1]
                        className = string.split(".")[-2]
                    if classNode.hasAttribute("name"):
                        method = classNode.getAttribute("name")
                if classNode.nodeName == "SourceLine":
                    if classNode.hasAttribute("start"):
                        line = int(classNode.getAttribute("start"))

        # If we get any records returned, then it's already in the table. Otherwise, if there are no returned records,
        # then we need to insert them into the table.
        cur.execute("SELECT * FROM methodUID WHERE Method = %s", (method))

        if cur.rowcount == 0: #The values do not exist in the testMethodUID table
                #Check if classUID values at least exist, which may not be possible if methodUID doesn't exist, but it's double checking.
                cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s", (package, className))

                if cur.rowcount == 0: #They don't exist, so add the values into the testMethodUID and testClassUID tables
                #Insert into classUID table first to generate the classUID for the testMethodUID table
                    try:
                        cur.execute("INSERT INTO classUID(classUID, Package, Class)" \
                        " VALUES (NULL, %s, %s)", (package, className))

                    except e:
                        print(e[0] + "|" + e[1])
                        connection.rollback()

                    #Execute the same select, so we can get the new classUID
                    cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s", (package, className))

                #Checking again, looking to make sure that we uploaded.
                if cur.rowcount == 0:
                    print("Somehow, we inserted and could not insert a classUID.  Exiting.")
                    sys.exit()
                elif cur.rowcount != 1:
                    print("Multiple matches for classUID table.  How even?")
                    sys.exit()
                else:
                    #Now we can actually get the number.
                    classUID = int(cur.fetchone()[0])

                #Insert into methodUID table
                try:
                    cur.execute("INSERT INTO methodUID(methodUID, ClassUID, Method)" \
                    " VALUES (NULL, %s, %s)", (classUID, method))

                except e:
                    print(e[0] + "|" + e[1])
                    connection.rollback()
                #Reset cursor for below
                cur.execute("SELECT * FROM methodUID WHERE Method = %s", (method))

        #Grab methodUID for below. By now, it should definitely exist
        methodUID = int(cur.fetchone()[0])
        # This one goes to findbugs
        try:
            add_findbugs = ("INSERT INTO findBugs(CommitsUID, MethodUID, BugType, Priority, Rank, Category, Line) " \
                  "VALUES ( '%d', '%d', '%s', '%d', '%d', '%s', '%d')" % ( CUID, methodUID, bugType, priority, rank, cat, line))
            cur.execute(add_findbugs)
        except:
            for error in sys.exec_info():
                print(error)

# Closing connection
connection.close()
