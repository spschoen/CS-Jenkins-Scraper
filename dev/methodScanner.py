import sys
#import pymysql.cursors
from git import *
from git.objects.util import *
'''
    methodScanner.py is a python file that will read methods.txt
    for all methods and classes in a student's directory,
    then upload the unique ones.
'''

# Setting up the DB connection
# Future people: change this to your master IP
# Or wherever your DB is.
#connection = pymysql.connect(host="152.46.20.243")
#cur = cnx.cursor()
# Connection setup

methodsFile = open("methods.txt", "r" )

allMethods = list(methodsFile)

currentClass = ""

#Current problem to be solved: if there's a space between methodName and (, then it dies.
for line in allMethods:
    if line == "\n":
        print("")
    else:
        if "class" in line:
            print(line, end="")
        elif "enum" in line:
            print()
        else:
            print(line, end="")
            for part in line.split(" "):
                if "(" in part:
                    print(part.split("(")[0])

methodsFile.close()

# Closing connection
#cnx.close()
