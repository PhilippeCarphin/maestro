#!/usr/bin/python3

# Print the first fetch URL found in 'git remote -v'.
# Example:   git@gitlab.science.gc.ca:sts271/maestro.git
# If failure, prints nothing.

import sys, re
from utilities import safe_check_output

cmd="git remote -v"
output=safe_check_output(cmd)

fetch=" (fetch)"
if fetch not in output:
    sys.exit()

for line in output.split("\n"):
    if fetch not in line:
        continue
    split=re.split("[ \t]+",line)
    for item in split:
        if "/" in item or "@" in item:
            print(item)
            sys.exit()
