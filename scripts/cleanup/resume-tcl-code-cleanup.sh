#!/bin/bash

for path in $(cat tcl-files) ; do
	echo "Starting commented code stripping for:
	$path"
	./remove_commented_code.py tcl /home/zulban/eccc/ziggurat/maestro/$path
done
