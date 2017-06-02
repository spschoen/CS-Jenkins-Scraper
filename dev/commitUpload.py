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
    5. PROJECT_ID - Name of project.  Likely "Project1" or "Project2" ...

Returns:
    N/A

Authors:
    Renata Ann Zeitler
    Samuel Schoeneberger
"""

import sys
import os
import xml.dom.minidom
import shutil
import subprocess
import Scraper
import pymysql
import platform

######################################################################

if len(sys.argv) != 6:
    print("Invalid number of arguments.")
    sys.exit()

# Getting some CLA
FILE_DIR = Scraper.get_file_dir(sys.argv[1])
repo_id = sys.argv[2]
commit_hash = sys.argv[3]
build_num = sys.argv[4]
project_name = sys.argv[5]

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

# Checking if the commit already exists in the table, and if so, just skip doing any scraping
commitFind = "SELECT * FROM commits WHERE Commit_Hash = %s AND Repo = %s"
cur.execute(commitFind, (commit_hash, repo_id))

# The record exists, so we don't need to scrape.
if cur.rowcount > 0:
    connection.close()
    sys.exit()

######################################################################

# Compile_ST
# Compile_TS

# Compile flags are generated by Jenkins after each build.  Post-build tasks will run, scanning logs
# for whether java has failed compiling or not.  See documentation in repo for more information on this.

try:
    compileLines = list(open("compLog.txt", "r"))
    Compile_ST = compileLines[0].replace("\n", "")
    Compile_TS = compileLines[1].replace("\n", "")
    os.remove("compLog.txt")
except:
    # Compilation successful.
    Compile_ST = "Y"
    Compile_TS = "Y"

######################################################################

# Author
# Time
# Duration
# Message

# Scan the git directory for the latest commit, its author, date, and duration since last commit.

git_dir = FILE_DIR
if platform.system() is "Windows":
    git_dir += "\\.git\\"
else:
    git_dir += "/.git/"

# Command + Arguments to be called by python to shell.

# this command prints out commit hash, ISO 8601 time, and sanitized commit message.  Example:
# "spschoen - 2017-05-02T19:58:13-04:00 - Fixing-lib-issue-for-future-copies - 5e17be445b8d7d0b7b4e905b6937331614c3124b"
git_log_command = ["git", "--git-dir=" + git_dir, "log", "-n", "2", "--pretty=format:\"%an - %at - %f - %H\""]

# We use check_output instead of call, because we want to save the output instead of immediately printing to stdout
# Since it comes back as bytes, we have to decode it using utf-8 to turn into a string, and then since it's one big
# String with as many newlines, we split it to get each individual record.
# We also have to remove the " char because it gets added from bytes, and is not needed.
last_two_commits = subprocess.check_output(git_log_command).decode("utf-8").replace("\"", "")
last_two_commits = last_two_commits.split("\n")

# Then, we split the split strings into more split strings, based off " - ", as we used in the --pretty option.
# This lets us get author, time, and message easily.
latest_commit = last_two_commits[0].split(" - ")
previous_commit = last_two_commits[1].split(" - ")

# Now we can get information
author = latest_commit[0][:8]
message = latest_commit[2][:50].replace("-", " ")
time = latest_commit[1]
duration = int(latest_commit[1]) - int(previous_commit[1])

# We also get the hash of the second to last commit, for use in Line of Code calculation
second_to_last_hash = previous_commit[3]

######################################################################

# Gen_Javadoc

# We do nearly exactly the same as above, but specifically on the doc/ directory.  We can tell if it
# exists or not, and how many commits its been since it was modified.
# Two special values are used:
#    -1 indicates that the doc/ directory exists but could not be read/accessed, and is a generic "failure" value
#    -2 indicates that the doc/ directory does not exist at the specific location

commits_since_doc_modified = -1

if platform.system() is "Windows":
    doc_dir = project_name + "\\doc\\"
    comp_doc_dir = project_name + "\\doc\\"
else:
    doc_dir = project_name + "/doc/"
    comp_doc_dir = project_name + "/doc/"

commits_since_doc_modified = -2

# check if the doc/ directory exists.  If it does, we continue.  If not, set to -2 for the DB.
if os.path.isdir(FILE_DIR + comp_doc_dir):
    # Get the last change to doc/ dir
    git_log_doc_command = ["git", "-C", git_dir, "log", "-n 1", "--pretty=format:\"%an - %at - %f\"", "--", doc_dir]
    last_mod_doc = subprocess.check_output(git_log_doc_command).decode("utf-8").replace("\"", "")

    last_doc_change_time = last_mod_doc.split(" - ")[1]
    # print(last_doc_change_time)

    # Get the number of commits since the commit found above
    # We add 1 to the commit time of the last change to doc/ because otherwise, it includes the
    # Change to doc.
    git_log_doc_command = ["git", "-C", git_dir, "log", "--pretty=format:\"%an - %at - %f\"",
                           "--since=\"" + str(int(last_doc_change_time) + 1) + "\""]
    commits_since_doc_change = subprocess.check_output(git_log_doc_command).decode("utf-8").replace("\"", "")
    # print(len(commits_since_doc_change.split("\n")))

    if last_mod_doc == '':
        commits_since_doc_modified = -2
    else:
        commits_since_doc_modified = int(len(commits_since_doc_change.split("\n")))
        pass

# print(commits_since_doc_modified)

######################################################################

# Code_lines
# Comment_Lines
# Class_Count

lines_of_code = -1
lines_of_comments = -1
classes = -1

# Verifying the CLOC is installed
if shutil.which("CLOC") is not None:
    # Sending CLOC output to /dev/null
    DEVNULL = open(os.devnull, 'wb')

    # NOTE: Maybe update this to only pull from src/ and not anything else?
    subprocess.call(["CLOC", FILE_DIR, "--by-file-by-lang", "--exclude-ext=xml", "--exclude-dir=gui,reference,output",
                     "--xml", "--out=CLOC.xml"], stdout=DEVNULL)

    # Get the parser, set it up to parse CLOC.xml
    try:
        DOMTree = xml.dom.minidom.parse("CLOC.xml")
        root = DOMTree.documentElement.getElementsByTagName('languages')[0]
        for node in root.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            if node.hasAttribute("name") and "Java" == node.getAttribute("name"):
                if node.hasAttribute("code") and not node.getAttribute("code") == "":
                    lines_of_code = node.getAttribute("code")
                if node.hasAttribute("comment") and not node.getAttribute("comment") == "":
                    lines_of_comments = node.getAttribute("comment")
                if node.hasAttribute("files_count") and not node.getAttribute("files_count") == "":
                    classes = node.getAttribute("files_count")
    except:
        print("Could not parse CLOC.xml, setting outputs to -1")
        lines_of_code = -1
        lines_of_comments = -1
        classes = -1
else:
    print("ERROR: CLOC utility is required to be installed.")
    # print("Script exiting.")
    # sys.exit()
    pass

######################################################################

# Method_Count

methodList = list(open("methods.txt", "r"))
methodCount = 0
for line in methodList:
    if "dir" not in line and line != "\n":
        # print(line.replace("\n", ""))
        methodCount += 1

# print(methodCount)

######################################################################

# Removed checking if the record exists in the DB, because that happens at the start.
# There should be no duplicate commit hashes in the database

insert = "INSERT INTO commits (CommitUID, Commit_Hash, Repo, Build_Num, Compile_ST, Compile_TS, Author, Time," \
         "Duration, Message, Code_Lines, Comment_Lines, Commits_Since_Javadoc, Method_Count, Class_Count) " \
         "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

print(commit_hash, repo_id, build_num, Compile_ST, Compile_TS, author, time, duration, message, lines_of_code,
      lines_of_comments, commits_since_doc_modified, methodCount, classes)

try:
    cur.execute(insert, (commit_hash, repo_id, build_num, Compile_ST, Compile_TS, author, time, duration, message,
                         lines_of_code, lines_of_comments, commits_since_doc_modified, methodCount, classes))
except:
    connection.rollback()
    ErrorString = sys.exc_info()[0] + "\n----------\n"
    ErrorString += sys.exc_info()[1] + "\n----------\n"
    ErrorString += sys.exc_info()[2]

    v_list = "(CommitUID, Build_Num, Compile_Stud, Compile_TS, Author, "
    v_list += "Time, Duration, Message, lines_of_code, lines_of_code_DIFF, Gen_Javadoc)"

    Scraper.sendFailEmail("Failed to insert into checkstyle table!", "The following insert failed:", insert,
                          v_list, ErrorString, commit_uid, Build_Num, Compile_Stud, Compile_TS, Author, Time,
                          Duration, Message[:50], lines_of_code, lines_of_code_DIFF, last_mod)

connection.close()
