import pymysql
import smtplib
import sys
import traceback
import email.utils
from email.mime.text import MIMEText


def get_method_UID(IP, user, pw, DB, method, className, package):
    """
    get_method_UID will take args to connect to a Database, as well as the names of the method, class, and
    package to be identified.  It will check the database records for the method UID (and, implicity, the class UID)
    and if it does not exist, it will create it, then check for the new method UID.
    Finally, it will return the newly found method UID.

    Args:
        IP        - The IP address that the database is located.
        user      - Username used to log into the database.  Should have read/write access.
        pw        - password for the user to log in with.
        DB        - Database to manipulate.
        method    - Name of method to lookup/insert into the DB
        className - Name of the class that the above method is in.
        package   - Name of the package that the above class is in.

    Returns:
        Unique ID number of the method in the MethodUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error + "")
        sys.exit()

    cur = connection.cursor()

    # print("Searching for methodUID")
    classUID = getClassUID(IP=IP, user=user, pw=pw, DB=DB,
                           className=className, package=package)

    select = "SELECT * FROM methodUID WHERE ClassUID = %s AND Method = %s"
    cur.execute(select, (classUID, method))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        try:
            insert = "INSERT INTO methodUID(methodUID, classUID, Method) VALUES (Null, %s, %s)"
            cur.execute(insert, (classUID, method))
        except e:
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            sendFailEmail("Failure to insert into methodUID!", "The following insert statement failed: ",
                          insert,
                          "The variables were: ", ErrorString, package, className)

    cur.execute(select, (classUID, method))
    methodUID = str(cur.fetchone()[0])

    connection.close()
    return methodUID


def getClassUID(IP, user, pw, DB, className, package):
    """
    getClassUID will take args to connect to a Database, as well as the names of the class and package to be
    identified.  It will check the database records for the class UID and if it does not exist, it will create it,
    then check for the new class UID.  Finally, it will return the newly found class UID.

    Args:
        IP        - The IP address that the database is located.
        user      - Username used to log into the database.  Should have read/write access.
        pw        - password for the user to log in with.
        DB        - Database to manipulate.
        className - Name of the class to lookup/add to DB.
        package   - Name of the package that the above class is in.

    Returns:
        Unique ID number of the class in the ClassUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error + "")
        sys.exit()

    cur = connection.cursor()

    # print("Searching for classUID")
    select = "SELECT * FROM classUID WHERE Package = %s AND Class = %s"
    cur.execute(select, (package, className))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        try:
            insert = "INSERT INTO classUID(classUID, Package, Class) VALUES (Null, %s, %s)"
            cur.execute(insert, (package, className))
        except e:
            connection.rollback()
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            sendFailEmail("Failure to insert into classUID!",
                          "The following insert statement failed: ",
                          insert,
                          "The variables were: ",
                          ErrorString,
                          package,
                          className)

    cur.execute(select, (package, className))
    classUID = str(cur.fetchone()[0])

    connection.close()
    return classUID


def getTestMethodUID(IP, user, pw, DB, method, className, package):
    """
    getTestMethodUID will take args to connect to a Database, as well as the names of the tes method, class, and
    package to be identified.  It will check the database records for the test method UID
    (and, implicity, the class UID) and if it does not exist, it will create it, then check for the new test method
    UID.  Finally, it will return the newly found method UID.

    Args:
        IP        - The IP address that the database is located.
        user      - Username used to log into the database.  Should have read/write access.
        pw        - password for the user to log in with.
        DB        - Database to manipulate.
        method    - Name of method to lookup/insert into the DB
        className - Name of the class that the above method is in.
        package   - Name of the package that the above class is in.

    Returns:
        Unique ID number of the method in the TestMethodUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error + "")
        sys.exit()

    cur = connection.cursor()

    # print("Searching for testMethodUID")
    testClassUID = getTestClassUID(IP=IP, user=user, pw=pw, DB=DB,
                           className=className, package=package)

    select = "SELECT * FROM testMethodUID WHERE testClassUID = %s AND testMethodName = %s"
    cur.execute(select, (testClassUID, method))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        try:
            insert = "INSERT INTO testMethodUID(testMethodUID, testClassUID, testMethodName) "
            insert += "VALUES (Null, %s, %s)"
            cur.execute(insert, (testClassUID, method))
        except e:
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            sendFailEmail("Failure to insert into testMethodUID!",
                          "The following insert statement failed: ",
                          insert,
                          "The variables were: ",
                          ErrorString,
                          method,
                          package,
                          className)

    cur.execute(select, (testClassUID, method))
    testMethodUID = str(cur.fetchone()[0])

    connection.close()
    return testMethodUID


def getTestClassUID(IP, user, pw, DB, className, package):
    """
    getClassUID will take args to connect to a Database, as well as the names of the test class and package to be
    identified.  It will check the database records for the test class UID and if it does not exist, it will create it,
    then check for the new test class UID.  Finally, it will return the newly found test class UID.

    Args:
        IP        - The IP address that the database is located.
        user      - Username used to log into the database.  Should have read/write access.
        pw        - password for the user to log in with.
        DB        - Database to manipulate.
        className - Name of the class to lookup/add to DB.
        package   - Name of the package that the above class is in.

    Returns:
        Unique ID number of the class in the TestClassUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error + "")
        sys.exit()

    cur = connection.cursor()

    # print("Searching for testClassUID")
    select = "SELECT * FROM testClassUID WHERE testPackage = %s AND testClass = %s"
    cur.execute(select, (package, className))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        try:
            insert = "INSERT INTO testClassUID(testClassUID, testPackage, testClass) VALUES "
            insert += "(Null, %s, %s)"
            cur.execute(insert, (package, className))
        except e:
            connection.rollback()
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            sendFailEmail("Failure to insert into testClassUID!",
                          "The following insert statement failed: ",
                          insert,
                          "The variables were: ",
                          ErrorString,
                          package,
                          className)

    cur.execute(select, (package, className))
    testClassUID = str(cur.fetchone()[0])

    connection.close()
    return testClassUID


