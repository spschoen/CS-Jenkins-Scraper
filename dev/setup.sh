#!/bin/bash

# Use the below if needed.

readonly LOG_FILE="$(pwd)/$(basename "$0")_$(date +%s).log"
info()    { echo "[INFO]    $@" | tee -a "$LOG_FILE" >&2 ; }
warning() { echo "[WARNING] $@" | tee -a "$LOG_FILE" >&2 ; }
error()   { echo "[ERROR]   $@" | tee -a "$LOG_FILE" >&2 ; }
fatal()   { echo "[FATAL]   $@" | tee -a "$LOG_FILE" >&2 ; exit 1 ; }

# This script NEEDS to be executed with sudo or else it won't do any work.
if [ "$EUID" -ne 0 ]; then
	fatal "Please run as root"
fi

#Update yum, because our versions are ancient.
info "Updating Yum"
update yum
info "$?"

#Install python3 because that's what the scripts run off.
yum install python34.x86_64

#Install the "count lines of code" utility for analysis.
yum install cloc

#Install gitstats utility for additional metrics
yum install gitstats

#Install the two Python Modules we use.
pip3 install PyMySQL
pip3 install GitPython

#Making sure GitPython will eventually work.
export "PATH=$PATH:/usr/local/git/bin/"
