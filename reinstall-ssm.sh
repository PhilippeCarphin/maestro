#!/bin/bash

echo "Fast way to erase and reinstall the ssm package. Convenient for development.
If <version> is not provided, assemble a guess from the git hash/tags.
If <ssm-root> is not provided, use '$HOME/ssm'.

Usage:
    ./reinstall-ssm.sh
    ./reinstall-ssm.sh <version>
    ./reinstall-ssm.sh <version> <ssm-root>
"

set -exu

# Define constants

PROJECT_PATH=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename $PROJECT_PATH)

# Use $1 and $2, or these defaults if they are empty.
VERSION=${1:-$($PROJECT_PATH/scripts/get_repo_version.sh)}
SSM_ROOT=${2:-$HOME/ssm}

INSTALLED_MAESTRO_PATH=$SSM_ROOT/$PROJECT_NAME
SSM_DOMAIN_PATH=$INSTALLED_MAESTRO_PATH/$VERSION
# If we find builds for these platforms, make them into ssm packages.
PLATFORMS="ubuntu-14.04-amd64-64 sles-11-amd64-64"

# Remove previous
rm -rf $INSTALLED_MAESTRO_PATH

# Install new
ssm created -d $SSM_DOMAIN_PATH
cd $PROJECT_PATH
SSM_PACKAGES=""
for platform in $PLATFORMS ; do
		SSM_PACKAGE=ssm/${PROJECT_NAME}_${VERSION}_${platform}.ssm
		if [[ -f $SSM_PACKAGE ]]; then
				SSM_PACKAGES="${SSM_PACKAGES} ${SSM_PACKAGE}"
				ssm install -f $SSM_PACKAGE -d $SSM_DOMAIN_PATH
				ssm publish -p ${PROJECT_NAME}_${VERSION}_${platform} -d $SSM_DOMAIN_PATH -pp $platform 
        else
            echo "Did not find SSM package '$SSM_PACKAGE' for platform '$platform'. Skipping install and publish."
		fi
done

set +x

echo "Installed and published: '$SSM_PACKAGES'"

BASELINE_DOMAIN="eccc/cmo/isst/maestro/1.5.1-rc22"
if [[ -n $(command -v python3) ]] ; then
		./scripts/environment-compare.py $SSM_DOMAIN_PATH $BASELINE_DOMAIN
fi

echo
echo "To use the new SSM package:

     . ssmuse-sh -d $SSM_DOMAIN_PATH

You may also want to start the mserver with the new maestro version:

     . ssmuse-sh -d $SSM_DOMAIN_PATH ; mserver_check -m maestro1"