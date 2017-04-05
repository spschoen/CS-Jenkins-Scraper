"""
methodScanner.py is a python file that will read methods.txt for all methods and classes in a
student's directory, then upload the unique ones.

Requirements:
 - methods.txt must exist.  If not, this script won't read it.
 - MySQL_Func.py for interacting with MySQL.
 - config.txt to read in variables for IP, DB, etc.

Execution:
 - python3 methodScanner.py
   - Arguments:
     - 0. methodScanner.py

@author Samuel Schoeneberger
"""

import sys
import pymysql
import MySQL_Func
import os

# Setting up the DB connection
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
    methodsFile = open("methods.txt", "r")
except:
    for error in sys.exc_info():
        print(error + "")
    sys.exit()
allMethods = list(methodsFile)

className = ""
package = ""
classUID = -1
for line in allMethods:
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" or "enum" in line:  # Ignore enums and blank lines
        continue
    else:
        if "dir" in line:  # for example: dir bug_tracker
            package = line.split(" ")[1].replace("\n", "")
            # Split the string on spaces, then take the second value
            # which is the directory/package, then remove the new line

        elif "class" in line:  # for example: public class TrackedBug {
            className = line.replace("\n", "").split(" ")
            # Remove new line, split on space.

            # While we haven't hit class/interface, remove previous elements.
            # Since access can be optional (none is accepted), we have to iterate until we hit
            # class/interface.  Once we get it, we delete class/interface and the first element
            # is the class name.
            while className[0] != "class" and className[0] != "interface":
                del className[0]
            del className[0]
            className = className[0]

            # Check the ClassUID table for all records that match the package
            # and class
            classUID = MySQL_Func.getClassUID(IP=IP, user=user, pw=pw, DB=DB,
                                              className=className, package=package)

        elif "enum" not in line:  # for example: public String getNote () {
            # split on the parenthesis, grab the first element. since that's gonna include the
            # method name, and split that on spaces
            part = line.split("(")[0].split(" ")

            # Iterate over the reversed list, for exmaple: ['','getNote','String','public']
            # Ignore the '', since if there's a space between ( and the method name, it'll split
            # into an empty string.  Then, the next item immediately after the blank/parenthesis
            # is the method name!
            for item in reversed(part):
                if item == "":
                    continue
                else:
                    methodName = item
                    break

            # Ignore new lines, for safety.
            if methodName == "\n":
                continue

            # olol this was like 30 lines now it's 3.
            # We're discarding the return value from the function since it does the inserting
            # as well as returning.
            methodUID = MySQL_Func.get_method_UID(IP=IP, user=user, pw=pw, DB=DB,
                                                    className=className, package=package,
                                                    method=methodName)


methodsFile.close()

# Closing connection
connection.close()
