import pymysql
import smtplib
import sys
import os
import platform


def get_method_uid(ip, user, pw, db, method, class_name, package):
    """
    get_method_uid will take args to connect to a Database, as well as the names of the method, class, and
    package to be identified.  It will check the database records for the method UID (and, implicitly, the class UID)
    and if it does not exist, it will create it, then check for the new method UID.
    Finally, it will return the newly found method UID.

    Args:
        ip         - The ip address that the database is located.
        user       - Username used to log into the database.  Should have read/write access.
        pw         - password for the user to log in with.
        db         - Database to manipulate.
        method     - Name of method to lookup/insert into the db
        class_name - Name of the class that the above method is in.
        package    - Name of the package that the above class is in.

    Returns:
        Unique ID number of the method in the MethodUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to db
    try:
        connection = pymysql.connect(host=ip, user=user, password=pw, db=db)
    except:
        print(sys.exc_info())
        sys.exit()

    cur = connection.cursor()

    # print("Searching for method_uid")
    class_uid = get_class_uid(ip=ip, user=user, pw=pw, db=db,
                              class_name=class_name, package=package)

    select = "SELECT * FROM methodUID WHERE ClassUID = %s AND Method = %s"
    cur.execute(select, (class_uid, method))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        insert = "INSERT INTO methodUID(methodUID, classUID, Method) VALUES (Null, %s, %s)"
        try:
            cur.execute(insert, (class_uid, method))
        except:
            connection.rollback()
            error_string = sys.exc_info()[0] + "\n----------\n"
            error_string += sys.exc_info()[1] + "\n----------\n"
            error_string += sys.exc_info()[2]
            send_fail_email("Failure to insert into method_uid!", "The following insert statement failed: ", insert,
                            "The variables were: ", error_string, package, class_name)

    cur.execute(select, (class_uid, method))
    method_uid = str(cur.fetchone()[0])

    connection.close()
    return method_uid


def get_class_uid(ip, user, pw, db, class_name, package):
    """
    get_class_uid will take args to connect to a Database, as well as the names of the class and package to be
    identified.  It will check the database records for the class UID and if it does not exist, it will create it,
    then check for the new class UID.  Finally, it will return the newly found class UID.

    Args:
        ip         - The ip address that the database is located.
        user       - Username used to log into the database.  Should have read/write access.
        pw         - password for the user to log in with.
        db         - Database to manipulate.
        class_name - Name of the class to lookup/add to db.
        package    - Name of the package that the above class is in.

    Returns:
        Unique ID number of the class in the ClassUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to db
    try:
        connection = pymysql.connect(host=ip, user=user, password=pw, db=db)
    except:
        print(sys.exc_info())
        sys.exit()

    cur = connection.cursor()

    # print("Searching for classUID")
    select = "SELECT * FROM classUID WHERE Package = %s AND Class = %s"
    cur.execute(select, (package, class_name))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        insert = "INSERT INTO classUID(classUID, Package, Class) VALUES (Null, %s, %s)"
        try:
            cur.execute(insert, (package, class_name))
        except:
            connection.rollback()
            error_string = sys.exc_info()[0] + "\n----------\n"
            error_string += sys.exc_info()[1] + "\n----------\n"
            error_string += sys.exc_info()[2]
            send_fail_email("Failure to insert into classUID!", "The following insert statement failed: ", insert,
                            "The variables were: ", error_string, package, class_name)

    cur.execute(select, (package, class_name))
    class_uid = str(cur.fetchone()[0])

    connection.close()
    return class_uid


