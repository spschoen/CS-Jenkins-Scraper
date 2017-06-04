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

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()
# Connection setup

try:
    testsFile = open("tests.txt", "r")
except:
    for error in sys.exc_info():
        print(error + "")
    sys.exit()
allMethods = list(testsFile)

class_name = ""
Package = ""
classUID = -1
for line in allMethods:
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" or "enum" in line:  # Ignore enums and blank lines
        continue

    if "dir" in line:  # for example: dir bug_tracker
        package = line.split(" ")[1].replace("\n", "")
        # Split the string on spaces, then take the second value
        # which is the directory/package, then remove the new line

    elif "class" in line:  # for example: public class TrackedBug {
        class_name = line.replace("\n", "").split(" ")
        # Remove new line, split on space.

        # While we haven't hit class/interface, remove previous elements.
        # Since access can be optional (none is accepted), we have to iterate until we hit
        # class/interface.  Once we get it, we delete class/interface and the first element
        # is the class name.
        while class_name[0] != "class" and class_name[0] != "interface":
            del class_name[0]
        del class_name[0]
        class_name = class_name[0]

        # Check the ClassUID table for all records that match the package
        # and class
        test_class_uid = Scraper.get_test_class_uid(ip=config_info['ip'], user=config_info['user'],
                                                    pw=config_info['pass'], db=config_info['db'],
                                                    class_name=class_name, package=package)

    elif "enum" not in line:  # for example: public String getNote () {

        # split on the parenthesis, grab the first element. since that's gonna include the
        # method name, and split that on spaces
        part = line.split("(")[0].split(" ")

        # Iterate over the reversed list, for example: ['','getNote','String','public']
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
        Scraper.get_test_method_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], method=test, class_name=class_name,  package=package)


testsFile.close()

# Closing connection
connection.close()
