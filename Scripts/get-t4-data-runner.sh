#!/usr/bin/env bash
#
# to be run as a cron, twice a day
# activate the venv environment
# run the request & receiver
# deactivate the venv
# gahh

echo "###########################################"
echo $(date +%j.%H.%M)
echo "activating"
source $HOME/esl/DataDump/.venv/bin/activate
echo "running"
python3 $HOME/esl/DataDump/GetT4StateOfHealth.py
echo "deactivating"
deactivate
echo "###########################################"