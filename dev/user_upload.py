"""
Upload users and matches them to Projects in database - used for Dashboard.

Args:
    Name of file containing student IDs & project IDs

Authors:
    Samuel Schoeneberger
"""

import pymysql
import os
import sys

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

try:
    connection = pymysql.connect(host=ip, user=user, password=pw, db=db)
except:
    error_string = sys.exc_info()[0] + "\n----------\n"
    error_string += sys.exc_info()[1] + "\n----------\n"
    error_string += sys.exc_info()[2]
    print(error_string)
cur = connection.cursor()

f = open("students.txt", "r")

upload = "INSERT INTO users(id, unityID, ProjectID) VALUES (NULL, %s, %s)"

for line in f:
    project_id = line.split(":")[0]
    users = line.split(":")[1].split(" ")
    for user in users:
        try:
            cur.execute(upload, (user.replace("\n",""), project_id))
        except:
            connection.rollback()
            error_string = sys.exc_info()[0] + "\n----------\n"
            error_string += sys.exc_info()[1] + "\n----------\n"
            error_string += sys.exc_info()[2]
            print(error_string)


connection.close()
