## Pre-Setup
#### (without setup.sh)

1. Update yum: ```sudo update yum```
2. Install Python3 (because RHEL is sensitive about 2.6): ```sudo yum install python34.x86_64```
3. Install cloc (Used by commitUpload.py): ```sudo yum install cloc```
3. Install Modules

```sudo pip3 install PyMySQL```    
```sudo pip3 install GitPython```

4. Export git to path, just to be safe: ```sudo echo "PATH=$PATH:/usr/local/git/bin/"```
5. ***RESTART THE EXECUTOR***

## Pre-Setup
#### (with setup.sh)

1. Execute ```sudo setup.sh```
2. ***RESTART THE EXECUTOR***

## Installation Instructions

1. ```git clone https://github.ncsu.edu/spschoen/CSC216-Python-Analyzer.git```


## Post Installation Instructions

1. Setup MySQL Server on your Master (I shouldn't have to explain this)
2. **Change IP, user, pw, and Database in each file** (Change DB w/ Project)
3. Add runscript.sh to your post-build action in Jenkins (cp it to the Workspace/ProjectName dir, run)


## Database Setup

1. Download repo_base.sql
2. Enter mysql: ```mysql -u root -p```
3. Create the DB: ```create database [DB NAME];```
4. Switch to the new DB: ```use [DB NAME];```
5. Import the file. ```source repo_base.sql```
