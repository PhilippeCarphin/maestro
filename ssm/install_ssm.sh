#!/bin/bash

USAGE="Fast way to install the ssm package. By default, only installs a package. You can also optionally delete some, or all, previously installed packages. Convenient for development.

Usage:
    ./install-ssm.sh <version> [--ssm-root=<path>] [--delete-all]
    
Options:
    -h --help             Show help.
    --ssm-root=<path>     Install and publish the SSM in this folder. Default: $HOME/ssm
    --delete-all          Delete all installed and published SSMs for this package in the --ssm-root.
    --reinstall           If this version is already installed, uninstall it first.
"

set -eu

# idiomatic parameter and option handling in sh
VERSION=$1
SSM_ROOT=$HOME/ssm
DELETE_ALL_SSM=false
REINSTALL=false
while test $# -gt 0
do
    case "$1" in
        --delete-all) DELETE_ALL_SSM=true
            ;;
        --help) echo "$USAGE" ; exit 0
            ;;
        -h) echo "$USAGE" ; exit 0
            ;;
        --reinstall) REINSTALL=true
            ;;
        --ssm-root=*) SSM_ROOT="${1#*=}"
            ;;
    esac
    shift
done

echo "$USAGE"

set -x

# Constants
PROJECT_PATH=$(git rev-parse --show-toplevel)
NAME=$(basename $PROJECT_PATH)
INSTALLED_MAESTRO_PATH=$SSM_ROOT/$NAME
SSM_DOMAIN_PATH=$INSTALLED_MAESTRO_PATH/$VERSION
# If we find builds for these platforms, make them into ssm packages.
PLATFORMS=$(cat $PROJECT_PATH/ssm/supported_platforms)

# Remove previous
if [[ $DELETE_ALL_SSM = "true" ]]; then
    	rm -rf $INSTALLED_MAESTRO_PATH
fi
if [[ $REINSTALL = "true" ]]; then
    	rm -rf $SSM_DOMAIN_PATH/*${ORDENV_PLAT}*
fi

# Install new

if [[ ! -d $SSM_DOMAIN_PATH ]] ; then
	ssm created -d $SSM_DOMAIN_PATH
fi

cd $PROJECT_PATH
SSM_PACKAGES=""
for platform in $PLATFORMS ; do
		SSM_PACKAGE=ssm/maestro_${VERSION}_${platform}.ssm
		if [[ -f $SSM_PACKAGE ]]; then
				SSM_PACKAGES="${SSM_PACKAGES} ${SSM_PACKAGE}"
				ssm install -f $SSM_PACKAGE -d $SSM_DOMAIN_PATH
				ssm publish -p maestro_${VERSION}_${platform} -d $SSM_DOMAIN_PATH -pp $platform 
		fi
done

set +x

echo "Installed and published: '$SSM_PACKAGES'"

BASELINE_MAESTRO_DOMAIN="eccc/cmo/isst/maestro/1.5.1-rc22"
if [[ -n $(command -v python3) ]] ; then
		./scripts/environment-compare.py $SSM_DOMAIN_PATH $BASELINE_MAESTRO_DOMAIN
fi

echo
echo "To use the new SSM package:

     . ssmuse-sh -d $SSM_DOMAIN_PATH

You may also want to start the mserver with the new maestro version:

     . ssmuse-sh -d $SSM_DOMAIN_PATH ; mserver_check -m maestro1"