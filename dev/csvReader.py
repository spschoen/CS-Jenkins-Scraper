"""
@authors Samuel Schoeneberger 02/2017

Execution: python3 csvReader.py $WORKSPACE $PROJECT_ID $GIT_COMMIT
0. commitUpload.py
1. WORKSPACE  : /path/to/report.csv (DO NOT INCLUDE report.csv)
2. PROJECT_ID : PW-XYZ
3. GIT_COMMIT : [40 char commit hash]
"""

import csv
import sys
import os
import pymysql

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

# TODO: take argument
with open('site/jacoco/report.csv', newline='') as csvfile:
    report = csv.DictReader(csvfile, delimiter=',')
    for row in report:
        for row in report:
            if "gui" not in row['PACKAGE'].lower() and row['CLASS'][-4:].lower() != "test":
                print(row['PACKAGE'].split(".")[-1],
                        row['CLASS'].split(".")[-1],
                        row['LINE_MISSED'],
                        row['LINE_COVERED'])
