#!/bin/bash

# This script scans the ssm folder for all required ssm packages for the build.
# It outputs missing packages, and returns non-zero if anything is missing.

function show_usage () {
    echo "Usage:"
    echo "    verify-ssm-packages.sh <package_version>"
    exit 1
}

ssm_folder="ssm"
package_version=$1
SPACES="      "
if [ -z $package_version ] ; then
  show_usage
fi

# Build a list of required packages
required_packages=""
for platform in sles-11-amd64-64 ubuntu-14.04-amd64-64 ; do 
		required_packages="maestro_${package_version}_${platform}.ssm $required_packages"
		required_packages="tcl-tk_8.5.11_${platform}.ssm $required_packages"
done
for package in maestro-manager maestro-utils xflow ; do 
		platform=all 
		required_packages="${package}_${package_version}_${platform}.ssm $required_packages"
done 

if [ $verbose=="1" ] ; then
		echo
		echo "Required packages:"
		for package in $required_packages ; do
				echo "${SPACES}${package}"
		done
fi

# Print all missing packages.
has_missing=""
for package in $required_packages ; do
		if [ ! -f $ssm_folder/$package ]; then
				if [ -z $has_missing ] ; then
						echo
						echo "Missing packages:"
				fi
				echo "${SPACES}${package}"
				has_missing="true"
		fi
done

# Exit
if [ -n "$has_missing" ] ; then
	exit 1 
else
		echo
		echo "All required packages were found in folder '${ssm_folder}'"
		echo
fi
