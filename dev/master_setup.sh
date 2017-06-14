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

START_DIR="$(pwd)"
MySQL_URL="http://dev.mysql.com/get/Downloads/MySQL-5.6"

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
yum -y -q update
if [ "$?" -ne 0 ]; then
	warning "Yum update resulted in non-zero exit status.  Continue? (y/n) "
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

MYSQL_LIST="$(sudo yum list | grep MySQL- | grep .x86_64)"
MYSQL_COUNT="$(echo "$MYSQL_LIST" | wc -l)"

if [ "$MYSQL_COUNT" -ne "4" ]; then
    warning "MySQL is not installed, running installation steps."

    # Downloading the MySQL Files for upgrade
    info "Checking for & downloading MySQL 5.6 files."
    if [ ! -f "$START_DIR/MySQL-shared-5.6.10-1.rpm" ]; then
        warning "Could not find MySQL Shared file, downloading as MySQL-shared-5.6.10-1.rpm"
        wget -q -O "MySQL-shared-5.6.10-1.rpm" "$MySQL_URL/MySQL-shared-5.6.10-1.el6.x86_64.rpm/"
    fi
    if [ ! -f "$START_DIR/MySQL-client-5.6.10-1.rpm" ]; then
        warning "Could not find MySQL Client file, downloading as MySQL-client-5.6.10-1.rpm"
        wget -q -O "MySQL-client-5.6.10-1.rpm" "$MySQL_URL/MySQL-client-5.6.10-1.el6.x86_64.rpm/"
    fi
    if [ ! -f "$START_DIR/MySQL-server-5.6.10-1.rpm" ]; then
        warning "Could not find MySQL Server file, downloading as MySQL-server-5.6.10-1.rpm"
        wget -q -O "MySQL-server-5.6.10-1.rpm" "$MySQL_URL/MySQL-server-5.6.10-1.el6.x86_64.rpm/"
    fi

    # Installing new MySQL
    info "Installing MySQL 5.6"
    rpm -ivh "MySQL-shared-5.6.10-1.rpm"
    rpm -ivh "MySQL-client-5.6.10-1.rpm"
    rpm -ivh "MySQL-server-5.6.10-1.rpm"
    info "Installation complete."
    
    # Downloading the MySQL Files for upgrade
    info "Removing MySQL install files."
    if [ -f "$START_DIR/MySQL-shared-5.6.10-1.rpm" ]; then
        rm -f "MySQL-shared-5.6.10-1.rpm"
    fi
    if [ ! -f "$START_DIR/MySQL-client-5.6.10-1.rpm" ]; then
        rm -f "MySQL-client-5.6.10-1.rpm"
    fi
    if [ ! -f "$START_DIR/MySQL-server-5.6.10-1.rpm" ]; then
        rm -f "MySQL-server-5.6.10-1.rpm"
    fi

    # Fixing permissions, starting MySQL
    info "Fixing permissions of MySQL directory in /var/lib/"
    chown -R mysql:mysql /var/lib/mysql
    
    info "Starting MySQL service."
    service mysql start

    # Getting root pw, and config options
    info "Reading generated rood password from installation."
    SECRET_FILE="$(head -n1 /root/.mysql_secret)"
    MYSQL_PASS=${SECRET_FILE##* }

    echo -n "New MySQL Root PW: "
    read NEW_PASS
    
    info "Changing MySQL root password"
    mysql -u root -p$MYSQL_PASS -e "SET PASSWORD FOR 'root'@'localhost' = PASSWORD('$NEW_PASS');"

else
    echo -n "MySQL root pass: "
    read NEW_PASS
fi

echo -n "New database Name: "
read DATABASE

echo -n "New Miner User Pass: "
read USER_PASS

exit

info "Creating MySQL Table, and importing settings from ../docs/base.sql"
mysql -u root -p$NEW_PASS -e "CREATE TABLE $DATABASE"
mysql -u root -p$NEW_PASS $DATABASE < ../docs/base.sql

for i in $*; do
    mysql -u root -p$NEW_PASS -e "CREATE USER 'miner'@'$i' identified by '$USER_PASS';"
    mysql -u root -p$NEW_PASS -e "GRANT INSERT, UPDATE, SELECT on $DATABASE.* to 'miner'@'$i';"
done
