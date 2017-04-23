"""
Custom pmd xml parser
Requirements:
 - pmd.xml must exist.  If not, this script won't read it.
 - Scraper.py for interacting with MySQL.
 - config.txt to read in variables for IP, DB, etc.

Execution:
 - python3 pmdUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
   - Arguments:
     - 0. pmdUpload.py
     - 1. WORKSPACE  : /path/to/pmd.xml (DO NOT INCLUDE pmd.xml)
     - 2. PROJECT_ID : PW-XYZ
     - 3. GIT_COMMIT : [40 char commit commit_hash]

@author Renata Ann Zeitler
"""

import xml.dom.minidom
import sys
import pymysql
import Scraper
import os

FILE_DIR = Scraper.get_file_dir()

if not (os.path.isfile(FILE_DIR + "/pmd.xml")):
    print(FILE_DIR + "/pmd.xml")
    print("Could not access pmd.xml. Exiting.")
    sys.exit()

try:
    pmd = xml.dom.minidom.parse(FILE_DIR + '/pmd.xml')
except:
    # This is commented out, because pmd XML can be not created for a lot of reasons.
    print("Could not access pmd.xml.  Exiting.")
    '''error_string = sys.exc_info()[0] + "\n----------\n"
    error_string += sys.exc_info()[1] + "\n----------\n"
    error_string += sys.exc_info()[2]
    Scraper.sendFailEmail("Failed to read pmd.xml", "The following command failed:",
                                "pmd = xml.dom.minidom.parse(FILE_DIR + '/pmd.xml')",
                                "With the following variables (FILE_DIR)",
                                error_string, FILE_DIR)'''
    print("Could not access pmd xml file, but it exists.")
    sys.exit()

# Getting commitUID info
repo_id = sys.argv[2]
commit_hash = sys.argv[3]

# root is the first <> element in the XML file.
root = pmd.documentElement

# Set up to read XML

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

# CommitUID getting
commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], commit_hash=commit_hash, repo_id=repo_id)

# A basic for loop, to look at all the nodes (<> elements) inside the file node
# (which is now the root node) and print out their information to the DB.
# .childNodes is a list of nodes that the root has as children.
for file in root.childNodes:
    if file.nodeType != file.TEXT_NODE:
        for node in file.childNodes:
            package = ""
            className = ""
            method = ""
            line = 0
            rule = ""
            ruleset = ""
            if node.nodeType != node.TEXT_NODE:
                if node.hasAttribute("beginline"):
                    line = int(node.getAttribute("beginline"))
                if node.hasAttribute("rule"):
                    rule = node.getAttribute("rule")
                if node.hasAttribute("ruleset"):
                    ruleset = node.getAttribute("ruleset")
                if node.hasAttribute("package"):
                    package = node.getAttribute("package").split('.')[-1]
                if node.hasAttribute("class"):
                    className = node.getAttribute("class")
                if node.hasAttribute("method"):
                    method = node.getAttribute("method")
    else:
        continue

    # holy FRAK it fits on the 100 limit!
    if package == "" or className == "" or method == "" or rule == "" or ruleset == "" or line == 0:
        # print("Could not find an attribute.  Rerun with print debugging.")
        continue

    # Class UID
    methodUID = Scraper.get_method_UID(IP=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                       DB=config_info['db'], package=package, class_name=className, method=method)

    search = "SELECT * FROM PMD WHERE CommitUID = %s AND MethodUID = %s AND Ruleset = %s AND Rule = %s AND Line = %s"
    cur.execute(search, (str(commit_uid), str(methodUID), str(ruleset), str(rule), str(line)))
    if cur.rowcount != 0:
        continue

    # PMD time!
    insertPMD = "INSERT INTO PMD(CommitUID, MethodUID, Ruleset, Rule, Line) VALUES ( %s, %s, %s, %s, %s )"

    try:
        cur.execute(insertPMD, (str(commit_uid), str(methodUID), str(ruleset), str(rule), str(line)))
    except:
        connection.rollback()
        error_string = sys.exc_info()[0] + "\n----------\n"
        error_string += sys.exc_info()[1] + "\n----------\n"
        error_string += sys.exc_info()[2]

        v_list = "(CommitUID, MethodUID, Ruleset, Rule, Line)"
        Scraper.sendFailEmail("Failed to insert into PMD table!", "The following insert failed:", insertPMD, v_list,
                              error_string, str(commit_uid), str(methodUID), str(ruleset), str(rule), str(line))

# Closing connection
connection.close()
