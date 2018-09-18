#!/bin/bash

ssm_domain_path=$HOME/ssm/maestro/1.5.1
version=1.5.1
set -ex 
rm -rf /home/sts271/ssm/maestro/1.5.1
ssm created -d $ssm_domain_path

cd /home/sts271/projects/maestro

platform="ubuntu-14.04-amd64-64"
ssm install -f ssm/maestro_${version}_${platform}.ssm -d $ssm_domain_path
ssm publish -p maestro_${version}_${platform} -d $ssm_domain_path -pp $platform 
#ssm install -f ssm/tcl-tk_*_${platform}.ssm -d $ssm_domain_path

set +x

echo ". ssmuse-sh -d $HOME/ssm/maestro/1.5.1/"
. ssmuse-sh -d $HOME/ssm/maestro/1.5.1/
