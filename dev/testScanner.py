import sys
import pymysql.cursors
from git import *
from git.objects.util import *
'''
    testScanner.py is a python file that will read tests.txt
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

methodsFile = open("tests.txt", "r" )
allMethods = list(methodsFile)

currentClass = ""
currentPacka = ""
classUID = -1
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
            cur.execute("SELECT * FROM testClassUID WHERE testPackage = %s and \
                            testClass = %s",(currentPacka, currentClass))

            #If we get any records returned, then obviously it's already in the table we don't
            #have to insert.  Otherwise, if there are no returned records, then we need to
            #insert them into the table.
            if cur.rowcount == 0:
                #debug
                print("    [Data Miner] Detecting new test class to be added to database.  " +  
                            "Adding " + currentClass + " to Database")
                '''print("\nAdding record to DB.         | PKG: " + currentPacka.ljust(20) + \
                        " | CLS: " + currentClass.ljust(30))'''
                try:
                    cur.execute("INSERT INTO testClassUID(testClassUID, testPackage, testClass) \
                                VALUES (NULL, %s, %s)",(currentPacka, currentClass))
                except e:
                    #debug
                    #print(e[0] + "|" + e[1])
                    connection.rollback()
            else:
                pass
                #debug
                '''print("\nRecord already exists in DB. | PKG: " + currentPacka.ljust(20) + \
                        " | CLS: " + currentClass.ljust(20))'''

            #Execute the same select, so we can get the new classUID
            cur.execute("SELECT * FROM testClassUID WHERE testPackage = %s and \
                            testClass = %s",(currentPacka, currentClass))
            if cur.rowcount == 0:
                print("Somehow, we inserted and could not insert a test classUID.  Exiting.")
                sys.exit()
            elif cur.rowcount != 1:
                print("Multiple matches for testclassUID table.  What?")
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
            for test in reversed(part):
                if test == "":
                    continue
                else:
                    break

            #Ignore new lines, for safety.
            if test == "\n":
                continue

            #If we get any records returned, then obviously it's already in the table we don't
            #have to insert.  Otherwise, if there are no returned records, then we need to
            #insert them into the table.
            cur.execute("SELECT * FROM testMethodUID WHERE testClassUID = %d and \
                            testMethodName = '%s'" % (classUID, test))
            if cur.rowcount == 0:
                #debug
                print("    [Data Miner] Detecting new test to be added to database.  Adding " \
                            + test + " to Database")
                '''print("Adding record to DB.         | PKG: " + currentPacka.ljust(20) + " | CLS: " \
                        + currentClass.ljust(30) + " | MTD: " + test.ljust(40))'''
                try:
                    cur.execute("INSERT INTO testMethodUID(testMethodUID, testClassUID, \
                                    testMethodName) VALUES (NULL, %s, %s)", (classUID, test))
                except e:
                    #debug
                    #print(e[0] + "|" + e[1])
                    connection.rollback()
            else:
                pass
                #debug
                '''print("Record already exists in DB. | PKG: " + currentPacka.ljust(20) + " | CLS: " \
                        + currentClass.ljust(30) + " | MTD: " + test.ljust(40))'''


methodsFile.close()

print()

# Closing connection
connection.close()
