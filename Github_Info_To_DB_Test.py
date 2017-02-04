#sudo /etc/init.d/mysql start

#Don't know why I make the names have underscores.  Better than spaces.
#You could do better
#hashtag or comment?

#All the packages we use.
from git import *
from git.objects.util import *
from future_builtins import *
import MySQLdb
import os

#See MySQL_Test.py for better comments on this.
#The DB conection
cnx = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

#Because this is how we connect
cur = cnx.cursor()

#The repo of wherever this script is run.
repo = Repo(os.getcwd() + "/.git")
default_pulled = 1000
#I would be worried if a 216 repo had more than 1000 commits.
#So this second line *SHOULD* handle that.
first_commits = list(repo.iter_commits('master', max_count=default_pulled))
first_commits = list(repo.iter_commits('master', \
                                        max_count=first_commits[0].count()))

f = open(os.path.join(os.getcwd()+"/output/lines_of_code.dat"), "r")
data = f.readlines()

#A Loop to get each commit in the repo, and then put it in the DB.
#i is used to make sure we aren't doing some weird duration calculation.
i = 0
for commit in reversed(first_commits):
    #Seting insert to be blank, duration to 0, and then checking if there's a
    #Previous commit.  If there is, calculate how much time elapsed between
    #them.
    insert = ""
    dur = 0
    if i != 0:
        # Future note to me - figure out the longest time between possible commits.
        # and then pad out the duration with zeros to fit that.
        last = first_commits[first_commits[0].count() - i].committed_date
        now = commit.committed_date
        dur = now - last

    #Insert message - packages up the commit info and gets it ready to be
    #parsed by MySQL
    try:
        insert = "INSERT INTO commits(id, hexSHA, author, time, duration, Message, loc) \
        VALUES (NULL, '%s', '%s', '%d', '%d', '%s', '%d')" % \
        (commit.hexsha, commit.author.name[:8], commit.committed_date, dur, \
        commit.message.replace('\n\n',' - ').replace('\n','').replace('\'','\\\'')[:50], \
        int(data[i].replace("\n","").split(" ")[1]))
        # removing double/single lines ^ here and here ^                ^
        #                   making the ' characters safe to insert here ^
        #                       by wrapping them up.
        #If you left them in there, unescaped, then you'd allow commit messages to
        #break the insert command and potentially break the DB.
        #Before added, it would simply refuse to add the commit to the DB.
    except:
        insert = "INSERT INTO commits(id, hexSHA, author, time, duration, Message, loc) \
        VALUES (NULL, '%s', '%s', '%d', '%d', '%s', NULL)" % \
        (commit.hexsha, commit.author.name[:8], commit.committed_date, dur, \
        commit.message.replace('\n\n',' - ').replace('\n','').replace('\'','\\\'')[:50])
    #Try/except block - it will send MySQL the command to run, and commit it.
    #If it can't run the command, print the command that was attempted and then email
    #the error to someone who cares - that will probably be removed but I wanted to do it
    #Anyways.  Oh, it also removes the attempt from the database, which is nice.
    try:
        cur.execute(insert)
        cnx.commit()
    except:
        print("Unable to execute '%s', '%s', '%d', '%04d', '%s', '%d'") % \
        (commit.hexsha, commit.author.name[:8], commit.committed_date, dur, \
        commit.message.replace('\n\n',' - ').replace('\n','').replace('\'','\\\'')[:50], \
        int(data[i].replace("\n","").split(" ")[1]))
        cnx.rollback()

    i += 1

#Close the connection.
cnx.close()
