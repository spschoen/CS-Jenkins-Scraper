# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 commitUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUM
# 0. commitUpload.py
# 1. WORKSPACE  : /path/to/.git (ABSOLUTE: As given by $WORKSPACE) DO NOT ADD .git
# 2. PROJECT_ID : PW-XYZ
# 3. GIT_COMMIT : [40 char commit hash]
# 4. BUILD_NUM  : integer

import sys
import os
import pymysql
import xml.dom.minidom
import shutil
import subprocess
from git import *
import MySQL_Func

# TODO: CHANGE THESE IN PRODUCTION
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()

# Getting path to .git directory.
FILE_DIR = "/"
# Iterate through the path to git to set up the directory.
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    #print(arg.ljust(20) + " | " + FILE_DIR)

repoID = sys.argv[2]
hash = sys.argv[3]
CUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)
Build_Num = sys.argv[4]

try:
    repo = Repo(path=FILE_DIR)
    tree = repo.tree()
except:
    # debug
    for error in sys.exc_info():
        print("Unexpected error:", error + "")
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

# Build number is ignored because, fun fact, it can be different while
# the rest is the same.  This causes an error where commitUID is the say when it should be
# changed.  I can't explain it well but trust me.
# TODO: update Build_Num in this situation
commitFind = "SELECT * FROM commits WHERE CommitUID = %s and Author = %s " + \
                "and Time = %s and Duration = %s and LOC = %s and LOC_DIFF = %s"

cur.execute( commitFind, (CUID, Author, Time, Duration, LOC, LOC_DIFF) )

if cur.rowcount == 0:
    insert = "INSERT INTO commits (CommitUID, Build_Num, Author, Time, Duration, Message, "
    insert += "LOC, LOC_DIFF) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(insert, (CUID, Build_Num, Author, Time, Duration, Message[:50], LOC, LOC_DIFF))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]

        v_list = "(CommitUID, Build_Num, Author, Time, Duration, Message, LOC, LOC_DIFF)"

        MySQL_Func.sendFailEmail("Failed to insert into checkstyle table!",
                                    "The following insert failed:",
                                    insert,
                                    v_list,
                                    ErrorString,
                                    CUID, Build_Num, Author, Time, Duration,
                                    Message[:50], LOC, LOC_DIFF)

connection.close()
