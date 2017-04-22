"""
Reads local git directory, lines of code, and more, and uploads relevant information to given database.

Requirements:
    MySQL_Func.py - library for interaction with databases must be available in the same directory as this file.
    config.txt    - file specifying database information.

Args:
    1. WORKSPACE  - Absolute path to the location of the .git directory
    2. PROJECT_ID - 17 char string representing class, section, project, and unique ID of the current project.
                    For example: csc216-002-P2-096
    3. GIT_COMMIT - 40 Character commit hash.
    4. BUILD_NUM  - Integer, the build number.

Returns:
    N/A

Authors:
    Renata Ann Zeitler
    Samuel Schoeneberger
"""

import sys
import os
import pymysql
import xml.dom.minidom
import shutil
import subprocess
import platform
from git import *
import MySQL_Func

if len(sys.argv) != 5:
    print("Invalid number of arguments.")
    sys.exit()

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
if platform.system() is "Windows":
    FILE_DIR = ""
else:
    FILE_DIR = "/"

# Iterate through the path to git to set up the directory.
for arg in sys.argv[1].split("/"):
    if ":" in arg:
        FILE_DIR = os.path.join(FILE_DIR, arg + "\\")
    elif arg != "":
        FILE_DIR = os.path.join(FILE_DIR, arg)
    # print(arg.ljust(25) + " | " + FILE_DIR)

repoID = sys.argv[2]
commitHash = sys.argv[3]
Build_Num = sys.argv[4]

CUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=commitHash, repoID=repoID)

# print(FILE_DIR)

try:
    repo = Repo(path=(FILE_DIR + "/.git/"))
    tree = repo.tree()
except:
    print("Could not locate git directory.  Exiting.")
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

# So, because of how Jenkins works, the following code is irrelevant.
# It was intended to calculate how long it's been since Javadoc was generated
# So the user would be warned in the dashboard.  Because Jenkins deletes the
# workspace on each build, it basically just gets a few seconds after the commit.
# AKA useless.  So we leave it as -1.

last_mod = -1

"""try:
    statinfo = os.stat(os.getcwd() + '/doc')
    last_mod = statinfo.st_mtime
except:
    last_mod = -1


def get_dir_comp(directory, length):
    global last_mod
    for file in os.listdir(directory):
        if os.path.isdir(directory + "/" + file):
            # print(" " * length + file + "/")
            get_dir_comp(directory + "/" + file, length + 4)
        elif "html" in file:
            pass
            statinfo = os.stat(directory + "/" + file)
            if statinfo.st_mtime > last_mod:
                last_mod = statinfo.st_mtime
            # print(" " * length + item)


try:
    get_dir_comp(os.getcwd() + '/doc', 0)
except:
    last_mod = -1"""

# CLOC and parsing.

LOC = 0
# Verifying the CLOC is installed
# Commented out because doesn't work on Windows.
if shutil.which("cloc") is None:
    print("ERROR: CLOC utility is required to be installed.")
    # print("Script exiting.")
    # sys.exit()
    LOC = "0"
else:
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
commitFind = "SELECT * FROM commits WHERE CommitUID = %s"

cur.execute(commitFind, CUID)

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
                                 Message[:50], LOC, LOC_DIFF, last_mod)

connection.close()
