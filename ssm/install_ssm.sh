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

BASELINE_MAESTRO_DOMAIN="eccc/cmo/isst/maestro/1.6.8"

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

# Constants
set -x
PROJECT_PATH=$(git rev-parse --show-toplevel)
PROJECT_SSM_PATH=$PROJECT_PATH/ssm
NAME=$(basename $PROJECT_PATH)
INSTALLED_MAESTRO_PATH=$SSM_ROOT/$NAME
SSM_DOMAIN_PATH=$INSTALLED_MAESTRO_PATH/$VERSION
# If we find builds for these platforms, make them into ssm packages.
PLATFORMS=$(cat $PROJECT_PATH/ssm/supported_platforms)
set +x

# Remove previous
if [[ $DELETE_ALL_SSM = "true" ]]; then
	set -x
    	rm -rf $INSTALLED_MAESTRO_PATH
	set +x
fi
if [[ $REINSTALL = "true" ]]; then
	set -x
	rm -rf $SSM_DOMAIN_PATH/*${ORDENV_PLAT}*
	set +x
	SSM_PACKAGES=""
	for platform in $PLATFORMS ; do
		SSM_PACKAGE=ssm/maestro_${VERSION}_${platform}.ssm
		if [[ -f $SSM_PACKAGE ]]; then
			set -x
			ssm unpublish -p maestro_${VERSION}_${platform} -d $SSM_DOMAIN_PATH
			ssm uninstall -p maestro_${VERSION}_${platform} -d $SSM_DOMAIN_PATH
			set +x
		fi
	done
fi

# Install new

if [[ ! -d $SSM_DOMAIN_PATH ]] ; then
	set -x
	ssm created -d $SSM_DOMAIN_PATH
	set +x
fi

cd $PROJECT_PATH
SSM_PACKAGES=""
for platform in $PLATFORMS ; do
		SSM_PACKAGE=ssm/maestro_${VERSION}_${platform}.ssm
		if [[ -f $SSM_PACKAGE ]]; then
				SSM_PACKAGES="${SSM_PACKAGES} ${SSM_PACKAGE}"
				set -x
				ssm install -f $SSM_PACKAGE -d $SSM_DOMAIN_PATH
				ssm publish -p maestro_${VERSION}_${platform} -d $SSM_DOMAIN_PATH -pp $platform 
				set +x
		fi
done

if [[ -z "$SSM_PACKAGES" ]] ; then
	echo "
Aborted. Did not find any SSM packages to install in '$PROJECT_SSM_PATH'.
Perhaps version argument '$VERSION' is incorrect?"
	all_ssm_packages=$(find $PROJECT_SSM_PATH -name "*.ssm" -type f -exec basename {} \;)
	if [[ -z $all_ssm_packages ]] ; then
		echo "Found no SSM packages."
	else
		echo "SSM packages in '$PROJECT_SSM_PATH':

$all_ssm_packages
	"
	fi
	exit 1
fi

echo "Installed and published: '$SSM_PACKAGES'"

if [[ -n $(command -v python3) ]] ; then
		./scripts/environment-compare.py $SSM_DOMAIN_PATH $BASELINE_MAESTRO_DOMAIN
fi

echo
echo "To use the new SSM package:

     . ssmuse-sh -d $SSM_DOMAIN_PATH

You may also want to start the mserver with the new maestro version:

     . ssmuse-sh -d $SSM_DOMAIN_PATH ; mserver_check -m $TRUE_HOST"
