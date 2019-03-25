MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

# Setup the environment for xc40 compilation if xc40
export IS_XC40=$(shell ${PWD}/scripts/is_platform_xc40.sh )
export XC40_MODULE_SWITCH=
export XC40_DYNAMIC_FLAG=
ifeq (${IS_XC40}, true)
		export ORDENV_PLAT=sles-11-amd64-64
		export XC40_MODULE_SWITCH=module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ; 
		export XC40_DYNAMIC_FLAG=-dynamic
endif

export VERSION=$(shell ${PWD}/scripts/get_repo_version.sh )
export SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
export BUILD_FOLDER=${PWD}/build
export BUILD_PLATFORM_FOLDER=${BUILD_FOLDER}/${SSMPACKAGE}
export BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/bin
export TCL_BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/tcl_bin
export WRAPPER_PREFIX=maestro_${VERSION}.
export WRAPPERS_BUILD_FOLDER=${BUILD_PLATFORM_FOLDER}/src/core/wrappers
export SCRIPTS_FOLDER=${PWD}/scripts
export SSM_FOLDER=${PWD}/ssm
export MAN_FOLDER=${BUILD_PLATFORM_FOLDER}/man/man1
CC=cc

all: clean
	echo "VERSION = '${VERSION}'"
	echo "ORDENV_PLAT = '${ORDENV_PLAT}'"
	# Abort if VERSION was not set.
	if [[ -z "${VERSION}" ]] ; then \
		echo "Aborted. Failed to find VERSION." ;\
		exit 1 ;\
	fi

	cd man ; ./create_roffs_from_markdown.sh
	mkdir -p ${MAN_FOLDER}
	cp -r man/roff/* ${MAN_FOLDER}

	if [ -n "${XC40_MODULE_SWITCH}" ] ; then \
			echo "Compiling on some architectures like xc40 requires that we specify a module for a different 'gcc'." ;\
			echo "In this case we are using this module switch:" ;\
			echo "        ${XC40_MODULE_SWITCH}" ;\
	fi

	mkdir -p ${BUILD_PLATFORM_FOLDER} ${BIN_FOLDER} ${WRAPPERS_BUILD_FOLDER}
	
	${SCRIPTS_FOLDER}/copy_wrappers.sh ${WRAPPER_PREFIX} ${WRAPPERS_BUILD_FOLDER}
	cp -r src ${BUILD_PLATFORM_FOLDER}/
	cp -r ssm/.ssm.d ${BUILD_PLATFORM_FOLDER}/

	${XC40_MODULE_SWITCH} make -C ${BUILD_PLATFORM_FOLDER}/src/core

	# Use != instead of == so that IS_XC40==true is explicitly the only way we skip this important step.
	if [ -d "_tcl" ] && [ ${IS_XC40} != "true" ] ; then \
		echo "Using _tcl folder instead of building tcl from source." ;\
		rm -rf ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
		cp -r _tcl/ ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	elif [ ${IS_XC40} != "true" ] ; then \
		echo "Could not find _tcl folder, building tcl from source." ;\
		sleep 4 ;\
		${XC40_MODULE_SWITCH} make -C ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
	fi \
	
	. ${SSM_FOLDER}/create_ssm_control_files.sh ${BUILD_PLATFORM_FOLDER}/.ssm.d
	${SSM_FOLDER}/package-ssm.sh
	
clean:
	rm -rf ${BIN_FOLDER}
	# Delete all builds for this ord environment platform
	rm -rf ${BUILD_FOLDER}/*${ORDENV_PLAT}*

	mkdir -p build
