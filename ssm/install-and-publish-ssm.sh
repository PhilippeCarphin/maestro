#!/bin/bash

if [ -z "$1" ] || [ -z  "$2" ] ; then
		echo "Usage:"
		echo "    script.ksh <ssm-domain-path> <package-version>"
		exit 1
fi

destination_domain=$1 
version=$2 

./verify-ssm-packages.sh

set -ex 
ssm created -d $destination_domain || exit 1 

#ppp/gpsc

pub_platform=ubuntu-14.04-amd64-64

for package in  maestro-manager maestro-utils xflow ; do 

   ssm install -f ${package}_${version}_${platform}.ssm -d $destination_domain
   ssm publish -p ${package}_${version}_${platform} -d $destination_domain -pp $pub_platform 

done 

ssm install -f maestro_${version}_${pub_platform}.ssm -d $destination_domain
ssm publish -p maestro_${version}_${pub_platform} -d $destination_domain 

ssm install -f tcl-tk_*_${pub_platform}.ssm -d  $destination_domain 

#hare/brooks

pub_platform=sles-11-amd64-64

for package in  maestro-manager maestro-utils xflow ; do 

   ssm install -f ${package}_${version}_${platform}.ssm -d $destination_domain
   ssm publish -p ${package}_${version}_${platform} -d $destination_domain -pp $pub_platform 

done 
 
ssm install -f maestro_${version}_${pub_platform}.ssm -d $destination_domain
ssm publish -p maestro_${version}_${pub_platform} -d $destination_domain 

echo " 
export ORDENV_PLAT=$pub_platform ;  
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ; 
cd $PWD ; 
ssm install -f tcl-tk_*_${pub_platform}.ssm -d  $destination_domain "  | ssh hare bash --login 
  
