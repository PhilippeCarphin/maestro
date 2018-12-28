#!/bin/bash

# Prints 'true' if we are likely on IBM cray architecture.
# Prints 'false' otherwise.
# This script is essentially a re-usable function for the makefile, so that this check is easily changed or removed in the future.

if [[ "$(lsb_release -a)" = *"SUSE LINUX"* ]] ; then 
		echo "true"
		exit 0
else
		echo "false"
fi
