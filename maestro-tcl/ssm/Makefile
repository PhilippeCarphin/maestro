include ../config/config.mk              

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
	.SUFFIXES:

all: ssm

ssm:
	echo "Creating SSM package $(SSMPACKAGE)..."
	if [ ! -d $(SSMPACKAGE) ]; then \
	   mkdir $(SSMPACKAGE); \
	fi;
	cp -r ../src $(SSMPACKAGE);
	cp -r ../maint $(SSMPACKAGE); 
	cp -r ../lib $(SSMPACKAGE); 
	cp ../LICENSE.txt $(SSMPACKAGE);
	cp -r ../bin $(SSMPACKAGE);
	mkdir -p $(SSMPACKAGE)/.ssm.d;
	mkdir -p $(SSMPACKAGE)/ssm;
	cp post-install Makefile $(SSMPACKAGE)/ssm;
	mkdir -p $(SSMPACKAGE)/.ssm.d;
	cp post-install $(SSMPACKAGE)/.ssm.d;
	echo "Package: tcl-tk" > $(SSMPACKAGE)/.ssm.d/control; \
	echo "Version: ${VERSION}" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "Platform: ${ORDENV_PLAT}" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "Maintainer: $(shell whoami)" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "BuildInfo:" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "Description: maestro tcl-tk 8.5" >> $(SSMPACKAGE)/.ssm.d/control; \
	tar cvf - $(SSMPACKAGE) | gzip -> $(SSMPACKAGE).ssm

clean:
	rm -fr $(SSMPACKAGE).ssm $(SSMPACKAGE)
