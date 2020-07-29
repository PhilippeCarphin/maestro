#!/bin/bash

PYTHON_FOLDER=$(dirname $(dirname $(realpath $0)))
VENV=$PYTHON_FOLDER/venv
AUTOPEP8=$VENV/bin/autopep8
echo "Running autopep8 on Python scripts in:
    $PYTHON_FOLDER"
find $PYTHON_FOLDER -name "*.py" -exec $AUTOPEP8 {} -i --max-line-length 200 \;
echo "Done."
