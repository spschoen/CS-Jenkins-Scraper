"""
Reads student test reports and uploads them to the given Database.

Requirements:
    Scraper.py - library for interaction with databases must be available in the same directory as this file.
    config.txt    - file specifying database information.

Args:
    1. WORKSPACE  - Absolute path to the location of test-reports/, which contains the test XML files.
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

if len(sys.argv) != 4:
    print("Did not get expected arguments.")
    print("$WORKSPACE $PROJECT_ID $GIT_COMMIT")
    sys.exit()

FILE_DIR = Scraper.get_file_dir()

# Getting to the right directory
if '/test-reports/' not in FILE_DIR:
    FILE_DIR += '/test-reports/'

# Directory to XML set up.

# Getting commitUID info
repo_id = sys.argv[2]
commit_hash = sys.argv[3]

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

# CommitUID getting
commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    DB=config_info['db'], hash=commit_hash, repo_id=repo_id)

# Initialize variables
package = ""
method = ""
className = ""
test_name = ""
passing = ""

for file in os.listdir(FILE_DIR):
    if not (str(file).endswith(".xml")):
        continue
    try:
        DOMTree = xml.dom.minidom.parse(FILE_DIR + file)
    except:
        print("ERROR: Could not interact with file " + FILE_DIR + file)
        sys.exit()

    root = DOMTree.documentElement

    if root.hasAttribute("name"):
        temp = root.getAttribute("name")
        class_name = temp.split(".")[-1]
        package = temp.split(".")[-2]

        for node in root.childNodes:
            message = ""
            if node.nodeName == "testcase":
                if node.hasAttribute("name"):
                    test_name = node.getAttribute("name")
                if len(node.childNodes) != 0:
                    passing = "F"
                    for test_case_child in node.childNodes:
                        if test_case_child.nodeType != test_case_child.TEXT_NODE:
                            message = test_case_child.getAttribute("message")
                else:
                    passing = "P"

                test_method_uid = Scraper.get_test_method_uid(ip=config_info['ip'], user=config_info['user'],
                                                              pw=config_info['pass'], db=config_info['db'],
                                                              method=test_name, class_name=class_name, package=package)

                # If we get any records returned, then it's already in the table.
                # Otherwise, if there are no returned records, then we need to insert
                # them into the table.
                find = "SELECT * FROM testTable WHERE CommitUID = %s AND testMethodUID = %s AND Passing = %s"
                cur.execute(find, (commit_uid, test_method_uid, passing))

                if cur.rowcount == 0:
                    testInsert = "INSERT INTO testTable(CommitUID, testMethodUID, Passing, Message)" \
                                 "VALUES (%s, %s, %s, %s)"
                    try:
                        cur.execute(testInsert, (commit_uid, test_method_uid, passing, message))
                    except:
                        connection.rollback()
                        ErrorString = sys.exc_info()[0] + "\n----------\n"
                        ErrorString += sys.exc_info()[1] + "\n----------\n"
                        ErrorString += sys.exc_info()[2]

                        v_list = "(CommitUID, test_method_uid, Passing, Message)"
                        Scraper.sendFailEmail("Failed to insert into test Results table!",
                                              "The following insert failed:", testInsert, v_list, ErrorString,
                                              str(commit_uid), str(test_method_uid), str(passing), str(message))

connection.close()
