#!/bin/ksh

if [ -z "$1" ] || [ -z  "$2" ] ; then
		echo "Usage:"
		echo "    script.ksh <ssm-domain-path> <package-version>"
		exit 1
fi

destination_domain=$1 
version=$2 

# Verify that we have all required packages

for platform in sles-11-amd64-64 ubuntu-14.04-amd64-64 ; do 
  package=maestro
  [[ -f ./${package}_${version}_${platform}.ssm ]] || missing_packages="$missing_packages ${package}_${version}_${platform}.ssm" 
  package=tcl-tk 
  [[ -f ./${package}_8.5.11_${platform}.ssm ]] || missing_packages="$missing_packages ${package}_${version}_${platform}.ssm" 
done  

platform=all 

for package in maestro-manager maestro-utils xflow ; do 
   [[ -f ./${package}_${version}_${platform}.ssm ]] || missing_packages="$missing_packages ${package}_${version}_${platform}.ssm" 
done 

if [ -n "$missing_packages" ] ; then
	echo "Missing packages:"
	for package in $missing_packages
	do
			echo "$package"
	done

	exit 1 
fi

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
  
