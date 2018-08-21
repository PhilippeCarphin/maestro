#!/bin/ksh

# list packages

set -x 

dest_domain=$1 
version=$2 

#check for all packages: 

for platform in sles-11-amd64-64 ubuntu-14.04-amd64-64 ; do 

  pkg=maestro
  [[ -f ./${pkg}_${version}_${platform}.ssm ]] || something_missing="$something_missing ${pkg}_${version}_${platform}.ssm" 

  pkg=tcl-tk 
  [[ -f ./${pkg}_8.5.11_${platform}.ssm ]] || something_missing="$something_missing ${pkg}_${version}_${platform}.ssm" 


done  

platform=all 

for pkg in maestro-manager maestro-utils xflow ; do 

   [[ -f ./${pkg}_${version}_${platform}.ssm ]] || something_missing="$something_missing ${pkg}_${version}_${platform}.ssm" 
done 

[[ -n $something_missing ]] && echo Missing packages: $something_missing && exit 1 

ssm created -d $dest_domain || exit 1 

#ppp/gpsc

pub_platform=ubuntu-14.04-amd64-64

for pkg in  maestro-manager maestro-utils xflow ; do 

   ssm install -f ${pkg}_${version}_${platform}.ssm -d $dest_domain
   ssm publish -p ${pkg}_${version}_${platform} -d $dest_domain -pp $pub_platform 

done 

ssm install -f maestro_${version}_${pub_platform}.ssm -d $dest_domain
ssm publish -p maestro_${version}_${pub_platform} -d $dest_domain 

ssm install -f tcl-tk_*_${pub_platform}.ssm -d  $dest_domain 

#hare/brooks

pub_platform=sles-11-amd64-64

for pkg in  maestro-manager maestro-utils xflow ; do 

   ssm install -f ${pkg}_${version}_${platform}.ssm -d $dest_domain
   ssm publish -p ${pkg}_${version}_${platform} -d $dest_domain -pp $pub_platform 

done 
 
ssm install -f maestro_${version}_${pub_platform}.ssm -d $dest_domain
ssm publish -p maestro_${version}_${pub_platform} -d $dest_domain 

echo " 
export ORDENV_PLAT=$pub_platform ;  
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu ; 
cd $PWD ; 
ssm install -f tcl-tk_*_${pub_platform}.ssm -d  $dest_domain "  | ssh hare bash --login 
  
