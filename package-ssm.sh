#!/bin/bash

# This script is run after the compilation to create the ssm packages.

package="ubuntu-14.04-amd64-64"
folder="maestro_1.5.1_$package"

set -ex
rm -f ssm/*
tar -zcvf ssm/maestro_1.5.1_${package}.ssm -C build ${folder}/bin ${folder}/src/core ${folder}/src/utilities ${folder}/src/xflow ${folder}/src/xm ${folder}/config.mk ${folder}/.ssm.d

# tar -zcvf ssm/tcl-tk_8.5.11_${package}.ssm LICENSE.txt -C build/${package}/src/tcl bin .ssm.d
