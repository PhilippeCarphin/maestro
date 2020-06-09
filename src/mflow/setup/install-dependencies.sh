#!/bin/bash

PROJECT_ROOT=$(git rev-parse --show-toplevel)
set -u

# setup the Python virtual environment
VENV=$PROJECT_ROOT/venv
if [ ! -d $VENV ] ; then
    virtualenv -p python3 $VENV || python3 -m venv $VENV
fi
$VENV/bin/pip3 install --upgrade pip
$VENV/bin/pip3 install -r $PROJECT_ROOT/setup/requirements.txt

echo "

Done."

