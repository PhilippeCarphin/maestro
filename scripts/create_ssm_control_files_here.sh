# This script uses variables in the environment to create the control and control.json files for SSM packages.
# It creates "control" and "control.json" in the current folder.
# If given, the first argument of the script is used as the 'git fetch url' to describe where to get the repo.

DESCRIPTION="Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems."
if [ ! -z "$1" ]; then
		DESCRIPTION="$DESCRIPTION You can get an up to date git repo here: $1"
fi

TITLE="maestro"

echo "Package: ${TITLE}
Version: ${VERSION}
Platform: ${ORDENV_PLAT}
Maintainer: ${USER}
BuildInfo:
Description: ${DESCRIPTION}" > control

echo "{
		\"description\": \"Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems.\",
		\"name\": \"${TITLE}\",
		\"platform\": \"${ORDENV_PLAT}\",
		\"summary\": \"Maestro Suite\",
		\"version\": \"${VERSION}\"
}" > control.json

echo "export SEQ_MAESTRO_VERSION=${VERSION}" > profile.sh
