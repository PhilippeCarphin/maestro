#!/bin/bash

# This script uses variables in the environment to create the control files for SSM packages.
# It creates "control" and "control.json" in <target-folder>.
# If given, <project-url> is added to the description of the package.
# Usage:
#     ./create_ssm_control_files.sh <version> <target-folder> [<project-url>]

set -exu

VERSION=$1
TARGET_FOLDER=$2
PROJECT_URL=${3-}

DESCRIPTION="Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems."
if [ ! -z "${PROJECT_URL:-}" ]; then
		DESCRIPTION="$DESCRIPTION  $PROJECT_URL"
fi

TITLE="maestro"

echo "Package: ${TITLE}
Version: ${VERSION}
Platform: ${ORDENV_PLAT}
Maintainer: ${USER}
BuildInfo:
Description: ${DESCRIPTION}" > ${TARGET_FOLDER}/control

echo "{
		\"description\": \"Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems.\",
		\"name\": \"${TITLE}\",
		\"platform\": \"${ORDENV_PLAT}\",
		\"summary\": \"Maestro Suite\",
		\"version\": \"${VERSION}\"
}" > ${TARGET_FOLDER}/control.json

echo "export SEQ_MAESTRO_VERSION=${VERSION}" > ${TARGET_FOLDER}/profile.sh
