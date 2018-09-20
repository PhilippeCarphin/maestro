#!/bin/bash

# This script is run after the compilation to create the ssm packages using all builds in the build folder.

rm -f ssm/*
mkdir -p ssm

packages=`ls build`
for package in $packages ; do
		tar -zcvf ssm/${package}.ssm -C build ${package}/bin ${package}/src/core ${package}/src/utilities ${package}/src/xflow ${package}/src/xm ${package}/src/tcl ${package}/.ssm.d
done

echo
echo "Created SSM packages: '$packages'"
