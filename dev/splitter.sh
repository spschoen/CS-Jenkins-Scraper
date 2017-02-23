#!/bin/bash

# example URL: git@github.ncsu.edu:spschoen/csc216-002-P2-096.git

if [ $# -ne 1 ]; then
    echo "Expected 1 argument, got $#."
    exit 1
fi

# Split the GIT_URL on / and take last element.
loc=${1##*/}

# git@github.ncsu.edu:spschoen/csc216-002-P2-096.git > csc216-002-P2-096.git

# Get the 6 chars at offset 11.
loc=${loc:11:6}

# csc216-002-|P2-096|.git

# echo the final string to stdout, to be captured in runScript.
echo $loc
