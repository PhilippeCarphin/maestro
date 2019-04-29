#!/bin/bash

# Attempts to print a version string like '1.5.1' from this repo.

# First tries git describe for the tag.
# If that fails, first 16 characters of checked out branch hash.
# If that fails (no repo?) prints 'unknown-version'

output1=$(git describe 2>/dev/null)
output2=$(git rev-parse HEAD 2>/dev/null)

commit_hash_length=8
unknown="unknown_version"

if [[ -n "$output1" && $output1 != *"fatal:"* ]] ; then
		version=${output1}

		if [ -z "$version" ] ; then
				echo $unknown
		else
				echo $version
		fi

elif [[ -n "$output2" && $output2 != *"fatal:"* ]] ; then
		version=${output2:0:$commit_hash_length}

		if [ -z "$version" ] ; then
				echo $unknown
		else
				echo $version
		fi
else
		echo $unknown
fi
