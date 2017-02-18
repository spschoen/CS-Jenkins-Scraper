# Custome commit uploader
# @authors Renata Ann Zeitler and Samuel Schoeneberger 02/2017

from __future__ import print_function
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import pymysql.cursors
from git import *
from git.objects.util import *
from datetime import date, datetime, timedelta
import os.path as osp


# Setting up the DB connection
# TODO: Change this to either enter or the master IP.
# Future people: change this to your master IP
# Or wherever your DB is.
# Don't forget to
connection = pymysql.connect(host="152.46.20.243",
   user="root",
   passwd="",
   db="repoinfo")
cur = connection.cursor()

        
join = osp.join

# rorepo is a Repo instance pointing to the git-python repository.
repo = Repo(self.rorepo.working_tree_dir)
assert not repo.bare

#The repo of wherever this script is run.
# repo = Repo(os.getcwd() + "/.git")
default_pulled = 1000

#Second line *SHOULD* handle if a repo has more than 1000 commits.
first_commits = list(repo.iter_commits('master', max_count=default_pulled))
first_commits = list(repo.iter_commits('master', \
                                        max_count=first_commits[0].count()))

f = open(os.path.join(os.getcwd()+"\output\lines_of_code.dat"), "r")
data = f.readlines()
for line in data:
    data[data.index(line)] = line.replace('\n','')


#Gets each commit for the DB
#i is used to make sure we aren't doing some weird duration calculation.
i = 0
#counts the difference in lines between each commit
prevLines = 0;
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
        loc = int(data[i].replace("\n","").split(" ")[1])
        lineDiff = loc - int(prevLines)

    try:
        insert = "INSERT INTO commits(CommitUID, Build_Num, Author, Time, Duration, Message, LOC , LOC_DIFF)" \
                    "VALUES (NULL, '%d', '%s', '%d', '%d', '%s', '%d', '%d')" % \
                        (commits.Build_Num, commits.Author.name[:8], commits.committed_date, dur, \
                        commits.message.replace('\n\n',' - ').replace('\n','').replace('\'','\\\'')[:50], \
                        loc, lineDiff)
    except: 
        print("Error 1". sys.exc_info())

    try:
        cur.execute(insert)
        cnx.commit()
    except:
        print("Error commiting to DB", sys.exc_info())
    
    i += 1
    prevLines = loc

connection.close()
