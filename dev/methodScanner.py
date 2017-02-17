import sys
import pymysql.cursors
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
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = connection.cursor()
# Connection setup

methodsFile = open("methods.txt", "r" )
allMethods = list(methodsFile)

currentClass = ""
currentPacka = ""
for line in allMethods:
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" and "enum" in line:
        continue
    else:
        if "dir" in line:
            currentPacka = line.split(" ")[1].replace("\n","")
        elif "class" in line or "interface" in line:
            #print("\n" + line.replace("\n",""))
            print()
            currentClass = line.replace("\n","").split(" ")
            while currentClass[0] != "class" and currentClass[0] != "interface":
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
            print(currentPacka + ": " + currentClass + ": " + item)
            cur.execute("SELECT * FROM classUID WHERE Package = %s and class = %s",(currentPacka, currentClass))
            if cur.rowcount == 0:
                try:
                    cur.execute("INSERT INTO classUID(classUID, Package, Class) VALUES (NULL, %s, %s)",(currentPacka, currentClass))
                except e:
                    print(e[0] + "|" + e[1])
                    connection.rollback()
                    print("rip")
                    sys.exit()


methodsFile.close()

print()

# Closing connection
connection.close()
