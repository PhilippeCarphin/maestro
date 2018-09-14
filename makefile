include config.mk        

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

all: clean
	mkdir -p ${SWDEST}
	cp config.mk ${SWDEST}/
	cp -r src ${SWDEST}/
	make -C ${SWDEST}/src/core
	make -C ${SWDEST}/src/tcl
	
	# Soft link all bins to the root bin folder.
	mkdir -p ${BIN_FOLDER}
	# Do not copy tcl bins however, because it may clash with system tcl.
	ln -s ${SWDEST}/src/core/bin/* ${BIN_FOLDER}/
	ln -s ${SWDEST}/src/utilities/bin/* ${BIN_FOLDER}/
	ln -s ${SWDEST}/src/xflow/bin/* ${BIN_FOLDER}/
	ln -s ${SWDEST}/src/xm/bin/* ${BIN_FOLDER}/
clean:
	rm -rf ${SWDEST} ${BIN_FOLDER}
