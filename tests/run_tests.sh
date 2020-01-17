#!/bin/bash

set -eu

PROJECT_PATH=$(git rev-parse --show-toplevel)
VERSION=unittest
PROJECT_NAME=$(basename $PROJECT_PATH)

SSM_ROOT=$HOME/tmp/ssm
INSTALLED_MAESTRO_PATH=$SSM_ROOT/$PROJECT_NAME
SSM_DOMAIN_PATH=$INSTALLED_MAESTRO_PATH/$VERSION

rm -rf $SSM_ROOT
mkdir -p $INSTALLED_MAESTRO_PATH

cd ${PROJECT_PATH}
make VERSION=$VERSION

./reinstall-ssm.sh $VERSION $SSM_ROOT

echo "
RUNNING PYTHON TESTS
"

cd ${PROJECT_PATH}/tests
./run_python_tests.py
