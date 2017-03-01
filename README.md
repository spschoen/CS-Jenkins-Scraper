# Jenkins Data Scrapers

Do you have dozens, hundreds of students constantly pushing to Jenkins, building Megs and Megs of untapped data that you could use to write grant proposals with?  Do you want to know exactly what test was the worst test to deal with for all students?  Do you find Databases fun?

Then use these scrapers, plain and simple.  Follow the instructions below to setup (or contact spschoen@ncsu.edu or razeitle@ncsu.edu for help) these scripts to pull information from each student submission to Jenkins, and place into a database of your choosing.

Warning: Data is not anonymized and can be traced back to students if malicious folks got access to the database.

 * Do not leave Databases unsecured
 * Do not leave Databases unattended
 * Unattended databases will be asked to hold ```Robert'); DROP TABLE Students; --```

Alternatively, you can (manually) remove the Author column from the Commits table, and the respective usage in the scripts, and it'll be nearly anonymized.

TL;DR These are a bunch of scripts which, when run, will scrape data from all the xml files produced by Jenkins, and feed that information into a Database, for future calculations.

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
4. Ensure ant builds include JaCoCo coverage report output.


## Database Setup

1. Download repo_base.sql
2. Enter mysql: ```mysql -u root -p```
3. Create the DB: ```create database [DB NAME];```
4. Switch to the new DB: ```use [DB NAME];```
5. Import the file. ```source repo_base.sql```
