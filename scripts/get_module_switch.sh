#!/bin/bash

# On some platforms, a module switch is required for compilation.
# If that is necessary, this script prints it. Otherwise prints nothing.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [[ "$(bash ${SCRIPT_DIR}/is_platform_xc40.sh )" = "true" ]] ; then
		echo "module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ; "
else
		echo ""
fi
