#sudo /etc/init.d/mysql start

from git import *
from git.objects.util import *
from future_builtins import *
import MySQLdb
import os

#The DB conection
cnx = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

#Because this is how we connect
cur = cnx.cursor()

#Local repo
repo = Repo(os.getcwd() + "/.git")
default_pulled = 10
first_commits = list(repo.iter_commits('master', max_count=default_pulled))
first_commits = list(repo.iter_commits('master',
                                        max_count=first_commits[0].count()))

#print(first_commits[0].count())

i = 0

for commit in reversed(first_commits):
    #print('Commit')
    #print(' |-->    HexSHA:', commit.hexsha)
    #if len(commit.parents) > 1:
    #    print(' |-->   Parents:', commit.parents)
    #print(' |-->    Author:', commit.author.name)
    #if commit.author.name != commit.committer.name:
    #    print(' |--> Committer:', commit.committer.name)
    #print(' |--> Committed:', time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(commit.committed_date)))
    insert = ""
    dur = 0
    if i != 0:
        last = first_commits[first_commits[0].count() - i].committed_date
        now = commit.committed_date
        dur = now - last

    insert = "INSERT INTO commits(id, hexSHA, author, time, duration, Message) \
    VALUES (NULL, '%s', '%s', '%d', '%d', '%s')" % \
    (commit.hexsha, commit.author.name, commit.committed_date, dur, commit.message.replace('\n',''))

    try:
        cur.execute(insert)
        cnx.commit()
    except:
        cnx.rollback()

    i += 1

#Debug below: selects all from the table, and then prints it.
cur.execute("SELECT * FROM commits")

for row in cur.fetchall():
    print(row)

#Close the connection.
cnx.close()
