"""
Reads report.csv file from jacoco and uploads coverage information to given database.

Requirements:
    Scraper.py - library for interaction with databases must be available in the same directory as this file.
    config.txt    - file specifying database information.

Args:
    1. WORKSPACE  - Absolute path to the location of report.csv
    2. PROJECT_ID - 17 char string representing class, section, project, and unique ID of the current project.
                    For example: csc216-002-P2-096
    3. GIT_COMMIT - 40 Character commit hash.

Returns:
    N/A

Authors:
    Renata Ann Zeitler
    Samuel Schoeneberger
"""

import csv
import sys
import pymysql
import Scraper

if len(sys.argv) != 4:
    print("Did not get expected args.")
    sys.exit()

# Getting config options.
config_info = Scraper.get_config_options()
connection = pymysql.connect(host=config_info['ip'], user=config_info['user'],
                             password=config_info['pass'], db=config_info['db'])
cur = connection.cursor()

FILE_DIR = Scraper.get_file_dir()

repo_id = sys.argv[2]
commit_hash = sys.argv[3]

commit_uid = Scraper.get_commit_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                    db=config_info['db'], hash=commit_hash, repo_id=repo_id)

try:
    csvfile = open(FILE_DIR + "/report.csv", newline='')
except:
    print("Failed to open report.csv file; please contact a TA.")
    sys.exit()


report = csv.DictReader(csvfile, delimiter=',')
for row in report:
    if "gui" not in row['PACKAGE'].lower() and row['CLASS'][-4:].lower() != "test":
        class_uid = Scraper.get_class_uid(IP=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                          DB=config_info['db'], className=row['CLASS'].split(".")[-1],
                                          package=row['PACKAGE'].split(".")[-1])

        coverage = int(row['LINE_COVERED']) / (int(row['LINE_MISSED']) + int(row['LINE_COVERED']))
        coverage = str(round(coverage * 100))

        search = "SELECT * FROM coverage WHERE CommitUID = %s AND ClassUID = %s AND Line = %s"
        cur.execute(search, (commit_uid, class_uid, coverage))
        if cur.rowcount != 0:
            continue

        insert = "INSERT INTO coverage(CommitUID, ClassUID, Line) VALUES (%s, %s, %s)"
        try:
            cur.execute(insert, (commit_uid, class_uid, coverage))
        except:
            connection.rollback()
            ErrorString = sys.exc_info()[0] + "\n----------\n"
            ErrorString += sys.exc_info()[1] + "\n----------\n"
            ErrorString += sys.exc_info()[2]
            Scraper.sendFailEmail("Failed to insert into Coverage table!", "The following insert failed:", insert,
                                  "(CommitUID, ClassUID, Line)", ErrorString, commit_uid, class_uid, coverage)

connection.close()
