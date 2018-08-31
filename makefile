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
clean:
	rm -rf ${SWDEST}
