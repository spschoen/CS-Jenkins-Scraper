from git import *
from git.objects.util import *
import datetime
import time
import os

#repo = Repo("C:/users/Sam/Documents/Github/Tscripts/.git/")
repo = Repo(os.getcwd() + "/.git")
hc = repo.head.commit

# Verification
#print(hc.hexsha)

default_pulled = 10

first_commits = list(repo.iter_commits('master', max_count=default_pulled))
first_commits = list(repo.iter_commits('master', max_count=first_commits[0].count()))
#print(first_commits)

print(first_commits[0].count())
    
i = 0
for commit in reversed(first_commits):
    print('Commit', i)
    print(' |-->    HexSHA:', commit.hexsha)
    if len(commit.parents) > 1:
        print(' |-->   Parents:', commit.parents)
    print(' |-->    Author:', commit.author.name)
    if commit.author.name != commit.committer.name:
        print(' |--> Committer:', commit.committer.name)
    print(' |--> Committed:', time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(commit.committed_date)))
    if i != 0:
        #print(first_commits[first_commits[0].count() - i].committed_date)
        #print(commit.committed_date)
        #print(commit.committed_date - first_commits[first_commits[0].count() - i].committed_date)
        last = first_commits[first_commits[0].count() - i].committed_date
        now = commit.committed_date
        dur = now - last
        dur = str(datetime.timedelta(seconds=dur))
        print(' |-->      Time:', dur, 'since last commit')
        
    print(' |-->   Message:', commit.message.replace('\n\n',' - ') + '\n')
    i += 1
    
#lazy
