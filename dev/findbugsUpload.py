"""
Reads findbugs xml file uploads any records into given database.

Requirements:
    Scraper.py  - library for interaction with databases must be available in the same directory as this file.
    config.json - file specifying database information.

Args:
    1. WORKSPACE  - Absolute path to the location of the findbugs.xml file
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

FILE_DIR = Scraper.get_file_dir(sys.argv[1])

# Getting commitUID info
repo_id = sys.argv[2]
commit_hash = sys.argv[3]

if not (os.path.isfile(FILE_DIR + "/findbugs.xml")):
    print("Could not access " + FILE_DIR + "/findbugs.xml" + " Exiting.")
    sys.exit()

try:
    findbug_xml = xml.dom.minidom.parse(FILE_DIR + "/findbugs.xml")
except:
    print("Could not access findbugs xml file, but it exists.")
    sys.exit()

# root is the first <> element in the XML file.
root = findbug_xml.documentElement

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

# CommitUID getting
commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], commit_hash=commit_hash, repo_id=repo_id)

package = ""
class_name = ""
method = ""
bugType = ""
priority = 0
rank = 0
cat = ""
line = 0

for node in root.childNodes:
    # If it's not a <BugInstance>, we don't need it.
    if node.nodeName != "BugInstance" or node.nodeType == node.TEXT_NODE:
        continue

    bugType = node.getAttribute("type")
    if node.hasAttribute("priority"):
        priority = int(node.getAttribute("priority"))
    if node.hasAttribute("rank"):
        rank = int(node.getAttribute("rank"))
    if node.hasAttribute("category"):
        cat = node.getAttribute("category")
    for classNode in node.childNodes:
        if classNode.nodeType == classNode.TEXT_NODE:
            continue
        if classNode.nodeName == "Method" and not classNode.hasAttribute("role"):
            if classNode.hasAttribute("classname"):
                string = classNode.getAttribute("classname")
                package = string.split(".")[-1]
                class_name = string.split(".")[-2]
            if classNode.hasAttribute("name"):
                method = classNode.getAttribute("name")
        if classNode.nodeName == "SourceLine" and classNode.hasAttribute("start"):
            line = int(classNode.getAttribute("start"))

    # Grab methodUID for below. By now, it should definitely exist

    method_uid = Scraper.get_method_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                        db=config_info['db'], package=package, class_name=class_name,
                                        method=method)
    search = "SELECT * FROM findBugs WHERE CommitUID = %s AND MethodUID = %s AND BugType = %s AND Priority = %s " \
             "AND Rank = %s and Category = %s AND Line = %s"

    cur.execute(search, (commit_uid, method_uid, bugType, priority, rank, cat, line))
    if cur.rowcount != 0:
        continue

    add_findbugs = "INSERT INTO findBugs(CommitUID, MethodUID, BugType, Priority, Rank, Category, Line) VALUES " \
                   "(%s, %s, %s, %s, %s, %s, %s)"
    # This one goes to findbugs
    try:
        cur.execute(add_findbugs, (commit_uid, method_uid, bugType, priority, rank, cat, line))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]

        v_list = "(CommitUID, MethodUID, BugType, Priority, Rank, Category, Line)"
        Scraper.sendFailEmail("Failed to insert into findBugs table!", "The following insert failed:",
                              add_findbugs, v_list, ErrorString, commit_uid, method_uid, bugType, priority,
                              rank, cat, line)

# Closing connection
connection.close()
