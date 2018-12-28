#!/bin/bash

# Prints 'true' if we are likely on IBM cray architecture.
# Prints 'false' otherwise.
# This script exists as an easy way to perform an identical check many times in the convoluted build process.

if [[ "$(lsb_release -a)" = *"SUSE LINUX"* ]] ; then 
		echo "true"
		exit 0
else
		echo "false"
fi
