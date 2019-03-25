#!/bin/bash

# 

set -eu

ORDENV_PLAT=$(${PWD}/scripts/adjust_ordenv_plat.sh)
VERSION=$(${PWD}scripts/get_repo_version.sh)
SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
BUILD_FOLDER=${PWD}/build
BUILD_PLATFORM_FOLDER=${BUILD_FOLDER}/${SSMPACKAGE}
SCRIPTS_FOLDER=${PWD}/scripts

	cp -r .ssm.d ${BUILD_PLATFORM_FOLDER}/

	
	cd ${BUILD_PLATFORM_FOLDER}/.ssm.d ; . ${SCRIPTS_FOLDER}/create_ssm_control_files_here.sh
	./scripts/package-ssm.sh
	
	
	

rm -f ssm/*
mkdir -p ssm

packages=`ls build`
for package in $packages ; do
		tar -zcvf ssm/${package}.ssm -C build ${package}/man ${package}/bin ${package}/src/core ${package}/src/utilities ${package}/src/xflow ${package}/src/xm ${package}/src/tcl ${package}/.ssm.d
done

echo
echo "Created SSM packages: '$packages'"
