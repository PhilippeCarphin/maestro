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
	$(MAKE) -C xflow
	$(MAKE) -C utilities
	$(MAKE) -C xm
	$(MAKE) -C tcl
	$(MAKE) -C core
	./setup/hare-compile.sh ;\

clean:
	rm -rf build ssm
