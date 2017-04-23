"""
methodScanner.py is a python file that will read tests.txt for all methods and classes in a
student's directory, then upload the unique ones.

Requirements:
 - tests.txt must exist.  If not, this script won't read it.
 - Scraper.py for interacting with MySQL.
 - config.txt to read in variables for IP, DB, etc.

Execution:
 - python3 testScanner.py
   - Arguments:
     - 0. testScanner.py

@author Samuel Schoeneberger
"""

import sys
import pymysql
import Scraper
import os

# Setting up the DB connection
# Future people: change this to your master IP
# Or wherever your DB is.
# Now, we begin reading the config file.
if not os.path.exists('config.txt'):
    # config.txt doesn't exist.  Don't run.
    # print("Could not access config.txt, exiting.")
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
# Connection setup

try:
    testsFile = open("tests.txt", "r")
except:
    for error in sys.exc_info():
        print(error + "")
    sys.exit()
allMethods = list(testsFile)

newClass = ""
Package = ""
classUID = -1
for line in allMethods:
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" or "enum" in line:  # Ignore enums and blank lines
        continue
    else:
        if "dir" in line:  # for example: dir bug_tracker
            Package = line.split(" ")[1].replace("\n", "")
            # Split the string on spaces, then take the second value
            # which is the directory/package, then remove the new line

        elif "class" in line:  # for example: public class TrackedBug {
            newClass = line.replace("\n", "").split(" ")
            # Remove new line, split on space.

            # While we haven't hit class/interface, remove previous elements.
            # Since access can be optional (none is accepted), we have to iterate until we hit
            # class/interface.  Once we get it, we delete class/interface and the first element
            # is the class name.
            while newClass[0] != "class" and newClass[0] != "interface":
                del newClass[0]
            del newClass[0]
            newClass = newClass[0]

            # Check the ClassUID table for all records that match the package
            # and class
            testClassUID = testClassUID = Scraper.getTestClassUID(IP=IP, user=user, pw=pw,
                                                                     DB=DB, package=Package,
                                                                     className=newClass)

        elif "enum" not in line:  # for example: public String getNote () {

            # split on the parenthesis, grab the first element. since that's gonna include the
            # method name, and split that on spaces
            part = line.split("(")[0].split(" ")

            # Iterate over the reversed list, for exmaple: ['','getNote','String','public']
            # Ignore the '', since if there's a space between ( and the method name, it'll split
            # into an empty string.  Then, the next item immediately after the blank/parenthesis
            # is the method name!
            for test in reversed(part):
                if test == "":
                    continue
                else:
                    break

            # Ignore new lines, for safety.
            if test == "\n":
                continue

            # If we get any records returned, then obviously it's already in the table we don't
            # have to insert.  Otherwise, if there are no returned records, then we need to
            # insert them into the table.
            Scraper.getTestMethodUID(IP=IP, user=user, pw=pw, DB=DB, className=newClass,
                                        package=Package, method=test)


testsFile.close()

# Closing connection
connection.close()
