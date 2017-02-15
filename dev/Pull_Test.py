from git import *
from git.objects.util import *
from future_builtins import *
import MySQLdb
import os

#See MySQL_Test.py for better comments on this.
#The DB conection
DB = MySQLdb.connect(host="152.46.20.243", user="root", passwd="",
                        db="repoinfo")
print("DB connected.")

cursor = DB.cursor()
print("Cursor made.")

cursor.execute("SELECT * FROM commits")
print("Command executed.")

for row in cursor.fetchall():
    print(row)
    print(len(row))
    for col in row:
            

DB.close()
