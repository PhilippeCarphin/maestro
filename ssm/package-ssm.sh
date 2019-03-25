#!/bin/bash

# This script is run after the compilation to create an ssm package for each folder found in the builds folder.

set -eu

PROJECT_PATH=$(git rev-parse --show-toplevel)
BUILD_FOLDER=${PROJECT_PATH}/build
SSM_FOLDER=${PROJECT_PATH}/ssm

mkdir -p ${PROJECT_PATH}/ssm
rm -f ${PROJECT_PATH}/ssm/*.ssm

packages=$(ls ${BUILD_FOLDER})
for package in $packages ; do
    cp -r ${SSM_FOLDER}/.ssm.d ${BUILD_FOLDER}/$package/
    
    . ${SSM_FOLDER}/create_ssm_control_files.sh ${BUILD_PLATFORM_FOLDER}/.ssm.d

    tar -zcvf ssm/${package}.ssm -C build ${package}/man ${package}/bin ${package}/src/core ${package}/src/utilities ${package}/src/xflow ${package}/src/xm ${package}/src/tcl ${package}/.ssm.d
done

echo
echo "Created SSM packages: '$packages'"
