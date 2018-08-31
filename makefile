include config.mk        

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
	
	$(MAKE) -C src/core
	$(MAKE) -C src/tcl
	
	echo "Creating ssm package: ${SSMPACKAGE}"
	mkdir -p ssm
	cp -r src/* ssm/
	tar cvf - $(SSMPACKAGE) | gzip -> $(SSMPACKAGE).ssm
	
	./hare-compile.sh ;\

clean:
	rm -rf ssm
