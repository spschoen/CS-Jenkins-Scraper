#Building custom Checkstyle parser since none exist. RIP @me
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
# import pymysql.connector

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[len(sys.argv) - 1].split("/"):
    if arg == "":
        continue
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
# Future people: change this to your master IP
# Or wherever your DB is.
# Don't forget to
connection = pymysql.connect(host="152.46.20.243",
   user="root",
   passwd="",
   db="repoinfo")
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
