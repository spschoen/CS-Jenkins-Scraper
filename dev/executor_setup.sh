#!/bin/bash

# Use the below if needed.

readonly LOG_FILE="$(pwd)/$(basename "$0")_$(date +%s).log"
info()    { echo "[INFO]    $@" | tee -a "$LOG_FILE" >&2 ; }
warning() { echo "[WARNING] $@" | tee -a "$LOG_FILE" >&2 ; }
error()   { echo "[ERROR]   $@" | tee -a "$LOG_FILE" >&2 ; }
fatal()   { echo "[FATAL]   $@" | tee -a "$LOG_FILE" >&2 ; exit 1 ; }

clear

if [ ! -d ~/log/ ]; then
    mkdir ~/log/
fi

info "Moving log files to ~/log/"
find . -name '*.log' -exec mv {} ~/log/ \;
sleep 1
info "Log files moved."

# This script NEEDS to be executed with sudo or else it won't do any work.
if [ "$EUID" -ne 0 ]; then
    fatal "Please run as root"
fi

#Update yum, because our versions are ancient.
info "Updating Yum"
yum -y update
if [ "$?" -ne 0 ]; then
    warning "Yum update resulted in non-zero exit status."
    echo -n "Continue? (y/n) "
    read yum_warning_choice
    if [[ "$yum_warning_choice" == "y" ]]; then
        info "Continuing execution of setup.sh"
    elif [[ "$yum_warning_choice" == "n" ]]; then
        fatal "Execution exiting."
        exit 1
    else
        fatal "Unknown answer, exiting."
        exit 2
    fi
fi

# Python34 Installation
if [[ "$(yum list installed python34.x86_64 >/dev/null 2>&1)" == 1 ]]; then
    info "Python34.x86_64 was not detected; installing."
    yum install python34.x86_64
else
    info "Python34.x86_64 was detected; moving to next step."
fi

# cloc Installation
if [[ "$(yum list installed cloc >/dev/null 2>&1)" == 1 ]]; then
    info "cloc was not detected; installing."
    yum install cloc
else
    info "cloc was detected; moving to next step."
fi

# gitstats Installation
if [[ "$(yum list installed gitstats >/dev/null 2>&1)" == 1 ]]; then
    info "gitstats was not detected; installing."
    pip3 install gitstats
else
    info "gitstats was detected; moving to next step."
fi

# gitstats Installation
if [[ "$(python -c "import PyMySQL" >/dev/null 2>&1)" == 1 ]]; then
    info "PyMySQL was not detected; installing."
    pip3 install PyMySQL
else
    info "PyMySQL was detected; moving to next step."
fi

info "Beginning config.json generation"
echo -n "DB IP   : "
read IP
echo -n "DB User : "
read user
echo -n "DB Pass : "
read pass
echo -n "Database: "
read db

echo "{" > config.json
echo "  \"ip\": \"$IP\"," >> config.json
echo "  \"username\": \"$user\"," >> config.json
echo "  \"password\": \"$pass\"," >> config.json
echo "  \"database\": \"$db\"," >> config.json
echo "}" >> config.json
