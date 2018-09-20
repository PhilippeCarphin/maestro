MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

VERSION=$(shell ${PWD}/scripts/get_repo_version.py)
SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
BUILD_PLATFORM_FOLDER=${PWD}/build/${SSMPACKAGE}
BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/bin
CC=cc

all: clean
	mkdir -p ${BUILD_PLATFORM_FOLDER}
	mkdir -p ${BIN_FOLDER}

	cp -r src ${BUILD_PLATFORM_FOLDER}/
	cp -r .ssm.d ${BUILD_PLATFORM_FOLDER}/

	if [[ `lsb_release -a` = *"SUSE LINUX"* ]] ; then \
			echo "Compiling on SLES architecture requires that we specify a module and more generic ORDENV_PLAT" ;\
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
			make -C ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	fi
	
	./scripts/package-ssm.sh

clean:
	echo "version = ${VERSION}"
	rm -rf ${BUILD_PLATFORM_FOLDER} ${BIN_FOLDER}
