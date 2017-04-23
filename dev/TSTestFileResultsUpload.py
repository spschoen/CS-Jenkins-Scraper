"""
Reads test reports and uploads
Requirements:
 - test[blaaaaah].xml must exist.  If not, this script won't read it.
 - Scraper.py for interacting with MySQL.
 - config.txt to read in variables for IP, DB, etc.

Execution:
 - python3 testFileResultsUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
   - Arguments:
     - 0. testFileResultsUpload.py
     - 1. WORKSPACE  : /path/to/test-reports/*.xml (DO NOT INCLUDE *.xml)
     - 2. PROJECT_ID : PW-XYZ
     - 3. GIT_COMMIT : [40 char commit commit_hash]

@author Renata Ann Zeitler
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

# Setting up the XML to read
FILE_DIR = Scraper.get_file_dir()

# Getting to the right directory
if '/ts-test-reports/' not in FILE_DIR:
    FILE_DIR += '/ts-test-reports/'

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
                                    db=config_info['db'], hash=commit_hash, repo_id=repo_id)

count = 0

# Initialize variables
package = ""
method = ""
class_name = ""
test_name = ""
passing = ""

for file in os.listdir(FILE_DIR):
    if file == '.DS_Store':
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
            if node.nodeName == "testcase":
                if node.hasAttribute("name"):
                    test_name = node.getAttribute("name")
                if len(node.childNodes) != 0:
                    passing = "F"
                else:
                    passing = "P"

                # If we get any records returned, then it's already in the table.
                # Otherwise, if there are no returned records, then we need to insert
                # them into the table.
                test_method_uid = Scraper.get_test_method_uid(ip=config_info['ip'], user=config_info['user'],
                                                              pw=config_info['pass'], db=config_info['db'],
                                                              method=test_name, class_name=class_name, package=package)

                find = "SELECT * FROM TS_testTable WHERE CommitUID = %s AND testMethodUID = %s AND Passing = %s"
                cur.execute(find, (commit_uid, test_method_uid, passing))

                if cur.rowcount == 0:
                    testInsert = "INSERT INTO TS_testTable(CommitUID, testMethodUID, Passing) VALUES (%s, %s, %s)"
                    try:
                        cur.execute(
                            testInsert, (commit_uid, test_method_uid, passing))
                    except:
                        connection.rollback()
                        ErrorString = sys.exc_info()[0] + "\n----------\n"
                        ErrorString += sys.exc_info()[1] + "\n----------\n"
                        ErrorString += sys.exc_info()[2]

                        v_list = "(commit_uid, test_method_uid, passing)"
                        Scraper.sendFailEmail("Failed to insert into TS Test Results table!",
                                              "The following insert failed:", testInsert, v_list, ErrorString,
                                              str(commit_uid), str(test_method_uid), passing)

connection.close()
