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
    connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    cur = connection.cursor()

    print("Searching for methodUID")

    classUID = getClassUID(IP, user, pw, DB, className, package)

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

    print("Searching for classUID")

    select = "SELECT * FROM classUID WHERE Package = %s AND Class = %s"
    cur.execute(select, (package, className))

    print("Selected " + str(cur.rowcount) + " elements.")

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
    else:
        try:
            insert = "INSERT INTO classUID(classUID, Package, Class) VALUES (Null, %s, %s)"
        except:
            ErrorString = str(sys.exc_info()[0]) + "\n----------\n"
            ErrorString += str(sys.exc_info()[1]) + "\n----------\n"
            ErrorString += str(sys.exc_info()[2])

            msg = MIMEText("The following insert statement failed:\n\n"
                            + insert
                            + "\n\nWith the following variables (package | class):\n\n"
                            + package + " | " + className
                            + "\n\nThe following error message was produced:"
                            + "\n\n" + traceback.format_exc())

            msg["To"] = email.utils.formataddr(("Administrator", "spschoen.alerts@gmail.com"))
            msg["From"] = email.utils.formataddr(("Alert System", "spschoen.alerts@gmail.com"))
            msg["Subject"] = "Failure to insert into classUID!"

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            # TODO: SECURE THE PASSWORD BUT FOR NOW YOU HAVE TO EDIT IT IN.
            server.login("spschoen.alerts@gmail.com", "PASSWORD")
            server.set_debuglevel(True) # show communication with the server
            try:
                server.sendmail("spschoen.alerts@gmail.com", ["spschoen.alerts@gmail.com"], \
                                    msg.as_string())
            finally:
                server.quit()



    select = "SELECT * FROM classUID WHERE Package = %s AND Class = %s"
    classUID = int(cur.fetchone()[0])

    connection.close()
    return classUID

def getCommitUID(IP, user, pw, DB, hash, repoID):
    connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    cur = connection.cursor()

    CUID = -1
    commitUIDSelect = "SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s"
    cur.execute(commitUIDSelect, (hash, repoID) )
    if cur.rowcount == 0: #UID doesn't exist
        try:
            cur.execute("INSERT INTO commitUID(commitUID, Hexsha, Repo) VALUES \
                            (NULL, %s, %s)", (hash, repoID) )
            cur.execute(commitUIDSelect, (hash, repoID) )
            CUID = cur.fetchone()[0]
        except e:
            print(e[0] + "|" + e[1])
            connection.rollback()
    else:
        CUID = cur.fetchone()[0] #Get the actual UID since it exists

    if CUID == -1:
        print("Could not get CUID")
        sys.exit()

    connection.close()
    return CUID
