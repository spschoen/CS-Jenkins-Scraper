#!/bin/bash

# example URL: git@github.ncsu.edu:spschoen/csc216-002-P2-096.git

if [ $# -ne 1 ]; then
    echo "Expected 1 argument, got $#."
    exit 1
fi

# Split the GIT_URL on / and take last element.
loc=${1##*/}

# git@github.ncsu.edu:spschoen/csc216-002-P2-096.git > csc216-002-P2-096.git

loc=${loc%.*}

# csc216-002-P2-096.git > csc216-002-P2-096

loc=${loc#*-}
loc=${loc#*-}

# csc216-002-P2-096 > 002-P2-096
# 002-P2-096 > P2-096

# echo the final string to stdout, to be captured in runScript.
echo $loc
