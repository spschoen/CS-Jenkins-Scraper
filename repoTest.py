from git import *
from git.objects.util import *
import datetime
import time

pulled_commits = 60

repo = Repo("C:/users/Sam/Documents/Github/Tscripts/.git/")
hc = repo.head.commit

# Verification
#print(hc.hexsha)

first_commits = list(repo.iter_commits('master', max_count=pulled_commits))
#print(first_commits)
    
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
        #print(first_commits[pulled_commits - i].committed_date)
        #print(commit.committed_date)
        #print(commit.committed_date - first_commits[pulled_commits - i].committed_date)
        last = first_commits[pulled_commits - i].committed_date
        now = commit.committed_date
        dur = now - last
        dur = str(datetime.timedelta(seconds=dur))
        print(' |-->      Time:', dur, 'since last commit')
        
    print(' |-->   Message:', commit.message.replace('\n\n',' - ') + '\n')
    i += 1
    
#lazy