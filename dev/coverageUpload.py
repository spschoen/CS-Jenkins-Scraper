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
import os

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
                                    db=config_info['db'], commit_hash=commit_hash, repo_id=repo_id)

if not os.path.exists(FILE_DIR + '/report.csv'):
    print(FILE_DIR + "/report.csv")
    print("Could not access report.csv. Exiting.")
    sys.exit()

try:
    csv_file = open(FILE_DIR + "/report.csv", newline='')
except:
    print("Failed to open report.csv file; please contact a TA.")
    sys.exit()


report = csv.DictReader(csv_file, delimiter=',')
for row in report:
    if "gui" in row['PACKAGE'].lower() or row['CLASS'][-4:].lower() == "test":
        continue

    class_uid = Scraper.get_class_uid(ip=config_info['ip'], user=config_info['user'], pw=config_info['pass'],
                                      db=config_info['db'], class_name=row['CLASS'].split(".")[-1],
                                      package=row['PACKAGE'].split(".")[-1])

    coverage = int(row['LINE_COVERED']) / (int(row['LINE_MISSED']) + int(row['LINE_COVERED']))
    coverage = str(round(coverage * 100))

    instruction = int(row['INSTRUCTION_COVERED']) / (int(row['INSTRUCTION_MISSED']) + int(row['INSTRUCTION_COVERED']))
    instruction = str(round(instruction * 100))

    branch = int(row['BRANCH_COVERED']) / (int(row['BRANCH_MISSED']) + int(row['BRANCH_COVERED']))
    branch = str(round(branch * 100))

    complexity = int(row['COMPLEXITY_COVERED']) / (int(row['COMPLEXITY_MISSED']) + int(row['COMPLEXITY_COVERED']))
    complexity = str(round(complexity * 100))

    method = int(row['METHOD_COVERED']) / (int(row['METHOD_MISSED']) + int(row['METHOD_COVERED']))
    method = str(round(method * 100))

    search = "SELECT * FROM coverage WHERE CommitUID = %s AND ClassUID = %s AND Line_Coverage = %s AND " \
             "Instruction_Coverage = %s AND Branch_Coverage = %s AND Complexity_Coverage = %s AND Method_Coverage = %s"
    cur.execute(search, (commit_uid, class_uid, coverage, instruction, branch, complexity, method))
    if cur.rowcount != 0:
        continue

    insert = "INSERT INTO coverage(CommitUID, ClassUID, Line_Coverage, Instruction_Coverage, Branch_Coverage," \
             "Complexity_Coverage, Method_Coverage) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(insert, (commit_uid, class_uid, coverage, instruction, branch, complexity, method))
    except:
        connection.rollback()
        ErrorString = sys.exc_info()[0] + "\n----------\n"
        ErrorString += sys.exc_info()[1] + "\n----------\n"
        ErrorString += sys.exc_info()[2]
        fail_list = "(CommitUID, ClassUID, Line_Coverage, Instruction_Coverage, Branch_Coverage, "
        fail_list += "Complexity Coverage, Method_Coverage)"
        Scraper.sendFailEmail("Failed to insert into Coverage table!", "The following insert failed:", insert,
                              fail_list, ErrorString, commit_uid, class_uid,
                              (commit_uid, class_uid, coverage, instruction, branch, complexity, method))

connection.close()
