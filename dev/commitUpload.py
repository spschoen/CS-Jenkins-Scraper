"""
Reads local git directory, lines of code, and more, and uploads relevant information to given database.

Requirements:
    Scraper.py  - library for interaction with databases must be available in the same directory as this file.
    config.json - file specifying database information.

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
# Setup Section
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
# Setup complete
######################################################################

######################################################################
# Compile_ST - Flag of whether ST code compiled
# Compile_TS - Flag of whether TS code compiled
######################################################################

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
# Compilation Flags Section complete
######################################################################

######################################################################
# Author   - First 8 chars of latest commit
# Time     - unix epoch time of latest commit
# Duration - seconds since last commit
# Message  - commit message
######################################################################

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
# General information section complete
######################################################################

######################################################################
# Commits since Javadoc was last generated/modified
######################################################################

# We do nearly exactly the same as above, but specifically on the doc/ directory.  We can tell if it
# exists or not, and how many commits its been since it was modified.
# Two special values are used:
#    -1 indicates that the doc/ directory exists but could not be read/accessed, and is a generic "failure" value
#    -2 indicates that the doc/ directory does not exist at the specific location

if platform.system() is "Windows":
    doc_dir = project_name + "\\doc\\"
    comp_doc_dir = "\\" + project_name + "\\doc\\"
else:
    doc_dir = project_name + "/doc/"
    comp_doc_dir = "/" + project_name + "/doc/"

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
else:
    print("Failed to get doc dir, got: " + FILE_DIR + comp_doc_dir)
# print(commits_since_doc_modified)

######################################################################
# Javadoc check complete
######################################################################

######################################################################
# Src_Code_lines    - Lines of code     in src/
# Src_Comment_Lines - Lines of comments in src/
# Src_Class_Count   - Number of classes in src/
# Src_Method_Count  - Number of methods in src/
######################################################################

src_lines_of_code = -1
src_lines_of_comments = -1
src_classes = -1

src_dir = FILE_DIR
if platform.system() is "Windows":
    src_dir += "\\" + project_name + "\\src\\"
else:
    src_dir += "/" + project_name + "/src/"

# Verifying the CLOC is installed
if shutil.which("cloc") is not None:
    # Sending CLOC output to /dev/null
    DEVNULL = open(os.devnull, 'wb')

    subprocess.call(["cloc", src_dir, "--by-file-by-lang", "--exclude-ext=xml,html,css",
                     "--exclude-dir=gui,reference,output", "--xml", "--out=CLOC_src.xml"], stdout=DEVNULL)

    # Get the parser, set it up to parse CLOC_src.xml
    try:
        DOMTree = xml.dom.minidom.parse("CLOC_src.xml")
        root = DOMTree.documentElement.getElementsByTagName('languages')[0]
        for node in root.getElementsByTagName("language"):
            if not (node.hasAttribute("name") and "Java" == node.getAttribute("name")):
                continue

            if node.hasAttribute("code") and not node.getAttribute("code") == "":
                src_lines_of_code = node.getAttribute("code")
            if node.hasAttribute("comment") and not node.getAttribute("comment") == "":
                src_lines_of_comments = node.getAttribute("comment")
            if node.hasAttribute("files_count") and not node.getAttribute("files_count") == "":
                src_classes = node.getAttribute("files_count")
    except:
        print("Could not parse CLOC_src.xml, setting outputs to -1")
        src_lines_of_code = -1
        src_lines_of_comments = -1
        src_classes = -1
else:
    print("ERROR: CLOC utility is required to be installed.")

src_methodCount = -1
try:
    src_methodList = list(open("methods.txt", "r"))
    for line in src_methodList:
        if "dir" not in line and line != "\n":
            # print(line.replace("\n", ""))
            src_methodCount += 1
except:
    print("Could not open tests.txt")

######################################################################
# src/ number analysis complete
######################################################################

######################################################################
# test_Code_lines    - Lines of code     in test/
# test_Comment_Lines - Lines of comments in test/
# test_Class_Count   - Number of classes in test/
# test_Method_Count  - Number of methods in test/
######################################################################

test_lines_of_code = -1
test_lines_of_comments = -1
test_classes = -1

test_dir = FILE_DIR
if platform.system() is "Windows":
    test_dir += "\\" + project_name + "\\test\\"
else:
    test_dir += "/" + project_name + "/test/"

# Verifying the CLOC is installed
if shutil.which("cloc") is not None:
    # Sending CLOC output to /dev/null
    DEVNULL = open(os.devnull, 'wb')

    subprocess.call(["cloc", test_dir, "--by-file-by-lang", "--exclude-ext=xml,html,css",
                     "--exclude-dir=gui,reference,output", "--xml", "--out=CLOC_test.xml"], stdout=DEVNULL)

    # Get the parser, set it up to parse CLOC_test.xml
    try:
        DOMTree = xml.dom.minidom.parse("CLOC_test.xml")
        root = DOMTree.documentElement.getElementsByTagName('languages')[0]
        for node in root.getElementsByTagName("language"):
            if not (node.hasAttribute("name") and "Java" == node.getAttribute("name")):
                continue

            if node.hasAttribute("code") and not node.getAttribute("code") == "":
                test_lines_of_code = node.getAttribute("code")
            if node.hasAttribute("comment") and not node.getAttribute("comment") == "":
                test_lines_of_comments = node.getAttribute("comment")
            if node.hasAttribute("files_count") and not node.getAttribute("files_count") == "":
                test_classes = node.getAttribute("files_count")
    except:
        print("Could not parse CLOC_test.xml, setting outputs to -1")
        test_lines_of_code = -1
        test_lines_of_comments = -1
        test_classes = -1
else:
    print("ERROR: CLOC utility is required to be installed.")

test_methodCount = -1
try:
    test_methodList = list(open("tests.txt", "r"))
    for line in test_methodList:
        if "dir" not in line and line != "\n":
            # print(line.replace("\n", ""))
            test_methodCount += 1
except:
    print("Could not open tests.txt")

######################################################################
# test/ number analysis complete
######################################################################

######################################################################
# Counting number of asserts in test/
# Ignores commented assert statements
######################################################################

# Assert_Count

assert_count = 0

for root, dirs, files in os.walk(test_dir):
    for name in files:
        # print(name)
        with open(os.path.join(root, name)) as test_file:
            in_block_comment = False
            for line in test_file:
                if "/*" in line:
                    in_block_comment = True
                if "*/" in line:
                    in_block_comment = False
                if not in_block_comment and "assert" in line:
                        if "//" in line:
                            compare = line.split("//")[0]
                            if "assert" in compare:
                                assert_count += 1
                        else:
                            assert_count += 1

######################################################################
# Assert count complete
######################################################################

######################################################################
# Stacktrace acquisition
######################################################################


test_dir = FILE_DIR
if platform.system() is "Windows":
    f = open(FILE_DIR + "\\" + project_name + "\\" + "ant.log", "r")
else:
    f = open(FILE_DIR + "/" + project_name + "/" + "ant.log", "r")

javac_lines = []
stacktrace = ""

for line in f.readlines():
    # print(line.replace("\n", ""))
    fixed_line = line.replace("\n", "")
    if "[javac]" in fixed_line:
        if "Compiling" in fixed_line:
            continue
        javac_lines.append(fixed_line.split("[javac] ")[1])

if len(javac_lines) != 0:
    for line in javac_lines:
        stacktrace += line + "\n"

# Fixing some problems for the Dashboard.
stacktrace.replace("\t", "    ")

######################################################################
# Stacktrace found/ignored
######################################################################

######################################################################
# Database uploading
######################################################################

# Removed checking if the record exists in the DB, because that happens at the start.
# There should be no duplicate commit hashes in the database

insert = "INSERT INTO commits (CommitUID, Commit_Hash, Repo, Build_Num, Compile_ST, Compile_TS, Author, Time, " \
         "Duration, Message, Src_Code_Lines, Src_Comment_Lines, Src_Class_Count, Src_Method_Count, Test_Code_Lines, " \
         "Test_Comment_Lines, Test_Classes, Test_Method_Count, Assert_Count, Commits_Since_Javadoc, Stacktrace) " \
         "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

try:
    cur.execute(insert, (commit_hash, repo_id, build_num, Compile_ST, Compile_TS, author, time, duration, message,
                         src_lines_of_code, src_lines_of_comments, src_classes, src_methodCount, test_lines_of_code,
                         test_lines_of_comments, test_classes, test_methodCount, assert_count,
                         commits_since_doc_modified, stacktrace))
except:
    connection.rollback()
    Error_String = str(sys.exc_info()[0]) + "\n----------\n"
    Error_String += str(sys.exc_info()[1]) + "\n----------\n"
    Error_String += str(sys.exc_info()[2])

    v_list = "(CommitUID, Commit_Hash, Repo, Build_Num, Compile_ST, Compile_TS, Author, Time, Duration, Message, " \
             "Src_Code_Lines, Src_Comment_Lines, Src_Class_Count, Src_Method_Count, Test_Code_Lines, " \
             "Test_Comment_Lines, Test_Classes, Test_Method_Count, Assert_Count, Commits_Since_Javadoc, Stacktrace)"

    Scraper.sendFailEmail("Failed to insert into checkstyle table!", "The following insert failed:", insert,
                          v_list, Error_String, commit_hash, repo_id, build_num, Compile_ST, Compile_TS, author, time,
                          duration, message, src_lines_of_code, src_lines_of_comments, src_classes, src_methodCount,
                          test_lines_of_code, test_lines_of_comments, test_classes, test_methodCount, assert_count,
                          commits_since_doc_modified, stacktrace)

connection.close()
