"""
Reads local git directory and uploads important info to table
Requirements:
 - .git/ must exist.  If not, this script will not read it.
 - MySQL_Func.py for interacting with MySQL.
 - config.txt to read in variables for IP, DB, etc.

UPDATE: this is hardcoded to match Jenkins set paths.

Execution:
 - python3 commitUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUM
   - Arguments:
     - 0. commitUpload.py
     - 1. WORKSPACE  : /path/to/checkstyle.xml (ABSOLUTE: As given by $WORKSPACE) DO NOT ADD file
     - 2. PROJECT_ID : PW-XYZ
     - 3. GIT_COMMIT : [40 char commit hash]
     - 4. BUILD_NUM  : integer

@author Renata Ann Zeitler
@author Samuel Schoeneberger
"""

import sys
import os
import pymysql
import xml.dom.minidom
import shutil
import subprocess
from git import *
import MySQL_Func
import time

# Now, we begin reading the config file.
if not os.path.exists('config.txt'):
    # config.txt doesn't exist.  Don't run.
    print("Could not access config.txt, exiting.")
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

# Getting path to .git directory.
FILE_DIR = "/"
#FILE_DIR = os.getcwd()
# Iterate through the path to git to set up the directory.
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(arg.ljust(20) + " | " + FILE_DIR)

repoID = sys.argv[2]
hash = sys.argv[3]
CUID = MySQL_Func.getCommitUID(
    IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)
Build_Num = sys.argv[4]

try:
    repo = Repo(path=FILE_DIR)
    tree = repo.tree()
except:
    sys.exit()
    # couldn't locate the repo

last_commit = list(repo.iter_commits(paths=FILE_DIR))[0]
second_to_last_commit = list(repo.iter_commits(paths=FILE_DIR))[1]
Author = last_commit.author.name[:8]
Message = last_commit.summary
Time = last_commit.committed_date
Doc = "N"

try:
    compileFile = open("compLog.txt", "r")
    compileLines = list(compileFile)
    studComp = compileLines[0].replace("\n", "")
    TSComp = compileLines[1].replace("\n", "")
except:
    # Compilation successful.
    studComp = "Y"
    TSComp = "Y"

statinfo = os.stat(os.getcwd() + '/doc')
last_mod = statinfo.st_mtime

def getDirComp(directory, length):
    global last_mod
    for item in os.listdir(directory):
        if os.path.isdir(directory + "/" + item):
            # print(" " * length + item + "/")
            getDirComp(directory + "/" + item, length + 4)
        elif "html" in item:
            pass
            statinfo = os.stat(directory + "/" + item)
            if statinfo.st_mtime > last_mod:
                last_mod = statinfo.st_mtime
            # print(" " * length + item)

getDirComp(os.getcwd() + '/doc', 0)

# CLOC and parsing.

LOC = 0
# Verifying the CLOC is installed
# Commented out because doesn't work on Windows.
if shutil.which("cloc") == None:
    print("ERROR: CLOC utility is required to be installed.")
    print("Script exiting.")
    sys.exit()

# Sending cloc output to /dev/null
DEVNULL = open(os.devnull, 'wb')

subprocess.call(["cloc", FILE_DIR, "--by-file-by-lang",
                 "--exclude-ext=xml", "--exclude-dir=gui,reference,output",
                 "--xml", "--out=cloc.xml"], stdout=DEVNULL)

# Get the parser, set it up to parse cloc.xml
try:
    DOMTree = xml.dom.minidom.parse('cloc.xml')
except:
    LOC = -1

root = DOMTree.documentElement.getElementsByTagName('languages')[0]
for node in root.childNodes:
    if node.nodeType == node.TEXT_NODE:
        continue
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

# So much gets ignored, mostly because CommitUID and Time are unique enough that we don't have to
# find the others - also, they can be different (like build number)
commitFind = "SELECT * FROM commits WHERE CommitUID = %s and Time = %s"

cur.execute(commitFind, (CUID, Time))

if cur.rowcount == 0:
    insert = "INSERT INTO commits (CommitUID, Build_Num, Compile_Stud, Compile_TS, Author, "
    insert += "Time, Duration, Message, LOC, LOC_DIFF, Gen_Javadoc) VALUES (%s, %s, %s, %s, "
    insert += "%s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(insert, (CUID, Build_Num, studComp, TSComp, Author, Time,
                             Duration, Message[:50], LOC, LOC_DIFF, last_mod))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]

        v_list = "(CommitUID, Build_Num, Compile_Stud, Compile_TS, Author, "
        v_list += "Time, Duration, Message, LOC, LOC_DIFF, Gen_Javadoc)"

        MySQL_Func.sendFailEmail("Failed to insert into checkstyle table!",
                                 "The following insert failed:",
                                 insert,
                                 v_list,
                                 ErrorString,
                                 CUID, Build_Num, Compile_Stud, Compile_TS, Author, Time, Duration,
                                 Message[:50], LOC, LOC_DIFF, Doc)

connection.close()
