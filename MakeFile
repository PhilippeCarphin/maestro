MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

all:
	$(MAKE) -C xflow/ssm clean
	$(MAKE) -C xflow/ssm

	$(MAKE) -C maestro-utils/ssm clean
	$(MAKE) -C maestro-utils/ssm

	$(MAKE) -C maestro-manager/ssm clean
	$(MAKE) -C maestro-manager/ssm

	$(MAKE) -C maestro-tcl/ssm clean
	$(MAKE) -C maestro-tcl/ssm

	$(MAKE) -C maestro-core clean
	$(MAKE) -C maestro-core

	./setup/hare-compile.sh || exit 1
	./setup/soft-link-ssm.sh || exit 1

