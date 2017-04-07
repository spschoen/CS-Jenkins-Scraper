#!/bin/bash
#RZandSSwereHere2017

echo ""

echo "Data Miner:"

if [ $# -ne 1 ] || [ ! -d "$1" ]; then
    echo "ERROR: ARGUMENT IS NOT DIRECTORY/DOES NOT EXIST.  EXITING"
    exit 5
fi

DIRECTORY="$1"

# TODO: Make this work without logging in.  Probably easier than I think.
# cd /home/jenkins/scripts/
# git pull
# cd $WORKSPACE/$PROJECT_NAME

echo "    [Data Miner] Beginning mining."
cd $WORKSPACE/$PROJECT_NAME

##################################
# Getting Project ID for CUID    #
##################################

# echo "    [Data Miner] Acquiring ProjectID scanner"
cp "$DIRECTORY"/splitter.sh $WORKSPACE/$PROJECT_NAME/splitter.sh

# echo "    [Data Miner] Getting Project ID"
PROJECT_ID=$(bash splitter.sh $GIT_URL)

##################################
# Grabbing the library.          #
##################################

# echo "    [Data Miner] Pulling library functions."
cp "$DIRECTORY"/MySQL_Func.py $WORKSPACE/$PROJECT_NAME/MySQL_Func.py

##################################
# Scanning for methods           #
##################################

# echo "    [Data Miner] Acquiring method scanner"
cp "$DIRECTORY"/methodScan.sh $WORKSPACE/$PROJECT_NAME/methodScan.sh

# echo "    [Data Miner] Executing method scanner script"
sh $WORKSPACE/$PROJECT_NAME/methodScan.sh $WORKSPACE/$PROJECT_NAME/ > $WORKSPACE/$PROJECT_NAME/methods.txt

# echo "    [Data Miner] Acquiring method uploader"
cp "$DIRECTORY"/methodScanner.py $WORKSPACE/$PROJECT_NAME/methodScanner.py

# echo "    [Data Miner] Executing method uploader"
python3 methodScanner.py

##################################
# Scanning for tests             #
##################################

# echo "    [Data Miner] Acquiring test scanner"
cp "$DIRECTORY"/testScan.sh $WORKSPACE/$PROJECT_NAME/testScan.sh

# echo "    [Data Miner] Executing test scanner script"
sh $WORKSPACE/$PROJECT_NAME/testScan.sh $WORKSPACE/$PROJECT_NAME/ > $WORKSPACE/$PROJECT_NAME/tests.txt

# echo "    [Data Miner] Acquiring test uploader"
cp "$DIRECTORY"/testScanner.py $WORKSPACE/$PROJECT_NAME/testScanner.py

# echo "    [Data Miner] Executing test uploader"
python3 testScanner.py

##################################
# Uploading Commit Information.  #
##################################

# echo "    [Data Miner] Acquiring commit information uploader"
cp "$DIRECTORY"/commitUpload.py $WORKSPACE/$PROJECT_NAME/commitUpload.py

# echo "    [Data Miner] Executing commit information uploader"
python3 commitUpload.py $WORKSPACE $PROJECT_ID $GIT_COMMIT $BUILD_NUMBER

##################################
# Checkstyle uploading.          #
##################################

# echo "    [Data Miner] Acquiring checkstyle uploader"
cp "$DIRECTORY"/checkstyleUpload.py $WORKSPACE/$PROJECT_NAME/checkstyleUpload.py

# echo "    [Data Miner] Executing checkstyle uploader"
python3 checkstyleUpload.py ./ $PROJECT_ID $GIT_COMMIT

##################################
# FindBugs uploading.            #
##################################

# echo "    [Data Miner] Acquiring FindBugs uploader"
cp "$DIRECTORY"/findbugsUpload.py $WORKSPACE/$PROJECT_NAME/findbugsUpload.py

# echo "    [Data Miner] Executing FindBugs uploader"
python3 findbugsUpload.py ./ $PROJECT_ID $GIT_COMMIT

##################################
# PMD uploading.                 #
##################################

# echo "    [Data Miner] Acquiring PMD uploader"
cp "$DIRECTORY"/pmdUpload.py $WORKSPACE/$PROJECT_NAME/pmdUpload.py

# echo "    [Data Miner] Executing PMD uploader"
python3 pmdUpload.py ./ $PROJECT_ID $GIT_COMMIT

##################################
# Test Results uploading.        #
##################################

# echo "    [Data Miner] Acquiring Test Results uploader"
cp "$DIRECTORY"/testFileResultsUpload.py $WORKSPACE/$PROJECT_NAME/testFileResultsUpload.py

# echo "    [Data Miner] Executing Test Results uploader"
python3 testFileResultsUpload.py $WORKSPACE/$PROJECT_NAME $PROJECT_ID $GIT_COMMIT

##################################
# TS Test Results uploading.     #
##################################

# echo "    [Data Miner] Acquiring TS Test Results uploader"
cp "$DIRECTORY"/TSTestFileResultsUpload.py $WORKSPACE/$PROJECT_NAME/TSTestFileResultsUpload.py

# echo "    [Data Miner] Executing TS Test Results uploader"
python3 TSTestFileResultsUpload.py $WORKSPACE/$PROJECT_NAME $PROJECT_ID $GIT_COMMIT

##################################
# Coverage uploading.            #
##################################

# echo "    [Data Miner] Acquiring Coverage uploader"
cp "$DIRECTORY"/coverageUpload.py $WORKSPACE/$PROJECT_NAME/coverageUpload.py

# echo "    [Data Miner] Executing Coverage uploader"
python3 coverageUpload.py $WORKSPACE/$PROJECT_NAME $PROJECT_ID $GIT_COMMIT

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
