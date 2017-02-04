from github import *

#Note to self: IT REALLY FUCKING NEEDS THE /api/v3 ENDING
#BECAUSE NO DOCUMENTATION ON THIS ISSUE FUCK'S SAKE.
g = Github("spschoen","4mpEnQUi", base_url="https://github.ncsu.edu/api/v3")
#g = Github("spschoen", "5rVO&7d&p@V4BI!m")

spschoen = g.get_user()
print(spschoen.name)
print(spschoen.login)
print()

for repo in g.get_user().get_repos():
    print(repo.name)
    if repo.name == "E-115-Scripts":
        for commit in repo.get_commits():
            print(commit.commit.sha)
            print(commit.commit.author.name)
            print(commit.commit.author.date)
            print(commit.commit.author.email)
            print(commit.commit.message.replace('\n\n',' - ').replace('\n','')[:50])
            print()
