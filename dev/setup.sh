#!/bin/bash

# This script NEEDS to be executed with sudo or else it won't do any work.

#Update yum, because our versions are ancient.
update yum

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