def get_test_method_uid(ip, user, pw, db, method, class_name, package):
    """
    getTestMethodUID will take args to connect to a Database, as well as the names of the tes method, class, and
    package to be identified.  It will check the database records for the test method UID
    (and, implicitly, the class UID) and if it does not exist, it will create it, then check for the new test method
    UID.  Finally, it will return the newly found method UID.

    Args:
        ip         - The ip address that the database is located.
        user       - Username used to log into the database.  Should have read/write access.
        pw         - password for the user to log in with.
        db         - Database to manipulate.
        method     - Name of method to lookup/insert into the db
        class_name - Name of the class that the above method is in.
        package    - Name of the package that the above class is in.

    Returns:
        Unique ID number of the method in the TestMethodUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to db
    try:
        connection = pymysql.connect(host=ip, user=user, password=pw, db=db)
    except:
        print(sys.exc_info())
        sys.exit()

    cur = connection.cursor()

    # print("Searching for testMethodUID")
    test_class_uid = get_test_class_uid(ip=ip, user=user, pw=pw, db=db,
                                        class_name=class_name, package=package)

    select = "SELECT * FROM testMethodUID WHERE testClassUID = %s AND testMethodName = %s"
    cur.execute(select, (test_class_uid, method))

    # print("Selected " + str(cur.rowcount) + " elements.")

    if cur.rowcount == 0:
        insert = "INSERT INTO testMethodUID(testMethodUID, testClassUID, testMethodName) VALUES (Null, %s, %s)"
        try:
            cur.execute(insert, (test_class_uid, method))
        except:
            connection.rollback()
            error_string = sys.exc_info()[0] + "\n----------\n"
            error_string += sys.exc_info()[1] + "\n----------\n"
            error_string += sys.exc_info()[2]
            send_fail_email("Failure to insert into testMethodUID!", "The following insert statement failed: ", insert,
                            "The variables were: ", error_string, method, package, class_name)

    cur.execute(select, (test_class_uid, method))
    test_method_uid = str(cur.fetchone()[0])

    connection.close()
    return test_method_uid


def get_test_class_uid(ip, user, pw, db, class_name, package):
    """
    get_class_uid will take args to connect to a Database, as well as the names of the test class and package to be
    identified.  It will check the database records for the test class UID and if it does not exist, it will create it,
    then check for the new test class UID.  Finally, it will return the newly found test class UID.

    Args:
        ip         - The ip address that the database is located.
        user       - Username used to log into the database.  Should have read/write access.
        pw         - password for the user to log in with.
        db         - Database to manipulate.
        class_name - Name of the class to lookup/add to db.
        package    - Name of the package that the above class is in.

    Returns:
        Unique ID number of the class in the TestClassUID Table.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to db
    try:
        connection = pymysql.connect(host=ip, user=user, password=pw, db=db)
    except:
        print(sys.exc_info())
        sys.exit()

    cur = connection.cursor()

    # print("Searching for testClassUID")
    select = "SELECT * FROM testClassUID WHERE testPackage = %s AND testClass = %s"
    cur.execute(select, (package, class_name))

    # print("Selected " + str(cur.rowcount) + " elements.")

    insert = "INSERT INTO testClassUID(testClassUID, testPackage, testClass) VALUES (Null, %s, %s)"

    if cur.rowcount == 0:
        try:
            cur.execute(insert, (package, class_name))
        except:
            connection.rollback()
            error_string = sys.exc_info()[0] + "\n----------\n"
            error_string += sys.exc_info()[1] + "\n----------\n"
            error_string += sys.exc_info()[2]
            send_fail_email("Failure to insert into testClassUID!", "The following insert statement failed: ", insert,
                            "The variables were: ", error_string, package, class_name)

    cur.execute(select, (package, class_name))
    test_class_uid = str(cur.fetchone()[0])

    connection.close()
    return test_class_uid


