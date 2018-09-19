MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

VERSION=$(shell ./get_repo_version.py)
SSMPACKAGE=maestro_${VERSION}_${ORDENV_PLAT}
BUILD_PLATFORM_FOLDER=${PWD}/build/${SSMPACKAGE}
BIN_FOLDER=${BUILD_PLATFORM_FOLDER}/bin
CC=cc

all: core tcl

core: clean src-copy
	make -C ${BUILD_PLATFORM_FOLDER}/src/core

tcl: clean src-copy
	make -C ${BUILD_PLATFORM_FOLDER}/src/tcl

src-copy:
	mkdir -p ${BUILD_PLATFORM_FOLDER}
	mkdir -p ${BIN_FOLDER}

	cp -r src ${BUILD_PLATFORM_FOLDER}/
	cp -r .ssm.d ${BUILD_PLATFORM_FOLDER}/

clean:
	echo "version = ${VERSION}"
	rm -rf ${BUILD_PLATFORM_FOLDER} ${BIN_FOLDER}

skip-tcl: core
	# tcl rarely needs to be recompiled from source. This option speeds up development for clean builds.
	# Just copy the contents of build/.../src/tcl to the folder here.
	rm -rf ${BUILD_PLATFORM_FOLDER}/src/tcl
	cp -r ../tcl-maestro-backup-compiled/ ${BUILD_PLATFORM_FOLDER}/src/tcl
