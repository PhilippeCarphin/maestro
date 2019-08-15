#!/bin/bash

# This script is run after the compilation to create an ssm package for each folder found in the builds folder.
# Usage:
#     package-ssm.sh <version>

set -exu

VERSION=$1
PROJECT_PATH=$(git rev-parse --show-toplevel)
BUILD_FOLDER=${PROJECT_PATH}/build
SSM_FOLDER=${PROJECT_PATH}/ssm
HAS_INTERNET=$($PROJECT_PATH/scripts/has_internet.sh)

mkdir -p ${PROJECT_PATH}/ssm
rm -f ${PROJECT_PATH}/ssm/*.ssm

packages=$(ls ${BUILD_FOLDER})
for package in $packages ; do
    cp -r ${SSM_FOLDER}/.ssm.d ${BUILD_FOLDER}/$package/
    
    . ${SSM_FOLDER}/create_ssm_control_files.sh ${VERSION} ${BUILD_PLATFORM_FOLDER}/.ssm.d

    # In some cases the man pages cannot be built. If so, do not include 'man' in the tar command.
    MAN_FOLDER=
    if [[ -d ${BUILD_FOLDER}/${package}/man ]]; then
	    MAN_FOLDER="${package}/man"
    fi

    tar -zcf ssm/${package}.ssm -C build $MAN_FOLDER ${package}/bin ${package}/src/core ${package}/src/utilities ${package}/src/xflow ${package}/src/xm ${package}/src/tcl ${package}/.ssm.d
done

echo
echo "Created SSM packages: '$packages'"
