#!/bin/bash

# Some older platforms do not have realpath, they use a substitute instead.
REALPATH=realpath
if [[ -z $(which $REALPATH) ]] ; then
	REALPATH="true_path -n"
fi
if [[ -z $(which $REALPATH) ]] ; then
	echo "Setup requires 'realpath' or 'true_path' but failed to find either. Aborted."
	exit 1
fi

MAESTRO_ROOT=$($REALPATH $(dirname $(dirname $(dirname $(dirname $($REALPATH $0))))))
set -u

VENV=$MAESTRO_ROOT/venv
echo "Setting up the Python virtual environment:
    $VENV"
if [ ! -d $VENV ] ; then
    virtualenv -p python3 $VENV || python3 -m venv $VENV
fi
$VENV/bin/pip3 install --upgrade pip
$VENV/bin/pip3 install -r $MAESTRO_ROOT/setup/requirements.txt

echo "

Done."

