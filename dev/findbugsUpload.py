"""
Reads findbugs xml file uploads any records into given database.

Requirements:
    Scraper.py - library for interaction with databases must be available in the same directory as this file.
    config.txt    - file specifying database information.

Args:
    1. WORKSPACE  - Absolute path to the location of the findbugs.xml file
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
import Scraper
import platform

# Setting up the XML to read
if platform.system() is "Windows":
    FILE_DIR = "C:\\"
else:
    FILE_DIR = "/"

# Iterate through the path to git to set up the directory.
for arg in sys.argv[1].split("/"):
    if ":" in arg:
        FILE_DIR = os.path.join(FILE_DIR, arg + "\\")
    elif arg != "":
        FILE_DIR = os.path.join(FILE_DIR, arg)
    # print(arg.ljust(25) + " | " + FILE_DIR)

if not (os.path.isfile(FILE_DIR + "/findbugs.xml")):
    print("Findbugs.xml file does not exist.  Exiting.")
    sys.exit()

try:
    findbuggies = xml.dom.minidom.parse(FILE_DIR + "/findbugs.xml")
except:
    # This is commented out, because findbugs XML can be not created for a lot of reasons.
    '''ErrorString = sys.exc_info()[0] + "\n----------\n"
    ErrorString += sys.exc_info()[1] + "\n----------\n"
    ErrorString += sys.exc_info()[2]
    Scraper.sendFailEmail("Failed to read findbugs.xml", "The following command failed:",
                                "findbuggies = xml.dom.minidom.parse(FILE_DIR + "/findbugs.xml")",
                                "With the following variables (FILE_DIR)",
                                ErrorString, FILE_DIR)'''
    sys.exit()

# Getting commitUID info
repo_id = sys.argv[2]
commit_hash = sys.argv[3]

# root is the first <> element in the XML file.
root = findbuggies.documentElement

# Set up to read XML

# Setting up the DB connection
# Now, we begin reading the config file.
if not os.path.exists('config.txt'):
    # config.txt doesn't exist.  Don't run.
    # print("Could not access config.txt, exiting.")
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
CUID = Scraper.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=commit_hash, repo_id=repo_id)

if root.hasAttribute("version"):
    pass
    # print("FindBugs Version : %s" % root.getAttribute("version"))

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
                if classNode.nodeName == "Method" and not classNode.hasAttribute("role"):
                    if classNode.hasAttribute("classname"):
                        string = classNode.getAttribute("classname")
                        package = string.split(".")[-1]
                        className = string.split(".")[-2]
                    if classNode.hasAttribute("name"):
                        method = classNode.getAttribute("name")
                if classNode.nodeName == "SourceLine":
                    if classNode.hasAttribute("start"):
                        line = int(classNode.getAttribute("start"))

        # Grab methodUID for below. By now, it should definitely exist
        methodUID = Scraper.get_method_UID(IP=IP, user=user, pw=pw, DB=DB,
                                              className=className, package=package, method=method)
        search = "SELECT * FROM findBugs WHERE CommitUID = %s AND MethodUID = %s AND "
        search += "BugType = %s AND Priority = %s AND Rank = %s and Category = %s AND Line = %s"

        cur.execute(search, (CUID, methodUID, bugType, priority, rank, cat, line))
        if cur.rowcount != 0:
            continue

        add_findbugs = "INSERT INTO findBugs(CommitUID, MethodUID, BugType, Priority, "
        add_findbugs += "Rank, Category, Line) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # This one goes to findbugs
        try:
            cur.execute(add_findbugs, (CUID, methodUID, bugType, priority, rank, cat, line))
        except:
            connection.rollback()
            ErrorString = sys.exc_info()[0] + "\n----------\n"
            ErrorString += sys.exc_info()[1] + "\n----------\n"
            ErrorString += sys.exc_info()[2]

            v_list = "(CommitUID, MethodUID, BugType, Priority, Rank, Category, Line)"
            Scraper.sendFailEmail("Failed to insert into findBugs table!", "The following insert failed:",
                                     add_findbugs, v_list, ErrorString,
                                     CUID, methodUID, bugType, priority, rank, cat, line)

# Closing connection
connection.close()
