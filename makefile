include config.mk        

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

all: core tcl

core: clean src-copy
	make -C ${SWDEST}/src/core

tcl: clean src-copy
	make -C ${SWDEST}/src/tcl

src-copy:
	mkdir -p ${SWDEST}
	cp config.mk ${SWDEST}/
	cp -r src ${SWDEST}/
	cp -r .ssm.d ${SWDEST}/

clean:
	rm -rf ${SWDEST} ${BIN_FOLDER}

skip-tcl: core
	cp -r ../tcl-maestro-backup-compiled/ ${SWDEST}/src/tcl/
