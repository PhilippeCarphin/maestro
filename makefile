MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

export VERSION=$(shell ${PWD}/scripts/get_repo_version.sh )
export ORDENV_PLAT=$(shell ${PWD}/scripts/adjust_ordenv_plat.sh )
export SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
export BUILD_PLATFORM_FOLDER=${PWD}/build/${SSMPACKAGE}
export BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/bin
export WRAPPER_PREFIX=maestro_${VERSION}.
export WRAPPERS_BUILD_FOLDER=${BUILD_PLATFORM_FOLDER}/bin/wrappers
export SCRIPTS_FOLDER=${PWD}/scripts
export MAN_FOLDER=${BUILD_PLATFORM_FOLDER}/man/man1
CC=cc

all: clean
	echo "VERSION = '${VERSION}'"
	# Abort if VERSION was not set.
	if [[ -z "${VERSION}" ]] ; then \
		echo "Aborted. Failed to find VERSION." ;\
		exit 1 ;\
	fi

	cd man ; ./create_roffs_from_markdown.sh
	mkdir -p ${MAN_FOLDER}
	cp -r man/roff/* ${MAN_FOLDER}

	if [[ "$(shell ${PWD}/scripts/is_platform_xc40.sh )" = "true" ]] ; then \
			echo "Compiling on Cray architecture requires that we specify a module." ;\
			module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ;\
	fi

	mkdir -p ${BUILD_PLATFORM_FOLDER} ${BIN_FOLDER} ${WRAPPERS_BUILD_FOLDER}
	
	${SCRIPTS_FOLDER}/copy_wrappers.sh ${WRAPPER_PREFIX} ${WRAPPERS_BUILD_FOLDER}
	cp -r src ${BUILD_PLATFORM_FOLDER}/
	cp -r .ssm.d ${BUILD_PLATFORM_FOLDER}/

	module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ; make -C ${BUILD_PLATFORM_FOLDER}/src/core

	if [ -d "_tcl" ]; then \
			echo "Using _tcl folder instead of building tcl from source." ;\
			rm -rf ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
			cp -r _tcl/ ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	else \
			echo "Could not find _tcl folder, building tcl from source." ;\
			sleep 4 ;\
			module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ; make -C ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	fi

	cd ${BUILD_PLATFORM_FOLDER}/.ssm.d ; . ${SCRIPTS_FOLDER}/create_ssm_control_files_here.sh
	
	./scripts/package-ssm.sh
	
clean:
	echo "version = ${VERSION}"
	rm -rf build ${BIN_FOLDER}
	mkdir -p build
