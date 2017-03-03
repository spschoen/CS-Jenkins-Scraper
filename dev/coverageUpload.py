"""
@authors Samuel Schoeneberger 02/2017

Execution: python3 coverageUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
0. commitUpload.py
1. WORKSPACE  : /path/to/report.csv (DO NOT INCLUDE report.csv)
                    This isn't implemented yet, just because I haven't gotten the chance.  - Sam

2. PROJECT_ID : PW-XYZ
3. GIT_COMMIT : [40 char commit hash]
"""

import csv
import sys
import os
import pymysql
import MySQL_Func

if len(sys.argv) != 4:
    print("Did not get expected args.")
    sys.exit()

# FIXME: Change these to whatever your production DB is at.
IP = "152.46.20.243"
user = "root"
pw = ""
DB = "repoinfo"

connection = pymysql.connect(host=IP, user=user, password=pw, db=DB)
cur = connection.cursor()

# Getting path to report.csv
FILE_DIR = "/"
# Iterate through $WORKSPACE to set up the directory.
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))

repoID = sys.argv[2]
hash = sys.argv[3]

commitUID = MySQL_Func.getCommitUID(IP=IP, user=user, pw=pw, DB=DB, hash=hash, repoID=repoID)

csvfile = open('site/jacoco/report.csv', newline='')
report = csv.DictReader(csvfile, delimiter=',')
for row in report:
    if "gui" not in row['PACKAGE'].lower() and row['CLASS'][-4:].lower() != "test":
        classUID = MySQL_Func.getClassUID(
                        IP=IP,
                        user=user,
                        pw=pw,
                        DB=DB,
                        className=row['CLASS'].split(".")[-1],
                        package=row['PACKAGE'].split(".")[-1])
        coverage = int(row['LINE_COVERED']) / (int(row['LINE_MISSED']) + int(row['LINE_COVERED']))
        coverage = str(round(coverage * 100))

        search = "SELECT * FROM coverage WHERE CommitUID = %s AND ClassUID = %s AND Line = %s"
        cur.execute(search, (commitUID, classUID, coverage))
        if cur.rowcount != 0:
            continue

        insert = "INSERT INTO coverage(CommitUID, ClassUID, Line) VALUES (%s, %s, %s)"
        try:
            cur.execute(insert, (commitUID, classUID, coverage))
        except:
            connection.rollback()
            ErrorString = sys.exc_info()[0] + "\n----------\n"
            ErrorString += sys.exc_info()[1] + "\n----------\n"
            ErrorString += sys.exc_info()[2]
            MySQL_Func.sendFailEmail("Failed to insert into Coverage table!",
                                        "The following insert failed:",
                                        insert,
                                        "(CommitUID, ClassUID, Line)",
                                        ErrorString,
                                        commitUID, classUID, coverage)

connection.close()
