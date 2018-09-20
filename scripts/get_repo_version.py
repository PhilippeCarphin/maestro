#!/usr/bin/python3

# Attempts to print a version string like '1.5.1' from this repo.

# First tries git describe for the tag.
# If that fails, first 16 characters of checked out branch hash.
# If that fails (no repo?) prints 'unknown-version'

import sys
from utilities import safe_check_output

cmd1="git describe"
output1=safe_check_output(cmd1)
cmd2="git rev-parse HEAD"
output2=safe_check_output(cmd2)

if "fatal:" not in output1:
    print(output1.strip())
elif "fatal: " not in output2:
    print(output2.strip())
else:
    print("unknown-version")
