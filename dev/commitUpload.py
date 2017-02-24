# Custom commit uploader
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 commitUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUM
# 0. commitUpload.py
# 1. WORKSPACE  : /path/to/.git (ABSOLUTE: As given by $WORKSPACE) DO NOT ADD .git
# 2. PROJECT_ID : PW-XYZ
# 3. GIT_COMMIT : [40 char commit hash]
# 4. BUILD_NUM  : integer

import sys
import os
import pymysql.cursors
import xml.dom.minidom
import shutil
import subprocess
from git import *
from datetime import date, datetime, timedelta

# Setting up the DB connection
connection = pymysql.connect(host="152.46.20.243", user="root", password="", db="repoinfo")
cur = connection.cursor()

# Getting path to .git directory.
FILE_DIR = "/"
# Iterate through the path to git to set up the directory.
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(arg.ljust(20) + " | " + FILE_DIR)

#Curious to see what happens.
#FILE_DIR += "/.git"

repoID = sys.argv[2]
hash = sys.argv[3]

cur.execute("SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s", (hash, repoID) )

if cur.rowcount == 0:
    try:
        pass
        insert = "INSERT INTO commitUID (commitUID, Hexsha, Repo) VALUES (NULL, %s, %s)"
        cur.execute( insert, (hash, repoID) )
    except e:
        # debug
        # print(e[0] + "|" + e[1])
        # TODO: email when failure happens.
        connection.rollback()

# So that was to get the commitUID set in there.
cur.execute("SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s", (hash, repoID) )

# And this is the new CUID!
CUID = cur.fetchone()[0]
Build_Num = sys.argv[4]
try:
    repo = Repo(path=FILE_DIR)
    tree = repo.tree()
except:
    # debug
    for error in sys.exc_info():
        print("Unexpected error:", error)
    sys.exit()
    # TODO: email when failure happens.

last_commit = list(repo.iter_commits(paths=FILE_DIR))[0]
second_to_last_commit = list(repo.iter_commits(paths=FILE_DIR))[1]
Author = last_commit.author.name
Message = last_commit.summary
Time = last_commit.committed_date

# CLOC and parsing.

LOC = 0

#Verifying the CLOC is installed
#Commented out because doesn't work on Windows.
if shutil.which("cloc") == None:
    print("ERROR: CLOC utility is required to be installed.")
    print("Script exiting.")
    sys.exit()

#Sending cloc output to /dev/null
DEVNULL = open(os.devnull, 'wb')

#Commented out because doesn't work on Windows.
subprocess.call(["cloc", FILE_DIR, "--by-file-by-lang", \
 "--exclude-ext=xml", "--exclude-dir=gui,reference,output", \
 "--xml", "--out=cloc.xml"], stdout=DEVNULL)

#Get the parser, set it up to parse cloc.xml
try:
    DOMTree = xml.dom.minidom.parse('cloc.xml')
except:
    LOC = -1

root = DOMTree.documentElement.getElementsByTagName('languages')[0]
for node in root.childNodes:
    if node.nodeType == node.TEXT_NODE:
        continue;
    if node.hasAttribute("name") and "Java" in node.getAttribute("name"):
        if node.hasAttribute("code") and not node.getAttribute("code") == "":
            LOC = node.getAttribute("code")
        else:
            sys.exit()

# CLOC done.
# LOC Diff, thanks to git, below.

LOC_DIFF = 0

for item in last_commit.stats.total:
    if item == "insertions":
        LOC_DIFF += last_commit.stats.total.get(item)
    if item == "deletions":
        LOC_DIFF -= last_commit.stats.total.get(item)

# lololol
Duration = Time - second_to_last_commit.committed_date

commitFind = "SELECT * FROM commits WHERE CommitUID = %s and Build_Num = %s and Author = %s " + \
                "and Time = %s and Duration = %s and LOC = %s and LOC_DIFF = %s"

cur.execute( commitFind, (CUID, Build_Num, Author, Time, Duration, LOC, LOC_DIFF) )

if cur.rowcount == 0:
    try:
        insert = "INSERT INTO commits (CommitUID, Build_Num, Author, Time, Duration, Message, " + \
                    "LOC, LOC_DIFF) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute( insert, (CUID, Build_Num, Author, Time, Duration, Message, LOC, LOC_DIFF) )
    except e:
        # debug
        # print(e[0] + "|" + e[1])
        # TODO: email when failure happens.
        connection.rollback()

connection.close()
