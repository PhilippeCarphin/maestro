#!/bin/bash

MAESTRO_ROOT=$(realpath $(dirname $(dirname $(realpath $0))))
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

