#sudo /etc/init.d/mysql start

from git import *
from git.objects.util import *
from future_builtins import *
import MySQLdb
import os
#import subprocess

#The DB conection
cnx = MySQLdb.connect("localhost","root","p@55w0rd","WTP")

#Because this is how we connect
cur = cnx.cursor()

#Local repo
repo = Repo(os.getcwd() + "/.git")
default_pulled = 1000
#I would be worried if a 216 repo had more than 1000 commits.
#So this second line *SHOULD* handle that.
first_commits = list(repo.iter_commits('master', max_count=default_pulled))
first_commits = list(repo.iter_commits('master', \
                                        max_count=first_commits[0].count()))

#print(first_commits[0].count())

i = 0

for commit in reversed(first_commits):
    insert = ""
    dur = 0
    if i != 0:
        # Future note to me - figure out the longest time between possible commits.
        # and then pad out the duration with zeros to fit that.
        last = first_commits[first_commits[0].count() - i].committed_date
        now = commit.committed_date
        dur = now - last

    #Insert message - packages up the commit info and gets it ready to be
    #parsed by mysql
    insert = "INSERT INTO commits(id, hexSHA, author, time, duration, Message) \
    VALUES (NULL, '%s', '%s', '%d', '%d', '%s')" % \
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
        print("Unable to execute '%s', '%s', '%d', '%04d', '%s'") % \
        (commit.hexsha, commit.author.name[:8], commit.committed_date, dur, \
        commit.message.replace('\n\n',' - ').replace('\n','').replace('\'','\\\'')[:50])
        print("Sending error mail to spschoen.alerts")
        #ps = subprocess.Popen(['printf', 'Unable to add commit %s to db' % commit.hexsha], stdout=subprocess.PIPE)
        #out = subprocess.check_output(('msmtp', 'spschoen.alerts@gmail.com'), stdin=ps.stdout)
        #ps.wait()
        cnx.rollback()

    i += 1

#Close the connection.
cnx.close()