def get_commit_uid(ip, user, pw, db, commit_hash, repo_id):
    """
    getCommitUID will take args to connect to a Database, as well as the Project ID and commit commit_commit_hash,
    to get the correct commitUID.  Will create a commitUID if it doesn't exist.

    Args:
        ip          - The ip address that the database is located.
        user        - Username used to log into the database.  Should have read/write access.
        pw          - password for the user to log in with.
        db          - Database to manipulate.
        commit_hash - the commit commit_hash of a git commit. 40 hex chars
        repo_id     - the repo to look up in the commitUID table.  cscABC-DEF-PG-XYZ

    Returns:
        Unique ID number of the commit, across all commits.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Connecting to db
    try:
        connection = pymysql.connect(host=ip, user=user, password=pw, db=db)
    except:
        print(sys.exc_info())
        sys.exit()

    cur = connection.cursor()

    select = "SELECT * FROM commits WHERE Commit_Hash = %s and Repo = %s"
    # cur.execute(select, (commit_hash, repo_id))

    # So since commitUID is gone now, I think this is basically dead.  If the commitUID doesn't exist, something
    # went wrong and this single method won't fix it.

    # UID doesn't exist
    # if cur.rowcount == 0:
    #     insert = "INSERT INTO commitUID(commitUID, commitUID, Repo) VALUES (NULL, %s, %s)"
    #     try:
    #         cur.execute(insert, (commit_hash, repo_id))
    #     except:
    #         connection.rollback()
    #         error_string = sys.exc_info()[0] + "\n----------\n"
    #         error_string += sys.exc_info()[1] + "\n----------\n"
    #         error_string += sys.exc_info()[2]
    #         send_fail_email("Failure to insert commitUID!", "The following insert failed: ", insert,
    #                         "The variables were: ", error_string, commit_hash, repo_id)

    cur.execute(select, (commit_hash, repo_id))
    commit_uid = str(cur.fetchone()[0])

    connection.close()
    return commit_uid


def send_fail_email(subject, failure_message, command, variable_list, trace, *variables):
    """
    Emails information provided to alert system.
    
    You HAVE to create your own GMAIL/NCSU Email account and set up its information here.
    An example email has been provided, but is not configured.

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
    from_mail = "spschoen.alerts@gmail.com"

    # TODO: Change this to whoever receives the fail mail.
    to = "spschoen.alerts@gmail.com"

    body = failure_message + "\n\n" + command + "\n\n"
    body += str(variable_list) + "\n\n"
    body += str(list(variables)) + "\n\n"
    body += "The following error message was produced:\n\n" + str(trace)

    email_text = "From: " + from_mail + ",\n"
    email_text += "To: " + to + ",\n"
    email_text += "Subject: " + subject + "\n\n"
    email_text += body

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        # TODO: YOU HAVE TO EDIT THE PASSWORD IN.
        server.login("spschoen.alerts@gmail.com", "PASSWORD")
        server.sendmail(from_mail, to, str(email_text))
        server.close()
    except:
        error_string = sys.exc_info()[0] + "\n----------\n"
        error_string += sys.exc_info()[1] + "\n----------\n"
        error_string += sys.exc_info()[2]
        print(error_string)


def get_config_options():
    """
    Read the config file (config.txt, hardcoded) and return the values inside.

    Args:
        N/A

    Returns:
        Dictionary of Args:
            ip   - ip address of server
            user - username to log into server with
            pass - password to log into server with
            db   - database to connect to on server

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Now, we begin reading the config file.
    if not os.path.exists('config.txt'):
        print("Config.txt does not exist.  Exiting.")
        sys.exit()

    config_file = open("config.txt", "r")
    lines = list(config_file)
    if len(lines) != 4:
        # incorrect config file
        # print("config.txt contains incorrect number of records.")
        sys.exit()

    # Setting up the db connection
    ip = lines[0].replace("\n", "")
    user = lines[1].replace("\n", "")
    pw = lines[2].replace("\n", "")
    db = lines[3].replace("\n", "")

    return {'ip': ip, 'user': user, 'pass': pw, 'db': db}


def get_file_dir(filepath):
    """
    Get the current file directory from an absolute address.

    Args:
        N/A

    Returns:
        absolute address of the supplied directory.

    Authors:
        Renata Ann Zeitler
        Samuel Schoeneberger
    """
    # Getting path to .git directory.
    if platform.system() is "Windows":
        file_dir = ""
        path_list = filepath.split("\\")
    else:
        file_dir = "/"
        path_list = filepath.split("/")

    for arg in path_list:
        if ":" in arg:
            file_dir = os.path.join(file_dir, arg + "\\")
        elif arg != "":
            file_dir = os.path.join(file_dir, arg)
        # print(arg.ljust(25) + " | " + file_dir)

    # Iterate through the path to git to set up the directory.

    return file_dir
