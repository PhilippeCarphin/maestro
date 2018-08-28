#!/bin/bash

function show_usage () {
	echo
	echo "Usage:"
	echo "    install-and-publish-ssm.sh <ssm-domain-path> <package-version>"
	exit 1
}

ssm_domain_path=$1 
version=$2 
platform=all
ssm_folder="ssm"

# Verify commandline arguments.
if [ -z "$ssm_domain_path" ] || [ -z "$version" ] ; then
		show_usage
fi

./setup/verify-ssm-packages.sh $version || exit 1

set -ex 
ssm created -d $ssm_domain_path || exit 1 

#ppp/gpsc

publish_platform=ubuntu-14.04-amd64-64

for package in  maestro-manager maestro-utils xflow ; do 

   ssm install -f $ssm_folder/${package}_${version}_${platform}.ssm -d $ssm_domain_path
   ssm publish -p ${package}_${version}_${platform} -d $ssm_domain_path -pp $publish_platform 

done 

ssm install -f $ssm_folder/maestro_${version}_${publish_platform}.ssm -d $ssm_domain_path
ssm publish -p maestro_${version}_${publish_platform} -d $ssm_domain_path

ssm install -f $ssm_folder/tcl-tk_*_${publish_platform}.ssm -d $ssm_domain_path

#hare/brooks

publish_platform=sles-11-amd64-64
ssm install -f $ssm_folder/maestro_${version}_${publish_platform}.ssm -d $ssm_domain_path
ssm publish -p maestro_${version}_${publish_platform} -d $ssm_domain_path 

echo "

# Load gnu compiler instead of default intel:
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu

# Put a generic environment tag instead of chipset specific name
export ORDENV_PLAT=${publish_platform}

cd $PWD ; 
ssm install -f $ssm_folder/tcl-tk_*_${publish_platform}.ssm -d  $ssm_domain_path 

" | ssh hare bash --login
