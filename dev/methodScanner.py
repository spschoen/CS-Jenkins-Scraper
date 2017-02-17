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
        continue;
    else:
        if "class" in line:
            print("\n" + line.replace("\n",""))
            currentClass = line.replace("\n","")
        elif "enum" in line:
            print()
        else:
            #print(line.replace("\n",""))
            part = line.split("(")[0].split(" ")
            for item in reversed(part):
                if item == "":
                    continue
                else:
                    print(item)
                    break

methodsFile.close()

print()

# Closing connection
#cnx.close()
