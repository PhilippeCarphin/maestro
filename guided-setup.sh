#!/bin/bash

# Run this script for a guided configuration, build, and ssm install of the Maestro suite from source.

MAESTRO_ROOT=$PWD

# Check if compiling tcl is necessary.
TCL_SSMS="tcl-tk_8.5.11_sles-11-amd64-64.ssm tcl-tk_8.5.11_ubuntu-14.04-amd64-64.ssm"
MISSING_TCL=
for tcl_ssm in $TCL_SSMS ; do
    tcl_path=ssm/$tcl_ssm
    if [ ! -f $tcl_path ]; then
         MISSING_TCL="${MISSING_TCL} ${PWD}/${tcl_path}"
    fi
done

if [ -z "$MISSING_TCL" ]; then
    echo "Skipping tcl compile. Using ssm files instead."
else
    echo "Missing tcl files:"
    for tcl in $MISSING_TCL ; do
         echo "     $tcl"
    done
    echo "You can save some time if you find these files first and put them there to avoid compiling tcl from source."
    echo "Compile tcl from source? This may take awhile. [yn]: "
    read yn
    if ! [[ "$yn" =~ [yY] ]]; then
         echo "Aborted."
         exit 1
    fi
fi


set -e

cd $MAESTRO_ROOT/xflow/ssm
make clean
make

cd $MAESTRO_ROOT/maestro-utils/ssm
make clean
make

cd $MAESTRO_ROOT/maestro-manager/ssm
make clean
make

if [ -z "${MISSING_TCL}" ]; then
    cd $MAESTRO_ROOT/maestro-tcl/ssm
    make clean
    make
fi

cd $MAESTRO_ROOT/maestro-core
make clean
make

cd $MAESTRO_ROOT
./setup/hare-compile.sh
./setup/soft-link-ssm.sh
./setup/install-and-publish-ssm.sh $HOME/ssm/maestro/1.5.1 1.5.1

echo "Success!"
