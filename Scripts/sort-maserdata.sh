#!/usr/bin/env bash
#
# to be run as a cron at midnight
# just like portstuff but for the state of health data files
#

echo $(date +%j.%H.%M)
echo "cleaning up the maser data files"

YEAR=$(date -d yesterday +%Y)
DOY=$(date -d yesterday +%j)

# yesterday, this year
echo "check: $DOY, $YEAR"

for MSR in "NR" "T4"; do

    DIRECTORY="$HOME/Data/MaserData/${MSR}/"
    NEWFOLDER="${YEAR}/"

    if [[ ! -e "$DIRECTORY$NEWFOLDER" ]]; then
        mkdir $DIRECTORY$NEWFOLDER
        echo "made directory $DIRECTORY$NEWFOLDER"
    fi

    FILE="MaserData-${MSR}-${DOY}.txt"

    mv $DIRECTORY$FILE $DIRECTORY$NEWFOLDER$FILE
done

echo "moved yesterdays data into yearly folder"
