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
     - 3. GIT_COMMIT : [40 char commit hash]

@author Renata Ann Zeitler
"""

import xml.dom.minidom
import sys
import os
import pymysql
import Scraper

# Setting up the XML to read
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))
    # print(FILE_DIR)

try:
    pmd = xml.dom.minidom.parse(FILE_DIR + '/pmd.xml')
except:
    sys.exit()
    # This is commented out, because pmd XML can be not created for a lot of reasons.
    # TODO: Make ant only run the Data Miner if compilation succeeds.
    '''ErrorString = sys.exc_info()[0] + "\n----------\n"
    ErrorString += sys.exc_info()[1] + "\n----------\n"
    ErrorString += sys.exc_info()[2]
    Scraper.sendFailEmail("Failed to read pmd.xml", "The following command failed:",
                                "pmd = xml.dom.minidom.parse(FILE_DIR + '/pmd.xml')",
                                "With the following variables (FILE_DIR)",
                                ErrorString, FILE_DIR)'''

# Getting commitUID info
repo_id = sys.argv[2]
hash = sys.argv[3]

# root is the first <> element in the XML file.
root = pmd.documentElement

# Set up to read XML

# Setting up the DB connection
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

# CommitUID getting
CUID = Scraper.getCommitUID(
    IP=IP, user=user, pw=pw, DB=DB, hash=hash, repo_id=repo_id)

package = ""
className = ""
method = ""
line = 0
rule = ""
ruleset = ""

# A basic for loop, to look at all the nodes (<> elements) inside the file node
#(which is now the root node) and print out their information to the DB.
#.childNodes is a list of nodes that the root has as children.
for file in root.childNodes:
    if file.nodeType != file.TEXT_NODE:
        for node in file.childNodes:
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
        #print("Could not find an attribute.  Rerun with print debugging.")
        continue

    # Class UID
    methodUID = Scraper.get_method_UID(IP=IP, user=user, pw=pw, DB=DB, className=className,
                                        package=package, method=method)

    search = "SELECT * FROM PMD WHERE CommitUID = %s AND MethodUID = %s AND Ruleset = %s AND "
    search += "Rule = %s AND Line = %s"
    cur.execute(search, (str(CUID), str(methodUID),
                         str(ruleset), str(rule), str(line)))
    if cur.rowcount != 0:
        continue

    # PMD time!
    insertPMD = "INSERT INTO PMD(CommitUID, MethodUID, Ruleset, Rule, Line) "
    insertPMD += "VALUES ( %s, %s, %s, %s, %s )"

    try:
        cur.execute(insertPMD, (str(CUID), str(methodUID),
                                str(ruleset), str(rule), str(line)))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]

        v_list = "(CommitUID, MethodUID, Ruleset, Rule, Line)"
        Scraper.sendFailEmail("Failed to insert into PMD table!",
                                 "The following insert failed:",
                                 insertPMD,
                                 v_list,
                                 ErrorString,
                                 str(CUID), str(methodUID), str(ruleset), str(rule), str(line))

# Closing connection
connection.close()
