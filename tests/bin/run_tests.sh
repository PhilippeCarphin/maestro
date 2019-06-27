#!/bin/bash

echo "
RUNNING MAESTRO PYTHON TESTS
----------------------------------------------------------------------
"
cd ..
python -m unittest discover -v 

echo "
TESTS COMPLETED
"

