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

newClass = ""
Pacakge = ""
classUID = -1
for line in allMethods:
    # New lines are added by the scanner, don't need 'em.
    if line == "\n" or "enum" in line: #Ignore enums and blank lines
        continue
    else:
        if "dir" in line: #for example: dir bug_tracker
            Pacakge = line.split(" ")[1].replace("\n","")
            #Split the string on spaces, then take the second value
            #which is the directory/package, then remove the new line

        elif "class" in line or "interface" in line: #for example: public class TrackedBug {
            newClass = line.replace("\n","").split(" ")
            #Remove new line, split on space.

            #While we haven't hit class/interface, remove previous elements.
            #Since access can be optional (none is accepted), we have to iterate until we hit
            #class/interface.  Once we get it, we delete class/interface and the first element
            #is the class name.
            while newClass[0] != "class" and newClass[0] != "interface":
                del newClass[0]
            del newClass[0]
            newClass = newClass[0]

            #Check the ClassUID table for all records that match the package and class
            cur.execute("SELECT * FROM classUID WHERE Package = %s and class = %s",(Pacakge, newClass))

            #If we get any records returned, then obviously it's already in the table we don't
            #have to insert.  Otherwise, if there are no returned records, then we need to
            #insert them into the table.
            if cur.rowcount == 0:
                '''print("    [Data Miner] Detecting new Class to be added to database.  Adding " \
                            + newClass + " to Database")'''
                try:
                    cur.execute("INSERT INTO classUID(classUID, Package, Class) VALUES \
                                    (NULL, %s, %s)", (Pacakge, newClass))
                except e:
                    #debug
                    #print(e[0] + "|" + e[1])
                    # TODO: email when failure happens.
                    connection.rollback()
            else:
                pass
                #debug
                '''print("PKG: " + Pacakge.ljust(20) + " | CLS: " + newClass.ljust(20) + \
                            " | Already exists in DB.")'''

            #Execute the same select, so we can get the new classUID
            cur.execute("SELECT * FROM classUID WHERE Package = %s and Class = %s", \
                            (Pacakge, newClass))

            #Checking again, looking to make sure that we uploaded.
            if cur.rowcount == 0:
                print("Somehow, we inserted and could not insert a classUID.  Exiting.")
                # TODO: email when failure happens.
                sys.exit()
            elif cur.rowcount != 1:
                print("Multiple matches for classUID table.  What?")
                # TODO: email when failure happens.
                sys.exit()
            else:
                #Now we can actually get the number.
                classUID = int(cur.fetchone()[0])

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
                    methodName = item
                    break

            #Ignore new lines, for safety.
            if methodName == "\n":
                continue

            #If we get any records returned, then obviously it's already in the table we don't
            #have to insert.  Otherwise, if there are no returned records, then we need to
            #insert them into the table.
            cur.execute("SELECT * FROM methodUID WHERE ClassUID = %s and Method = %s", \
                            (classUID, methodName))
            if cur.rowcount == 0:
                #debug
                '''print("    [Data Miner] Detecting new method to be added to database.  Adding " \
                            + methodName + " to Database")'''
                '''print("PKG: " + Pacakge.ljust(20) + " | CLS: " + newClass.ljust(30) + \
                        " | MTD: " + methodName.ljust(40) + " | Adding to DB.")'''
                try:
                    cur.execute("INSERT INTO methodUID(methodUID, ClassUID, Method) VALUES \
                                    (NULL, %s, %s)",(classUID, methodName))
                except e:
                    #debug
                    #print(e[0] + "|" + e[1])
                    # TODO: email when failure happens.
                    connection.rollback()
            else:
                pass
                #debug
                #print("PKG: " + Pacakge.ljust(20) + " | CLS: " + newClass.ljust(30) + \
                #        " | MTD: " + methodName.ljust(40) + " | Already exists in DB.")


methodsFile.close()

# Closing connection
connection.close()
