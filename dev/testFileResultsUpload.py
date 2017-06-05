"""
Reads student test reports and uploads them to the given Database.

Requirements:
    Scraper.py         - library for interaction with databases must be available in the same directory as this file.
    config.json        - file specifying database information.
    (ts-)test-reports/ - directory of test report files to be scraped

Args:
    1. WORKSPACE  - Absolute path to the location of test-reports/, which contains the test XML files.
    2. PROJECT_ID - 17 char string representing class, section, project, and unique ID of the current project.
                    For example: csc216-002-P2-096
    3. GIT_COMMIT - 40 Character commit hash.
    4. PROJECT_ID - Name of project.  Likely "Project1" or "Project2" ...
    5. TEST_DIR   - Name of directory of test reports to be read in.  test-reports/ or ts-test-reports/, probably

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

######################################################################
# Setup Section
######################################################################

if len(sys.argv) != 6:
    print("Did not get expected arguments.")
    sys.exit()

FILE_DIR = Scraper.get_file_dir(sys.argv[1])

# Getting commitUID info
repo_id = sys.argv[2]
commit_hash = sys.argv[3]

######################################################################
# Setup Section partially complete
######################################################################

######################################################################
# Setting up reading the specific report directory
######################################################################

project_name = sys.argv[4]
if project_name not in FILE_DIR:
    if platform.system() is "Windows":
        FILE_DIR += "\\" + project_name + "\\"
    else:
        FILE_DIR += "/" + project_name + "/"

# Getting to the right directory

test_dir = sys.argv[5]

if test_dir not in FILE_DIR:
    if platform.system() is "Windows":
        FILE_DIR += "\\" + test_dir + "\\"
    else:
        FILE_DIR += "/" + test_dir + "/"

if "//" in FILE_DIR:
    FILE_DIR = FILE_DIR.replace("//", "/")
if "\\\\" in FILE_DIR:
    FILE_DIR = FILE_DIR.replace("\\\\", "\\")

######################################################################
# Report directory setup.
######################################################################

# Directory to XML set up.

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

# CommitUID getting
commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], commit_hash=commit_hash, repo_id=repo_id)

######################################################################
# Setup Section fully complete
######################################################################

######################################################################
# XML Setup/Reading/Uploading
######################################################################

# Initialize variables
package = ""
method = ""
class_name = ""
test_name = ""
passing = ""
message = ""
line = -1

for file in os.listdir(FILE_DIR):
    if not (str(file).endswith(".xml")):
        continue

    # Open parsing for test report
    try:
        DOMTree = xml.dom.minidom.parse(FILE_DIR + file)
    except:
        print("ERROR: Could not interact with file " + FILE_DIR + file)
        print(sys.exc_info())
        sys.exit()

    root = DOMTree.documentElement

    # If, for some reason, the root node lacks a name attribute, something horrible has happened we're skipping.
    if not root.hasAttribute("name"):
        continue

    temp = root.getAttribute("name")
    class_name = temp.split(".")[-1]
    package = temp.split(".")[-2]

    # TODO: Replace this with searching only through <testcase>
    for node in root.getElementsByTagName("testcase"):
        message = ""

        if node.hasAttribute("name"):
            test_name = node.getAttribute("name")

        if len(node.childNodes) != 0:
            passing = "F"

            # So, removed the for loop, because there's only one or no failures per method.
            # And since the first node is the new line, we just work with the second child node.

            message = node.childNodes[1].getAttribute("message")
            line = node.childNodes[1].firstChild.nodeValue.split("\n")[1].split(".java:")[1].split(")")[0]

        else:
            passing = "P"

        # If we get any records returned, then it's already in the table.
        # Otherwise, if there are no returned records, then we need to insert
        # them into the table.
        test_method_uid = Scraper.get_test_method_uid(ip=config_info['ip'], user=config_info['user'],
                                                      pw=config_info['pass'], db=config_info['db'],
                                                      method=test_name, class_name=class_name, package=package)

        if test_dir.startswith("ts"):
            find = "SELECT * FROM TS_testTable WHERE CommitUID = %s AND testMethodUID = %s AND Passing = %s"
        else:
            find = "SELECT * FROM testTable WHERE CommitUID = %s AND testMethodUID = %s AND Passing = %s"
        cur.execute(find, (commit_uid, test_method_uid, passing))

        if cur.rowcount == 0:
            if test_dir.startswith("ts"):
                testInsert = "INSERT INTO TS_testTable(CommitUID, testMethodUID, Passing, Message, Line)" \
                             " VALUES (%s, %s, %s, %s, %s)"
            else:
                testInsert = "INSERT INTO testTable(CommitUID, testMethodUID, Passing, Message, Line)" \
                             " VALUES (%s, %s, %s, %s, %s)"
            try:
                cur.execute(testInsert, (commit_uid, test_method_uid, passing, message, line))
            except:
                connection.rollback()
                Error_String = str(sys.exc_info()[0]) + "\n----------\n"
                Error_String += str(sys.exc_info()[1]) + "\n----------\n"
                Error_String += str(sys.exc_info()[2])

                v_list = "(CommitUID, test_method_uid, Passing, Message)"
                Scraper.sendFailEmail("Failed to insert into test Results table!", "The following insert failed:",
                                      testInsert, v_list, Error_String, str(commit_uid), str(test_method_uid),
                                      str(passing), str(message))

connection.close()
