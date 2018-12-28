#!/bin/bash

# Print the first fetch URL found in 'git remote -v'.
# Example:   git@gitlab.science.gc.ca:sts271/maestro.git

fetch_line=$(git remote -v | grep \(fetch\) )
array=($fetch_line)
echo ${array[1]}
