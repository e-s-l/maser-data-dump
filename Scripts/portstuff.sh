#!/usr/bin/env bash
#
# to be run as a cron at midnight
#
# why the heck is this called port stuff
#
# i am assuming that the logs autorestart...
# the files for the other ports are empty
# and are auto-deleted when the tic logging stops
#


echo $(date +%j.%H.%M)
echo "cleaning up the gps data files, copying into yearly folders"

YEAR=$(date -d yesterday +%Y)
DOY=$(date -d yesterday +%j)

echo "check: $DOY, $YEAR"

DIRECTORY="$HOME/Data/GPSTime/"
NEWFOLDER="TAC${YEAR}"

if [[ ! -e "$DIRECTORY$NEWFOLDER" ]]; then
	mkdir $DIRECTORY$NEWFOLDER
	echo "made directory $DIRECTORY$NEWFOLDER"
fi

for X in "A" "T"; do
	FILE="NR_${YEAR}_${DOY}${X}_PORT_01.csv"
	mv $DIRECTORY$FILE $DIRECTORY$NEWFOLDER/$FILE
done

# the C txt file:

FILE="NR_${YEAR}_${DOY}C.txt"
mv $DIRECTORY$FILE $DIRECTORY$NEWFOLDER/$FILE

#
echo "ok, 'portstuff' complete"



