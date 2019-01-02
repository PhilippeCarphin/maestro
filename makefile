MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

export VERSION=$(shell ${PWD}/scripts/get_repo_version.sh )
export ORDENV_PLAT=$(shell ${PWD}/scripts/adjust_ordenv_plat.sh )
export SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
export BUILD_FOLDER=${PWD}/build
export BUILD_PLATFORM_FOLDER=${BUILD_FOLDER}/${SSMPACKAGE}
export BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/bin
export WRAPPER_PREFIX=maestro_${VERSION}.
export WRAPPERS_BUILD_FOLDER=${BUILD_PLATFORM_FOLDER}/bin/wrappers
export SCRIPTS_FOLDER=${PWD}/scripts
export MAN_FOLDER=${BUILD_PLATFORM_FOLDER}/man/man1
export MODULE_SWITCH=$(shell ${PWD}/scripts/get_module_switch.sh )
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

	if [ -n "${MODULE_SWITCH}" ] ; then \
			echo "Compiling on some architectures like xc40 requires that we specify a module for a different 'gcc'." ;\
			echo "In this case we are using this module switch:" ;\
			echo "        ${MODULE_SWITCH}" ;\
	fi

	mkdir -p ${BUILD_PLATFORM_FOLDER} ${BIN_FOLDER} ${WRAPPERS_BUILD_FOLDER}
	
	${SCRIPTS_FOLDER}/copy_wrappers.sh ${WRAPPER_PREFIX} ${WRAPPERS_BUILD_FOLDER}
	cp -r src ${BUILD_PLATFORM_FOLDER}/
	cp -r .ssm.d ${BUILD_PLATFORM_FOLDER}/

	${MODULE_SWITCH} make -C ${BUILD_PLATFORM_FOLDER}/src/core

	if [ -d "_tcl" ]; then \
			echo "Using _tcl folder instead of building tcl from source." ;\
			rm -rf ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
			cp -r _tcl/ ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	else \
			echo "Could not find _tcl folder, building tcl from source." ;\
			sleep 4 ;\
			${MODULE_SWITCH} make -C ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	fi

	cd ${BUILD_PLATFORM_FOLDER}/.ssm.d ; . ${SCRIPTS_FOLDER}/create_ssm_control_files_here.sh
	
	./scripts/package-ssm.sh
	
clean:
	echo "version = ${VERSION}"

	rm -rf ${BIN_FOLDER}

	# Delete all builds for this ord environment platform
	rm -rf ${BUILD_FOLDER}/*${ORDENV_PLAT}*

	mkdir -p build
