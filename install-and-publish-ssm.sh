#!/bin/bash

function show_usage () {
	echo
	echo "Usage:"
	echo "    install-and-publish-ssm.sh <ssm-domain-path> <package-version>"
	exit 1
}

ssm_domain_path=$1 
version=$2

# Verify commandline arguments.
if [ -z "$ssm_domain_path" ] || [ -z "$version" ] ; then
		show_usage
fi

set -ex 
ssm created -d $ssm_domain_path || exit 1 

#ppp/gpsc

for platform in ubuntu-14.04-amd64-64 sles-11-amd64-64
    ssm install -f ssm/maestro_${version}_all.ssm -d $ssm_domain_path
    ssm publish -p maestro_${version}_all -d $ssm_domain_path -pp $platform 
    
    ssm install -f ssm/tcl-tk_*_${platform}.ssm -d $ssm_domain_path
done
