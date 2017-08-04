"""
Interpreter for methodScan.sh output file.  Uploads all methods to database, giving them unique identifiers used
throughout these scraper programs.

Requirements:
    Scraper.py  - library for interaction with databases must be available in the same directory as this file.
    config.json - file specifying database information.
    methods.txt - output from methodScan.sh script.

Args:
    N/A

Returns:
    N/A

Authors:
    Renata Ann Zeitler
    Samuel Schoeneberger
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
    methodsFile = open("methods.txt", "r")
except:
    for error in sys.exc_info():
        print(error + "")
    sys.exit()

allMethods = list(methodsFile)

class_name = ""
package = ""
classUID = -1
for line in allMethods:
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" or "enum" in line:
        continue

    if "dir" in line:
        # for example: dir bug_tracker
        package = line.split(" ")[1].replace("\n", "")
        # Split the string on spaces, then take the second value
        # which is the directory/package, then remove the new line

    elif "class" in line:
        # for example: public class TrackedBug {
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

        # Check the ClassUID table for all records that match the package and class
        Scraper.get_class_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                              db=config_info['db'], class_name=class_name, package=package)

    elif "enum" not in line:
        # for example: public String getNote () {
        # split on the parenthesis, grab the first element. since that's gonna include the
        # method name, and split that on spaces
        part = line.split("(")[0].split(" ")

        # Iterate over the reversed list, for example: ['','getNote','String','public']
        # Ignore the '', since if there's a space between ( and the method name, it'll split
        # into an empty string.  Then, the next item immediately after the blank/parenthesis
        # is the method name!
        for item in reversed(part):
            if item == "":
                continue
            else:
                method_name = item
                break

        # Ignore new lines, for safety.
        if method_name == "\n":
            continue

        # We're discarding the return value from the function since it does the inserting
        # as well as returning.
        methodUID = Scraper.get_method_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                           db=config_info['db'], package=package, class_name=class_name,
                                           method=method_name)


methodsFile.close()

# Closing connection
connection.close()
