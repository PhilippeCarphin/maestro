MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

all: clean
	if [ ! -f config.mk ] ; then \
			echo "Aborted. You must first run the 'configure-make.sh' script to generate the 'config.mk' file." ;\
			exit 1 ;\
	fi;
	
	mkdir -p build ssm
	
	cp -r xflow/* build/xflow/	
	cp -r utilities/* build/utilities/	
	cp -r xm/* build/xm/
	cp -r tcl/* build/tcl/
	cp -r core/* build/core/
	
	./setup/hare-compile.sh ;\

clean:
	rm -rf build ssm
