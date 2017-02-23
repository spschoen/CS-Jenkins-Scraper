# Custom commit uploader
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

# Execution: python3 commitUpload.py path/to/.git $GIT_URL $GIT_COMMIT

import sys
import os
import pymysql.cursors
from git import *
from datetime import date, datetime, timedelta


# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
connection = pymysql.connect(host="152.46.20.243",
                                user="root",
                                password="",
                                db="repoinfo")
cur = connection.cursor()

# Getting path to .git directory.
FILE_DIR = os.path.abspath(os.path.join(os.getcwd()))
for arg in sys.argv[1].split("/"):
    if arg == "" or ".py" in arg:
        continue
    FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, arg))

# Checking if user supplied .git directory, or just dir where .git is.
# If the latter, add /.git
if FILE_DIR[-4:] != ".git":
    FILE_DIR = FILE_DIR + "/.git"

# repoID = PX-ABC
# FILE_DIR = /home/jenkins/.../
repoID = FILE_DIR.split("/")[-2][-6:]
if repoID[0] != "P":
    #print("Wrong directory.  If you see this, please email spschoen immediately.")
    sys.exit()

repo = Repo(FILE_DIR)
tree = repo.tree()
hash = repo.head.object.hexsha

cur.execute("SELECT * FROM commitUID WHERE Hexsha = %s and Repo = %s", (hash, repoID))

if cur.rowcount == 0:
    try:
        insert = "INSERT INTO commitUID (commitUID, Hexsha, Repo) VALUES (NULL, '%s', '%s')"
        cur.execute( insert, (hash, repoID) )
    except e:
        #debug
        print(e[0] + "|" + e[1])
        # TODO: email when failure happens.
        connection.rollback()
else:
    pass

connection.close()
