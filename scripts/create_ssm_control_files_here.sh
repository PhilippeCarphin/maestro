# This script uses variables in the environment to create the control and control.json files for SSM packages.
# It creates "control" and "control.json" in the current folder.

DESCRIPTION="Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems."
TITLE="maestro"

echo "Package: ${TITLE}
Version: ${VERSION}
Platform: ${ORDENV_PLATFORM}
Maintainer: ${USER}
BuildInfo:
Description: ${DESCRIPTION}" > control

echo "{
		\"description\": \"Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems.\",
		\"name\": \"${TITLE}\",
		\"platform\": \"${PLATFORM}\",
		\"summary\": \"Maestro Suite\",
		\"version\": \"${VERSION}\"
}" > control.json
