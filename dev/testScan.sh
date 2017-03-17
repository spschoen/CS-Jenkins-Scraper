#!/bin/bash

function dirScan {
    cd "$1"
    #echo "Dir: $1"
    for D in *; do
        if [ -d "${D}" ]; then
            echo "dir ${D}"
            dirScan "${D}"
        else
            if [[ "${D}" == *.java ]]; then
                less "${D}" | egrep -o '(publ|priv|prot).*' | egrep -v "\*|;|interface"
                echo ""
            fi
        fi
    done
    cd ..
}

#Don't forget to change directory to wherever we are.
cd "$(dirname "$0")"

#Check if user supplied arguments
if [ $# -ne 1 ]; then
    echo "ERR: Not given expected arguments.."
    echo "Expected [directory of directories interact with]"
    echo "Exiting program with status 0."
    exit 0
fi

if [ ! -d $1 ]; then
    echo "ERR: Argument 1 is not a directory, or directory does not exist."
    echo "Exiting program with status 0."
    exit 0
fi

#Saving directory.
DIRECTORY="$1"

#dirScan $DIRECTORY
for D in $DIRECTORY/*; do
    if [ -d "${D}" ] && [[ "${D}" == "test" ]]; then
        echo "dir ${D}"
        dirScan "${D}"
    fi
done
