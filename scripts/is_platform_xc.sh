#!/bin/bash

# Prints 'xc40' or 'xc50' if we are on IBM cray architecture.
# Otherwise, prints nothing.
# This script is essentially a re-usable function for the makefile, so that this check is easily changed or removed in the future.

if [[ $ORDENV_PLAT == *"xc40" ]] ; then
	echo "xc40"
	exit 0
fi

if [[ $ORDENV_PLAT == *"xc50" ]] ; then
	echo "xc50"
	exit 0
fi
