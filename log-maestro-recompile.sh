#!/bin/bash

# This script deletes the Maestro project folders and ssm folders, clones, recompiles, and dumps compile output to a log.

FOLDER="logs"
FILENAME=$FOLDER/`date +%Y-%m-%d-%H:%M:%S`"-maestro-recompile.log"
mkdir -p $FOLDER

echo "Starting delete, clone, and recompile."
./restart-all-maestro.sh > $FILENAME 2>&1

if [ $? -eq 0 ]; then
		echo "Success. Line count of compile log is "`wc -l $FILENAME`
		echo
		echo "Wrote compile log to '$FILENAME'."
else
		echo "Compile failed."
		echo
		tail -n 10 $FILENAME
fi
