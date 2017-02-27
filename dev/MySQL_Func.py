import pymysql
import smtplib
import sys
import traceback
import email.utils
from email.mime.text import MIMEText

def getMethodUID(IP, user, pw, DB, method, className, package):
    """
    getMethodUID will take args to connect to a Database, as well as
    the names of the method, class, and package to be identified.
    It will check the database records for the method UID (and,
    implicity, the class UID) and if it does not exist, it will
    create it, then check for the new method UID.  Finally,
    it will return the newly found method UID.

    @author Samuel Schoeneberger
    @version 1.0

    @param IP        - the address of the Database to connect to
    @param user      - the username to log into the DB.  Probably root.
    @param pw        - the password of the above username.  c'mon man.
    @param DB        - the specific database to connect to in MySQL.
    @param method    - the method to look up in the DB.
    @param className - the class to look up in the DB.
    @param package   - the package to look up in the DB.

    @return methodUID, the UID of the method in the methodUID table.
    """
    #Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error)
        sys.exit()

    cur = connection.cursor()

    #print("Searching for methodUID")
    classUID = getClassUID(IP=IP, user=user, pw=pw, DB=DB, className=className, package=package)

    select = "SELECT * FROM methodUID WHERE ClassUID = %s AND Method = %s"
    cur.execute(select, (classUID, method))

    #print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        try:
            insert = "INSERT INTO methodUID(methodUID, classUID, Method) VALUES (Null, %s, %s)"
            cur.execute(insert, (classUID, method))
        except e:
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            fromMail = "spschoen.alerts@gmail.com"
            to = "spschoen.alerts@gmail.com"
            subject = "Failure to insert into methodUID!"
            body = "The following insert statement failed:\n\n"
            body += "%s\n\n".format(insert)
            body += "With the following variables (package | class):\n\n"
            body += "%s | %s".format(classUID, method)
            body += "The following error message was produced:\n\n%s".format(ErrorString)

            email_text = """\
            From: %s,
            To: %s,
            Subject: %s

            %s
            """, (fromMail, ", ".join(to), subject, body)
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                # TODO: SECURE THE PASSWORD BUT FOR NOW YOU HAVE TO EDIT IT IN.
                server.login("spschoen.alerts@gmail.com", "PASSWORD")
                server.sendmail(fromMail, to, email_text)
                server.close()
            except:
                print("Couldn't even send an email, wot")
                for error in sys.exc_info():
                    print(error)

    cur.execute(select, (package, className))
    methodUID = str(cur.fetchone()[0])

    connection.close()
    return methodUID

def getClassUID(IP, user, pw, DB, className, package):
    """
    getClassUID will take args to connect to a Database, as well as
    the names of the class and package to be identified.
    It will check the database records for the class UID and if it
    does not exist, it will create it, then check for the new
    class UID.  Finally, it will return the newly found class UID.

    @author Samuel Schoeneberger
    @version 1.0

    @param IP        - the address of the Database to connect to
    @param user      - the username to log into the DB.  Probably root.
    @param pw        - the password of the above username.  c'mon man.
    @param DB        - the specific database to connect to in MySQL.
    @param className - the class to look up in the DB.
    @param package   - the package to look up in the DB.

    @return classUID, the UID of the class in the classUID table.
    """
    #Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error)
        sys.exit()

    cur = connection.cursor()
    cur.execute("DELETE from classUID where Package=%s and Class=%s", ("String", "lang"))

    #print("Searching for classUID")

    select = "SELECT * FROM classUID WHERE Package = %s AND Class = %s"
    cur.execute(select, (package, className))

    #print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        try:
            insert = "INSERT INTO classUID(classUID, Package, Class) VALUES (Null, %s, %s)"
            cur.execute(insert, (package, className))
        except e:
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            fromMail = "spschoen.alerts@gmail.com"
            to = "spschoen.alerts@gmail.com"
            subject = "Failure to insert into classUID!"
            body = "The following insert statement failed:\n\n"
            body += "%s\n\n".format(insert)
            body += "With the following variables (package | class):\n\n"
            body += "%s | %s".format(package, className)
            body += "The following error message was produced:\n\n%s".format(ErrorString)

            email_text = """\
            From: %s,
            To: %s,
            Subject: %s

            %s
            """, (fromMail, ", ".join(to), subject, body)
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                # TODO: SECURE THE PASSWORD BUT FOR NOW YOU HAVE TO EDIT IT IN.
                server.login("spschoen.alerts@gmail.com", "PASSWORD")
                server.sendmail(fromMail, to, email_text)
                server.close()
            except:
                print("Couldn't even send an email, wot")
                for error in sys.exc_info():
                    print(error)

    cur.execute(select, (package, className))
    classUID = str(cur.fetchone()[0])

    connection.close()
    return classUID

def getCommitUID(IP, user, pw, DB, hash, repoID):
    """
    getCommitUID will take args to connect to a Database, as well as
    the Project ID and commit Hash, to get the correct commitUID.
    Will create a commitUID if it doesn't exist.

    @author Samuel Schoeneberger
    @version 1.0

    @param IP     - the address of the Database to connect to
    @param user   - the username to log into the DB.  Probably root.
    @param pw     - the password of the above username.  c'mon man.
    @param DB     - the specific database to connect to in MySQL.
    @param hash   - the commit hash of a git commit. 40 hex chars
    @param repoID - the repo to look up in the commitUID table.  PW-XYZ

    @return methodUID, the UID of the method in the methodUID table.
    """
    #Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error)
        sys.exit()
    cur = connection.cursor()

    CUID = -1
    commitUIDSelect = "SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s"
    cur.execute(commitUIDSelect, (hash, repoID) )
    if cur.rowcount == 0: #UID doesn't exist
        try:
            cur.execute("INSERT INTO commitUID(commitUID, Hexsha, Repo) VALUES \
                            (NULL, %s, %s)", (hash, repoID) )
            cur.execute(commitUIDSelect, (hash, repoID) )
            CUID = str(cur.fetchone()[0])
        except e:
            print(e[0] + "|" + e[1])
            connection.rollback()
    else:
        CUID = str(cur.fetchone()[0]) #Get the actual UID since it exists

    connection.close()
    return CUID
