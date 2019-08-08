#!/bin/bash

# Prints 'xc40' or 'xc50' if we are on IBM cray architecture.
# Otherwise, prints nothing.
# This script is essentially a re-usable function for the makefile, so that this check is easily changed or removed in the future.

# Note: we don't use ORDENV_PLAT because the result of this script may overwrite that in the build process.
lsb=$(lsb_release -a 2>/dev/null)
if [[ $lsb == *"SUSE Linux Enterprise Server 11"* ]] ; then
	echo "xc40"
	exit 0
fi

if [[ $lsb == *"SUSE Linux Enterprise Server 15"* ]] ; then
	echo "xc50"
	exit 0
fi
