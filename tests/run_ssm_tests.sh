#!/bin/bash

USAGE="Run automated tests on an installed maestro SSM package.

Usage:
    ./run_ssm_tests.sh [<path-to-installed-ssm>]

Options:
    <path-to-installed-ssm>     This is the SSM that will be tested. If no path is given, the project will be compiled, built into an SSM, installed, and then that will be tested.
"

if [[ $(which maestro) ]] ; then
    echo "Aborted. You need to run the maestro unit tests in a clean environment that does not have maestro. Perhaps in your profile there is a ssmuse maestro line. The path to maestro found in your environment is:
    
    $(which maestro)
    "
    exit 1
fi

SSM_DOMAIN_PATH=$1

set -eu

PROJECT_PATH=$(git rev-parse --show-toplevel)
VERSION=unittest
PROJECT_NAME=$(basename $PROJECT_PATH)

if [[ -z $SSM_DOMAIN_PATH ]]; then
    echo "No SSM path provided. Therefore, building and installing a temporary SSM as the test target."

    SSM_ROOT=$HOME/tmp/ssm
    INSTALLED_MAESTRO_PATH=$SSM_ROOT/$PROJECT_NAME
    SSM_DOMAIN_PATH=$INSTALLED_MAESTRO_PATH/$VERSION
    
    rm -rf $SSM_ROOT
    mkdir -p $INSTALLED_MAESTRO_PATH
    
    cd ${PROJECT_PATH}
    make VERSION=$VERSION
    
    ssm/install_ssm.sh $VERSION --ssm-root=$SSM_ROOT
fi

if [[ ! -d $SSM_DOMAIN_PATH ]]; then
    echo "
    
$USAGE

Aborted. SSM domain path does not exist."
    exit 1
fi

echo "
RUNNING PYTHON TESTS
"

export SSM_DOMAIN_PATH
cd ${PROJECT_PATH}/tests/src
./run_ssm_tests.py
