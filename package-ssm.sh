#!/bin/bash

# This script is run after the compilation to create the ssm packages.

package="ubuntu-14.04-amd64-64"
set -ex
rm -f ssm/*
tar -zcvf ssm/maestro_1.5.1_${package}.ssm -C build ${package}/bin ${package}/src/core ${package}/src/utilities ${package}/src/xflow ${package}/src/xm ${package}/config.mk ${package}/.ssm.d

# tar -zcvf ssm/tcl-tk_8.5.11_${package}.ssm LICENSE.txt -C build/${package}/src/tcl bin .ssm.d
