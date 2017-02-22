#!/bin/bash
#RZandSSwhereHere2017

echo "Data Miner:"

echo "    [Data Miner] Moving into $WORKDIR"
cd $WORKDIR

##################################
# Scanning for methods           #
##################################

echo "    [Data Miner] Copying method scanner into $WORKDIR"
cp /home/jenkins/scripts/dev/methodScan.sh $WORKDIR/methodScan.sh

echo "    [Data Miner] Executing method scanner script"
sh $WORKDIR/methodScan.sh $WORKDIR/ > $WORKDIR/methods.txt

echo "    [Data Miner] Copying method uploader into $WORKDIR"
cp /home/jenkins/scripts/dev/methodScanner.py $WORKDIR/methodScanner.py

echo "    [Data Miner] Executing method uploader"
python3 methodScanner.py

##################################
# Scanning for tests             #
##################################

echo "    [Data Miner] Copying test scanner into $WORKDIR"
cp /home/jenkins/scripts/dev/testScan.sh $WORKDIR/testScan.sh

echo "    [Data Miner] Executing test scanner script"
sh $WORKDIR/testScan.sh $WORKDIR/ > $WORKDIR/tests.txt

echo "    [Data Miner] Copying test uploader into $WORKDIR"
cp /home/jenkins/scripts/dev/testScanner.py $WORKDIR/testScanner.py

echo "    [Data Miner] Executing test uploader"
python3 testScanner.py

##################################
# Checkstyle uploading.          #
##################################

echo "    [Data Miner] Copying checkstyle uploader into $WORKDIR"
cp /home/jenkins/scripts/dev/checkstyleUpload.py $WORKDIR/checkstyleUpload.py

echo "    [Data Miner] Executing checkstyle uploader"
python3 checkstyleUpload.py ./

##################################
# FindBugs uploading.            #
##################################

echo "    [Data Miner] Copying FindBugs uploader into $WORKDIR"
cp /home/jenkins/scripts/dev/findbugsUpload.py $WORKDIR/findbugsUpload.py

echo "    [Data Miner] Executing FindBugs uploader"
python3 findbugsUpload.py ./

##################################
# PMD uploading.                 #
##################################

echo "    [Data Miner] Copying PMD uploader into $WORKDIR"
cp /home/jenkins/scripts/dev/pmdUpload.py $WORKDIR/pmdUpload.py

echo "    [Data Miner] Executing PMD uploader"
python3 pmdUpload.py ./

##################################
# [Next Step in data process]    #
##################################

echo "    [Data Miner] Test Results uploader fails; needs review."

echo "    [Data Miner] Copying Test Results uploader into $WORKDIR"
#cp /home/jenkins/scripts/dev/testFileResultsUpload.py $WORKDIR/testFileResultsUpload.py

echo "    [Data Miner] Executing Test Results uploader"
#python3 testFileResultsUpload.py ./

##################################
# [Next Step in data process]    #
##################################

 # some code goes here.

##################################
# Cleaning up the local dir.     #
##################################

echo "    [Data Miner] Cleaning up."
rm -f *.sh *.py *.txt

echo "    [Data Miner] Returning to parent directory."
cd ..

#echo $BUILD_NUMBER
#this just works, fwiw