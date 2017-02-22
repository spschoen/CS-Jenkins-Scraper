#!/bin/bash

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
# [Next Step in data process]    #
##################################

 # some code goes here.

##################################
# [Next Step in data process]    #
##################################

echo "    [Data Miner] Cleaning up."
rm -f *.sh *.py *.txt

echo "    [Data Miner] Returning to parent directory."
cd ..

#echo $BUILD_NUMBER
#this just works, fwiw