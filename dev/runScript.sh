#!/bin/bash
#RZandSSwereHere2017

echo ""

# Removing these from the directory; hiding them from students.
rm -rf $WORKDIR/ts_test
rm -rf $WORKDIR/ts_bin

echo "Data Miner:"

# TODO: Make this work without logging in.  Probably easier than I think.
#cd /home/jenkins/scripts/
#git pull
#cd $WORKDIR

echo "    [Data Miner] Beginning mining."
cd $WORKDIR

##################################
# Getting Project ID for CUID    #
##################################

 echo "    [Data Miner] Acquiring ProjectID scanner"
cp /home/jenkins/scripts/dev/splitter.sh $WORKDIR/splitter.sh

 echo "    [Data Miner] Getting Project ID"
PROJECT_ID=$(bash splitter.sh $GIT_URL)

##################################
# Uploading Commit Information.  #
##################################

 echo "    [Data Miner] Commit Information uploader fails; needs review."

 echo "    [Data Miner] Acquiring commit information uploader"
cp /home/jenkins/scripts/dev/commitUpload.py $WORKDIR/commitUpload.py

 echo "    [Data Miner] Executing commit information uploader"
python3 commitUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUMBER

##################################
# Scanning for methods           #
##################################

# echo "    [Data Miner] Acquiring method scanner"
cp /home/jenkins/scripts/dev/methodScan.sh $WORKDIR/methodScan.sh

# echo "    [Data Miner] Executing method scanner script"
sh $WORKDIR/methodScan.sh $WORKDIR/ > $WORKDIR/methods.txt

# echo "    [Data Miner] Acquiring method uploader"
cp /home/jenkins/scripts/dev/methodScanner.py $WORKDIR/methodScanner.py

# echo "    [Data Miner] Executing method uploader"
python3 methodScanner.py

##################################
# Scanning for tests             #
##################################

# echo "    [Data Miner] Acquiring test scanner"
cp /home/jenkins/scripts/dev/testScan.sh $WORKDIR/testScan.sh

# echo "    [Data Miner] Executing test scanner script"
sh $WORKDIR/testScan.sh $WORKDIR/ > $WORKDIR/tests.txt

# echo "    [Data Miner] Acquiring test uploader"
cp /home/jenkins/scripts/dev/testScanner.py $WORKDIR/testScanner.py

# echo "    [Data Miner] Executing test uploader"
python3 testScanner.py

##################################
# Checkstyle uploading.          #
##################################

# echo "    [Data Miner] Acquiring checkstyle uploader"
cp /home/jenkins/scripts/dev/checkstyleUpload.py $WORKDIR/checkstyleUpload.py

# echo "    [Data Miner] Executing checkstyle uploader"
python3 checkstyleUpload.py ./

##################################
# FindBugs uploading.            #
##################################

# echo "    [Data Miner] Acquiring FindBugs uploader"
cp /home/jenkins/scripts/dev/findbugsUpload.py $WORKDIR/findbugsUpload.py

# echo "    [Data Miner] Executing FindBugs uploader"
python3 findbugsUpload.py ./

##################################
# PMD uploading.                 #
##################################

# echo "    [Data Miner] Acquiring PMD uploader"
cp /home/jenkins/scripts/dev/pmdUpload.py $WORKDIR/pmdUpload.py

# echo "    [Data Miner] Executing PMD uploader"
python3 pmdUpload.py ./

##################################
# [Next Step in data process]    #
##################################

# echo "    [Data Miner] Test Results uploader fails; needs review."

# echo "    [Data Miner] Acquiring Test Results uploader"
cp /home/jenkins/scripts/dev/testFileResultsUpload.py $WORKDIR/testFileResultsUpload.py

# echo "    [Data Miner] Executing Test Results uploader"
python3 testFileResultsUpload.py ./

##################################
# [Next Step in data process]    #
##################################

 # some code goes here.

##################################
# Cleaning up the local dir.     #
##################################

echo "    [Data Miner] Cleaning up."
rm -f *.sh *.py *.txt

echo "    [Data Miner] Mining complete."
cd ..

echo ""

#echo $BUILD_NUMBER
#this just works, fwiw
