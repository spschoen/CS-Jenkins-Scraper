#Building custom Checkstyle parser since none exist. RIP @me
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[len(sys.argv) - 1].split("/"):
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

#root is the first <> element in the XML file.
root = findbuggies.documentElement

# Set up to read XML

# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = connection.cursor()

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

        # Gets information ready to be added to DB
        # This one is for methodUID
        try:
            add_methodUID = ("INSERT INTO methodUID(methodUID, Package, Class, Method) " \
                "VALUES (NULL, '%s', '%s', '%s')" % ( package, className, method))
            #print(add_methodUID)
        except:
            print("Messup 1")

        # This one goes to findbugs
        try:
            add_findbugs = ("INSERT INTO findBugs(CommitsUID, MethodUID, BugType, Priority, Rank, Category, Line) " \
                  "VALUES ( '%d', '%d', '%s', '%d', '%d', '%s', '%d')" % ( -1, -1, bugType, priority, rank, cat, line))
            #print(add_findbugs)
        except:
            print("Messup 2", sys.exc_info())
        # Attempts to insert information into database. If it doesn't match, it catches in the except and prints it.
        try:
            cur.execute(add_methodUID)
            cur.execute(add_findbugs)
            # cur.commit()
        except:
            print("Error in committing", sys.exc_info())
# Closing connection
connection.close()
