#!/bin/bash
#RZandSSwereHere2017

echo ""

echo "Data Miner:"

while [ "$#" -gt 0 ]; do
    case "$1" in
        -p) DIRECTORY="$2"; shift 2;;
        -d) DEBUG="y"; shift 1;;

        --path) DIRECTORY="$2"; shift 2;;
        --debug) DEBUG="y"; shift 1;;

        -*) echo "unknown option: $1" >&2; exit 1;;
        *) echo "unrecognized argument: $1"; exit 0
    esac
done

if [[ "$DEBUG" == "y" ]]; then
	echo "    [Data Miner] Debug output enabled."
fi

if [[ "$DIRECTORY" == "" ]]; then
	echo "    [Data Miner] Did not specify directory for scripts; exiting."
	exit 0
fi

echo "    [Data Miner] Beginning mining."
cd "$WORKSPACE"/"$PROJECT_NAME"

#####################################
# Getting Project ID for commit_uid #
#####################################

if [[ "$DEBUG" == "y" ]]; then
	echo "    [Data Miner] Acquiring ProjectID scanner"
fi
cp "$DIRECTORY"/splitter.sh "$WORKSPACE"/"$PROJECT_NAME"/splitter.sh

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Getting Project ID"
fi
PROJECT_ID=$(bash splitter.sh $GIT_URL)

##################################
# Grabbing the library.          #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Pulling library functions."
fi
cp "$DIRECTORY"/Scraper.py "$WORKSPACE"/"$PROJECT_NAME"/Scraper.py

##################################
# Scanning for methods           #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring method scanner"
fi
cp "$DIRECTORY"/methodScan.sh "$WORKSPACE"/"$PROJECT_NAME"/methodScan.sh

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing method scanner script"
fi
sh "$WORKSPACE"/"$PROJECT_NAME"/methodScan.sh "$WORKSPACE"/"$PROJECT_NAME"/ > "$WORKSPACE"/"$PROJECT_NAME"/methods.txt

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring method uploader"
fi
cp "$DIRECTORY"/methodScanner.py "$WORKSPACE"/"$PROJECT_NAME"/methodScanner.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing method uploader"
fi
python3 methodScanner.py

##################################
# Scanning for tests             #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring test scanner"
fi
cp "$DIRECTORY"/testScan.sh "$WORKSPACE"/"$PROJECT_NAME"/testScan.sh

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing test scanner script"
fi
sh "$WORKSPACE"/"$PROJECT_NAME"/testScan.sh "$WORKSPACE"/"$PROJECT_NAME"/ > "$WORKSPACE"/"$PROJECT_NAME"/tests.txt

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring test uploader"
fi
cp "$DIRECTORY"/testScanner.py "$WORKSPACE"/"$PROJECT_NAME"/testScanner.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing test uploader"
fi
python3 testScanner.py

##################################
# Uploading Commit Information.  #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring commit information uploader"
fi
cp "$DIRECTORY"/commitUpload.py "$WORKSPACE"/"$PROJECT_NAME"/commitUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing commit information uploader"
fi
python3 commitUpload.py "$WORKSPACE" "$PROJECT_ID" "$GIT_COMMIT" "$BUILD_NUMBER" "$PROJECT_NAME"

##################################
# Checkstyle uploading.          #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring checkstyle uploader"
fi
cp "$DIRECTORY"/checkstyleUpload.py "$WORKSPACE"/"$PROJECT_NAME"/checkstyleUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing checkstyle uploader"
fi
python3 checkstyleUpload.py "$WORKSPACE"/"$PROJECT_NAME" "$PROJECT_ID" "$GIT_COMMIT"

##################################
# FindBugs uploading.            #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring FindBugs uploader"
fi
cp "$DIRECTORY"/findbugsUpload.py "$WORKSPACE"/"$PROJECT_NAME"/findbugsUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing FindBugs uploader"
fi
python3 findbugsUpload.py "$WORKSPACE"/"$PROJECT_NAME" "$PROJECT_ID" "$GIT_COMMIT"

##################################
# PMD uploading.                 #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring PMD uploader"
fi
cp "$DIRECTORY"/pmdUpload.py "$WORKSPACE"/"$PROJECT_NAME"/pmdUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing PMD uploader"
fi
python3 pmdUpload.py "$WORKSPACE"/"$PROJECT_NAME" "$PROJECT_ID" "$GIT_COMMIT"

##################################
# Test Results uploading.        #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring Test Results uploader"
fi
cp "$DIRECTORY"/testFileResultsUpload.py "$WORKSPACE"/"$PROJECT_NAME"/testFileResultsUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing Test Results uploader"
fi
python3 testFileResultsUpload.py "$WORKSPACE"/"$PROJECT_NAME" "$PROJECT_ID" "$GIT_COMMIT" "$PROJECT_NAME"

##################################
# TS Test Results uploading.     #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring TS Test Results uploader"
fi
cp "$DIRECTORY"/TSTestFileResultsUpload.py "$WORKSPACE"/"$PROJECT_NAME"/TSTestFileResultsUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing TS Test Results uploader"
fi
python3 TSTestFileResultsUpload.py "$WORKSPACE"/"$PROJECT_NAME" "$PROJECT_ID" "$GIT_COMMIT" "$PROJECT_NAME"

##################################
# Coverage uploading.            #
##################################

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Acquiring Coverage uploader"
fi
cp "$DIRECTORY"/coverageUpload.py "$WORKSPACE"/"$PROJECT_NAME"/coverageUpload.py

if [[ "$DEBUG" == "y" ]]; then
    echo "    [Data Miner] Executing Coverage uploader"
fi
python3 coverageUpload.py "$WORKSPACE"/"$PROJECT_NAME"/site/jacoco "$PROJECT_ID" "$GIT_COMMIT"

##################################
# Cleaning up the local dir.     #
##################################

echo "    [Data Miner] Cleaning up."
if [[ "$DEBUG" == "y" ]]; then
	echo "    [Data Miner] Removing *.sh, *.py, and *.txt"
fi
rm -f *.sh *.py *.txt

echo "    [Data Miner] Mining complete."
cd ..

echo ""
