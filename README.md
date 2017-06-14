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
#### Without `*_setup.sh`

1. Update yum: ```sudo yum update```
2. Install Python3 (because RHEL is sensitive about 2.6): ```sudo yum install python34.x86_64```
3. Install cloc (Used by `commitUpload.py`): ```sudo yum install cloc```
3. Install gitstats (Used by `commitUpload.py`): ```sudo yum install gitstats```
4. Install Modules ```sudo pip3 install PyMySQL && sudo pip3 install GitPython```
5. Export git to path, just to be safe: ```sudo echo "PATH=$PATH:/usr/local/git/bin/"```

Alternatively, instead of using `pip` to install the modules, you can clone them from their repositories and make them:    
```git clone https://github.com/PyMySQL/PyMySQL.git```    
```git clone https://github.com/gitpython-developers/GitPython.git```    
```cd   GitPython; sudo python3 setup.py install```    
```cd ../PyMySQL/; sudo python3 setup.py install```

___

#### With `*_setup.sh`

1. Execute ```sudo sh master_setup.sh <IP for Executor 1> <IP for Executor 2> ... ``` on the master server.  Will install MySQL 5.6, as well as set up the database using base.sql, then setup Executors to have access.  In theory.
1. Execute ```sudo sh executor_setup.sh``` on the executor server.  Will install Python and needed modules.

___

***RESTART THE EXECUTOR*** at this point.

## Downloading Scrapers

1. Clone repo: ```git clone https://github.ncsu.edu/spschoen/CSC216-Python-Analyzer.git```
2. Move the scripts to your preferred location for use by `ant`.  Working location is `/home/jenkins/scripts`, however `runscript.sh` takes an argument of any directory containing the scripts, so any location is usable.

## Post Installation Instructions

1. Setup MySQL Server on your Master server.
2. Add `runscript.sh` to your post-build action in Jenkins - see the `README.md` file in `docs/` for more information.
3. Ensure `ant` builds include JaCoCo coverage report output.
4. Rename `example_config.json` to `config.json`
5. Edit `config.json` to contain your DB info (IP, username, password, database name)
6. Copy `config.json` to somewhere that ant can access it, then edit `build.xml` to copy it to the local directory.


## Database Setup (Master)

1. Download `base.sql`
2. Enter mysql: ```mysql -u root -p```
3. Create the DB: ```create database [DB NAME];```
4. Switch to the new DB: ```use [DB NAME];```
5. Import the file. ```source base.sql```

## File structure

* dev/
  * `*Upload.py` files read local files and upload data to your Database
  * `*Scanner` files scan the project for certain things (method names, packages, etc.) for Uploaders.
  * `runScript.sh` is the script which should be added to the post-build
* Docs/
  * DB_Tables represents the structure of a database, a plain text and easy to read version of repo_base.sql
  * `base.sql` is a dump file which can be imported into created databases to setup for the scripts.
* old/
  * These scripts are example scripts/XML which were used to create dev/ scripts.  They can be safely ignored (and deleted, which we should probably do)
