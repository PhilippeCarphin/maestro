MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

export VERSION=$(shell ${PWD}/scripts/get_repo_version.py)
export SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
export BUILD_PLATFORM_FOLDER=${PWD}/build/${SSMPACKAGE}
export BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/bin
CC=cc

all: clean
	mkdir -p ${BUILD_PLATFORM_FOLDER}
	mkdir -p ${BIN_FOLDER}

	cp -r src ${BUILD_PLATFORM_FOLDER}/
	cp -r .ssm.d ${BUILD_PLATFORM_FOLDER}/

	if [[ `lsb_release -a` = *"SUSE LINUX"* ]] ; then \
			echo "If release is SUSE, assume we are on IBM cray architecture." ;\
			echo "Compiling on Cray architecture requires that we specify a module and more generic ORDENV_PLAT" ;\
			module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ;\
			export ORDENV_PLAT=sles-11-amd64-64 ;\
	fi

	make -C ${BUILD_PLATFORM_FOLDER}/src/core

	if [ -d "_tcl" ]; then \
			echo "Using _tcl folder instead of building tcl from source." ;\
			rm -rf ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
			cp -r _tcl/ ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	else \
			echo "Could not find _tcl folder, building tcl from source." ;\
			sleep 4 ;\
			make -C ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	fi

	cd ${BUILD_PLATFORM_FOLDER}/.ssm.d ; . ../../../scripts/create_ssm_control_files_here.sh
	
	./scripts/package-ssm.sh

clean:
	echo "version = ${VERSION}"
	rm -rf build ${BIN_FOLDER}
	mkdir -p build
