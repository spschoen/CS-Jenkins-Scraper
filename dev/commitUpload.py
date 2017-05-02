"""
Reads local git directory, lines of code, and more, and uploads relevant information to given database.

Requirements:
    Scraper.py - library for interaction with databases must be available in the same directory as this file.
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
from git import *
import Scraper

# This is useless code - it tells Pycharm to shut up about unused import statements.
__all__ = ['sys', 'os']

if len(sys.argv) != 5:
    print("Invalid number of arguments.")
    sys.exit()

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

FILE_DIR = Scraper.get_file_dir()

repo_id = sys.argv[2]
commit_hash = sys.argv[3]
Build_Num = sys.argv[4]

commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], commit_hash=commit_hash, repo_id=repo_id)

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
    Compile_Stud = compileLines[0].replace("\n", "")
    Compile_TS = compileLines[1].replace("\n", "")
except:
    # Compilation successful.
    Compile_Stud = "Y"
    Compile_TS = "Y"

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

cur.execute(commitFind, commit_uid)

if cur.rowcount == 0:
    insert = "INSERT INTO commits (CommitUID, Build_Num, Compile_Stud, Compile_TS, Author, Time, Duration, Message," \
             "LOC, LOC_DIFF, Gen_Javadoc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(insert, (commit_uid, Build_Num, Compile_Stud, Compile_TS, Author, Time, Duration, Message[:50], LOC,
                             LOC_DIFF, last_mod))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]

        v_list = "(CommitUID, Build_Num, Compile_Stud, Compile_TS, Author, "
        v_list += "Time, Duration, Message, LOC, LOC_DIFF, Gen_Javadoc)"

        Scraper.sendFailEmail("Failed to insert into checkstyle table!", "The following insert failed:", insert,
                              v_list, ErrorString, commit_uid, Build_Num, Compile_Stud, Compile_TS, Author, Time,
                              Duration, Message[:50], LOC, LOC_DIFF, last_mod)

connection.close()
