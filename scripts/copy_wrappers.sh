#!/bin/bash

# This copies the maestro wrapper scripts from the src folder to the build folder.
# It also prepends the appropriate prefix for example "maestro_1.5.1."

# Usage:
#     copy_wrappers.sh <WRAPPER_PREFIX> <TARGET_FOLDER>

# This script was written to be run within a makefile, so that the more popular and modern bash
# syntax can be used instead of gnu makefile syntax.

set -eu

WRAPPER_PREFIX=$1
TARGET_FOLDER=$2
SOURCE_FOLDER=src/core/wrappers

for wrapper in `ls $SOURCE_FOLDER` ; do 
    cp ${SOURCE_FOLDER}/${wrapper} ${TARGET_FOLDER}/${WRAPPER_PREFIX}${wrapper} ;
done

set -x
ls $TARGET_FOLDER
