#!/bin/bash

for path in $(cat c-files) ; do
	echo "Starting commented code stripping for:
	$path"
	./remove_commented_code.py c /home/zulban/eccc/ziggurat/maestro/$path
done
