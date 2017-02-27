"""
@authors Samuel Schoeneberger 02/2017

Execution: python3 csvReader.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
0. commitUpload.py
1. WORKSPACE  : /path/to/report.csv (DO NOT INCLUDE report.csv)
2. PROJECT_ID : PW-XYZ
3. GIT_COMMIT : [40 char commit hash]

+-------------+---------+------+-----+---------+-------+
| Field       | Type    | Null | Key | Default | Extra |
+-------------+---------+------+-----+---------+-------+
| CommitUID   | int(11) | NO   | PRI | NULL    |       |
| ClassUID    | int(11) | YES  |     | NULL    |       |
| Coverage    | int(11) | YES  |     | NULL    |       |
| Instruction | int(11) | YES  |     | NULL    |       |
| Branch      | int(11) | YES  |     | NULL    |       |
| Complexity  | int(11) | YES  |     | NULL    |       |
| Line        | int(11) | YES  |     | NULL    |       |
+-------------+---------+------+-----+---------+-------+
"""

import csv
import sys
import os
import pymysql
import MySQL_Func

if len(sys.argv) != 4:
    print("Did not get expected args.")
    sys.exit()

connection = pymysql.connect(host="152.46.20.243", user="root", password="", db="repoinfo")
cur = connection.cursor()

# Getting path to report.csv
FILE_DIR = "/"
# Iterate through $WORKSPACE to set up the directory.
for arg in sys.argv[1].split("/"):
    if arg != "":
        FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))

repoID = sys.argv[2]
hash = sys.argv[3]

commitUID = MySQL_Func.getCommitUID(
                IP="152.46.20.243",
                user="root",
                pw="",
                DB="repoinfo",
                hash=hash,
                repoID=repoID)

# TODO: take argument
csvfile = open('site/jacoco/report.csv', newline='')
report = csv.DictReader(csvfile, delimiter=',')
for row in report:
    if "gui" not in row['PACKAGE'].lower() and row['CLASS'][-4:].lower() != "test":
        classUID = MySQL_Func.getClassUID(
                        IP="152.46.20.243",
                        user="root",
                        pw="",
                        DB="repoinfo",
                        className=row['CLASS'].split(".")[-1],
                        package=row['PACKAGE'].split(".")[-1])
        #print(row['LINE_MISSED'].ljust(3) + " | " + row['LINE_COVERED'].ljust(3))
        coverage = int(row['LINE_COVERED']) / (int(row['LINE_MISSED']) + int(row['LINE_COVERED']))
        print(row['CLASS'].split(".")[-1].ljust(16) + " | " + str(round(coverage * 100)))

        insert = "INSERT INTO coverage(CommitUID, ClassUID, Line) VALUES (%s, %s, %s)"
        try:
            cur.execute(insert, (commitUID, classUID, str(round(coverage * 100))))
        except:
            #TODO: Email on Failure
            for error in sys.exc_info():
                print(error)
