MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
	.SUFFIXES:

all:
	$(MAKE) -C ssm ssm

clean: 
	$(MAKE) -C ssm $@

distclean: clean
	find . -name "*~" -exec rm -f {} \;

install: all
	cd ssm ; $(MAKE) $@

uninstall:
	$(MAKE) -C ssm $@
