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
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" and "enum" in line:
        continue
    else:
        if "class" in line:
            #print("\n" + line.replace("\n",""))
            print()
            currentClass = line.replace("\n","").split(" ")
            while currentClass[0] != "class":
                del currentClass[0]
            del currentClass[0]
            currentClass = currentClass[0]
        elif "enum" not in line:
            part = line.split("(")[0].split(" ")
            for item in reversed(part):
                if item == "":
                    continue
                else:
                    part = item
                    break
            if item == "\n":
                continue
            print(currentClass + ": " + item)

methodsFile.close()

print()

# Closing connection
#cnx.close()