def getCommitUID(IP, user, pw, DB, hash, repoID):
    """
    getCommitUID will take args to connect to a Database, as well as the Project ID and commit commit_hash,
    to get the correct commitUID.  Will create a commitUID if it doesn't exist.

    Args:
        IP     - The IP address that the database is located.
        user   - Username used to log into the database.  Should have read/write access.
        pw     - password for the user to log in with.
        DB     - Database to manipulate.
        hash   - the commit hash of a git commit. 40 hex chars
        repoID - the repo to look up in the commitUID table.  cscABC-DEF-PG-XYZ

    Returns:
        Unique ID number of the commit, across all commits.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to DB
    try:
        connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
    except:
        for error in sys.exc_info():
            print(error + "")
        sys.exit()
    cur = connection.cursor()

    CUID = -1
    commitUIDSelect = "SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s"
    cur.execute(commitUIDSelect, (hash, repoID))
    if cur.rowcount == 0:  # UID doesn't exist
        try:
            insert = "INSERT INTO commitUID(commitUID, Hexsha, Repo) VALUES (NULL, %s, %s)"
            cur.execute(insert, (hash, repoID))
            cur.execute(commitUIDSelect, (hash, repoID))
            CUID = str(cur.fetchone()[0])
        except e:
            ErrorString = e[0] + "\n----------\n"
            ErrorString += e[1] + "\n----------\n"
            ErrorString += e[2]
            sendFailEmail("Failure to insert commitUID!",
                          "The following insert failed: ",
                          insert,
                          "The variables were: ",
                          ErrorString,
                          hash,
                          repoID)
            connection.rollback()
    else:
        CUID = str(cur.fetchone()[0])  # Get the actual UID since it exists

    connection.close()
    return CUID


def sendFailEmail(subject, failure_message, command, variable_list, trace, *variables):
    """
    Emails information provided to alert system.
    
    You HAVE to create your own GMAIL/NCSU Email account and set up its information here.  One is not provided.

    Args:
        Subject         - The subject of the email to send
                          "Failure to [do a thing]"
        failure_message - The first line of the email.
                          "The following [command] failed:"
        command         - The command that failed to insert.
                          "INSERT INTO ..."
        variable_list   - The line containing the descriptions of the variables.
                          "With the following variables ([variable 1] | [variable 2] | ...):"
        trace           - The trace, should be created by concatenating the traceback.
        variables       - The list of variables that are related to the variable list.

    Returns:
        N/A

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # TODO: Change this to wherever the fail mail is sent from.
    fromMail = "spschoen.alerts@gmail.com"

    # TODO: Change this to whoever receives the fail mail.
    to = "spschoen.alerts@gmail.com"

    body = failure_message + "\n\n" + command + "\n\n"
    body += str(variable_list) + "\n\n"
    body += str(list(variables)) + "\n\n"
    body += "The following error message was produced:\n\n" + str(trace)

    email_text = """\
    From: %s,
    To: %s,
    Subject: %s

    %s
    """, (fromMail, ", ".join(to), subject, body)

    email_text = "From: " + fromMail + ",\n"
    email_text += "To: " + to + ",\n"
    email_text += "Subject: " + subject + "\n\n"
    email_text += body

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        # TODO: YOU HAVE TO EDIT THE PASSWORD IN.
        server.login("spschoen.alerts@gmail.com", "PASSWORD")
        server.sendmail(fromMail, to, str(email_text))
        server.close()
    except:
        print("Couldn't even send an email, wot")
        for error in sys.exc_info():
            print(error + "")
