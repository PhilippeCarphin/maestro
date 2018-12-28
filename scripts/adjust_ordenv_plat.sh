#!/bin/bash

# This script prints the value of ORDENV_PLAT
# However on some platforms, an adjusted value is printed instead.

# find the full path which contains this script file, no matter where it is called from.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [[ "$(bash ${SCRIPT_DIR}/is_platform_xc40.sh )" = "true" ]] ; then
		echo "sles-11-amd64-64"
else
		echo $ORDENV_PLAT
fi
