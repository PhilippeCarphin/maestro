#!/bin/bash

# Autoformat all '.c' and '.h' files in this project.

# find the full path which contains this script file, no matter where it is called from.
script_folder="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

target_folder=${script_folder}/../src/core
if [[ ! -d $target_folder ]] ; then
	echo "Doing nothing. Target folder for c autoformat does not exist: $target_folder"
	exit 1
fi

targets="$(find $target_folder -name "*.c") $(find $target_folder -name "*.h")"
for target in $targets ; do
	cmd="clang-format -i $target"
	echo $cmd
	$cmd
done
