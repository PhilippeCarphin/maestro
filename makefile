MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

all:
	$(MAKE) -C xflow/ssm clean
	$(MAKE) -C xflow/ssm

	$(MAKE) -C utilities/ssm clean
	$(MAKE) -C utilities/ssm

	$(MAKE) -C manager/ssm clean
	$(MAKE) -C manager/ssm

	$(MAKE) -C tcl/ssm clean
	$(MAKE) -C tcl/ssm

	$(MAKE) -C core clean
	$(MAKE) -C core

	./setup/hare-compile.sh || exit 1
	./setup/soft-link-ssm.sh || exit 1

