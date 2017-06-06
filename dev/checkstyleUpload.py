"""
Reads checkstyle error file (checkstyle.xml) and uploads any records to the given Database.

Requirements:
    Scraper.py  - library for interaction with databases must be available in the same directory as this file.
    config.json - file specifying database information.

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

######################################################################
# Setup section
######################################################################

if len(sys.argv) != 4:
    print("Incorrect number of arguments.  Exiting.")
    sys.exit()

FILE_DIR = Scraper.get_file_dir(sys.argv[1])

if not os.path.exists(FILE_DIR + '/checkstyle.xml'):
    print("Could not access " + FILE_DIR + "/checkstyle.xml" + " Exiting.")
    sys.exit()

try:
    checkstyle_xml = xml.dom.minidom.parse(FILE_DIR + '/checkstyle.xml')
except:
    print("Could not access findbugs xml file, but it exists.")
    sys.exit()

# root is the first <> element in the XML file.
root = checkstyle_xml.documentElement

# We're now set up to read XML

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()
# Connection setup

repo_id = sys.argv[2]
commit_hash = sys.argv[3]

commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], commit_hash=commit_hash, repo_id=repo_id)

######################################################################
# Setup complete
######################################################################

######################################################################
# XML Reading/Uploading
######################################################################

# This has been updated to basically ignore the newline nodes.
# We get a list of <file> nodes, then check if they have the correct number of children.  If it's more than one,
# we know there are errors and have to analyze them.

# Unlike China, we are not a one child state.
# I think that joke is a bit dated, technically.
for first in root.getElementsByTagName("file"):
    # Checkstyle generates <file> tags with a single new line if empty, so all classes without checkstyle errors
    # will have exactly one child.  So we skip them.
    if len(first.childNodes) == 1:
        continue

    package = ""
    class_name = ""
    if first.hasAttribute("name"):
        package = first.getAttribute("name")
        class_name = package.split('/')[-1]
        class_name = class_name.split('.')[0]
        package = package.split('/')[-2]

    for node in first.getElementsByTagName("error"):
        # Some errors do not have a column number, so they will be saved as -1
        col = -1

        line = 0
        sev = ""
        mess = ""
        source = ""
        message = ""

        if node.hasAttribute("line"):
            line = int(node.getAttribute("line"))
        if node.hasAttribute("column"):
            col = int(node.getAttribute("column"))
        if node.hasAttribute("severity"):
            sev = node.getAttribute("severity")
        if node.hasAttribute("message"):
            message = node.getAttribute("message")
            message = connection.escape_string(message.replace("\\", "\\\\").replace('\'', '\\\'')[:50])
        if node.hasAttribute("source"):
            source = node.getAttribute("source").split('.')[-1]

        # Gets information ready to be added to DB
        class_uid = Scraper.get_class_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                          db=config_info['db'], class_name=class_name,    package=package)

        search = "SELECT * FROM checkstyle WHERE CommitUID = %s AND ClassUID = %s AND ErrorType = %s AND  Severity = " \
                 "%s AND Line = %s and Col = %s"

        cur.execute(search, (commit_uid, class_uid, source, sev, line, col))

        if cur.rowcount != 0:
            continue

        # Attempts to insert information into database.
        # If it doesn't match, it catches in the except and prints it.
        add_checkstyle = "INSERT INTO checkstyle (CommitUID, ClassUID, ErrorType, Severity, ErrorMessage, Line, " \
                         "Col) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            cur.execute(add_checkstyle, (commit_uid, class_uid, source, sev, message, line, col))
        except:
            connection.rollback()
            error_string = str(sys.exc_info()[0]) + "\n----------\n"
            error_string += str(sys.exc_info()[1]) + "\n----------\n"
            error_string += str(sys.exc_info()[2])

            v_list = "(CommitUID, ClassUID, ErrorType, Severity, ErrorMessage, Line, Col)"
            Scraper.sendFailEmail("Failed to insert into checkstyle table!", "The following insert failed:",
                                  add_checkstyle, v_list, error_string, commit_uid, class_uid, source, sev,
                                  mess, line, col)

# Closing connection
connection.close()
