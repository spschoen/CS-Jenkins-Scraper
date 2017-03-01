import sys
import pymysql
import MySQL_Func

'''
    methodScanner.py is a python file that will read methods.txt
    for all methods and classes in a student's directory,
    then upload the unique ones.
'''

# Setting up the DB connection
# Future people: change this to your master IP
# Or wherever your DB is.
# TODO: CHANGE THESE IN PRODUCTION
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()
# Connection setup
try:
    methodsFile = open("methods.txt", "r" )
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
    if line == "\n" or "enum" in line: #Ignore enums and blank lines
        continue
    else:
        if "dir" in line: #for example: dir bug_tracker
            package = line.split(" ")[1].replace("\n","")
            #Split the string on spaces, then take the second value
            #which is the directory/package, then remove the new line

        elif "class" in line: #for example: public class TrackedBug {
            className = line.replace("\n","").split(" ")
            #Remove new line, split on space.

            #While we haven't hit class/interface, remove previous elements.
            #Since access can be optional (none is accepted), we have to iterate until we hit
            #class/interface.  Once we get it, we delete class/interface and the first element
            #is the class name.
            while className[0] != "class" and className[0] != "interface":
                del className[0]
            del className[0]
            className = className[0]

            #Check the ClassUID table for all records that match the package and class
            classUID = MySQL_Func.getClassUID(IP=IP, user=user, pw=pw, DB=DB,
                                                className=className, package=package)
            print(classUID, className, package)

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

            #olol this was like 30 lines now it's 3.
            # We're discarding the return value from the function since it does the inserting
            # as well as returning.
            methodUID = MySQL_Func.getMethodUID(IP=IP, user=user, pw=pw, DB=DB,
                                    className=className, package=package,
                                    method=methodName)
            print(methodUID, classUID, methodName)


methodsFile.close()

cur.execute("SELECT * FROM classUID")
for line in cur.fetchall():
    print(line)

if cur.rowcount == 0:
    print("lol")

# Closing connection
connection.close()
