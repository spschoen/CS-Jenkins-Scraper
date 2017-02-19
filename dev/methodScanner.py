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
    if line == "\n" or "enum" in line: #Ignore enums and blank lines
        continue
    else:
        if "dir" in line: #for example: dir bug_tracker
            currentPacka = line.split(" ")[1].replace("\n","")
            #Split the string on spaces, then take the second value
            #which is the directory/package, then remove the new line

        elif "class" in line or "interface" in line: #for example: public class TrackedBug {
            currentClass = line.replace("\n","").split(" ")
            #Remove new line, split on space.

            #While we haven't hit class/interface, remove previous elements.
            #Since access can be optional (none is accepted), we have to iterate until we hit
            #class/interface.  Once we get it, we delete class/interface and the first element
            #is the class name.
            while currentClass[0] != "class" and currentClass[0] != "interface":
                del currentClass[0]
            del currentClass[0]
            currentClass = currentClass[0]

            #Check the ClassUID table for all records that match the package and class
            cur.execute("SELECT * FROM classUID WHERE Package = %s and class = %s",(currentPacka, currentClass))

            #If we get any records returned, then obviously it's already in the table we don't
            #have to insert.  Otherwise, if there are no returned records, then we need to
            #insert them into the table.
            if cur.rowcount == 0:
                try:
                    cur.execute("INSERT INTO classUID(classUID, Package, Class) VALUES \
                                    (NULL, %s, %s)",(currentPacka, currentClass))
                except e:
                    #debug
                    #print(e[0] + "|" + e[1])
                    connection.rollback()
            else:
                pass
                #debug
                #print("PKG: " + currentPacka.ljust(20) + " | CLS: " + currentClass.ljust(20) + \
                #            " | Already exists in DB.")

        elif "enum" not in line: #for example: public String getNote () {
            #split on the parenthesis, grab the first element. since that's gonna include the
            #method name, and split that on spaces
            part = line.split("(")[0].split(" ")

            #Iterate over the reversed list, for exmaple: ['','getNote','String','public']
            #Ignore the '', since if there's a space between ( and the method name, it'll split
            #into an empty string.  Then, the next item immediately after the blank/parenthesis
            #is the method name!
            for item in reversed(part):
                if item == "":
                    continue
                else:
                    part = item
                    break

            #Ignore new lines, for safety.
            if item == "\n":
                continue

            #If we get any records returned, then obviously it's already in the table we don't
            #have to insert.  Otherwise, if there are no returned records, then we need to
            #insert them into the table.
            cur.execute("SELECT * FROM methodUID WHERE Package = %s and Class = %s and \
                                Method = %s",(currentPacka, currentClass, item))
            if cur.rowcount == 0:
                #debug
                #print("PKG: " + currentPacka.ljust(20) + " | CLS: " + currentClass.ljust(30) + \
                #        " | MTD: " + item.ljust(40) + " | Adding to DB.")
                try:
                    cur.execute("INSERT INTO methodUID(methodUID, Package, Class, Method) VALUES \
                                    (NULL, %s, %s, %s)",(currentPacka, currentClass, item))
                except e:
                    #debug
                    print(e[0] + "|" + e[1])
                    connection.rollback()
            else:
                pass
                #debug
                #print("PKG: " + currentPacka.ljust(20) + " | CLS: " + currentClass.ljust(30) + \
                #        " | MTD: " + item.ljust(40) + " | Already exists in DB.")


methodsFile.close()

print()

# Closing connection
connection.close()
