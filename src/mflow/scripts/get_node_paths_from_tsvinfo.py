#!/usr/bin/python3

"""
Given a file containing the output of tsvinfo, prints all unique node_paths.
     get_node_paths_from_tsvinfo.py <tsvinfo-output-file>
"""

import sys
import os.path

def usage():
    print(__doc__)
    sys.exit(1)

if len(sys.argv)!=2:
    usage()

filename=sys.argv[1]

if not os.path.isfile(filename):
    usage()

with open(filename,"r") as f:
    data=f.read()

stubs=data.split(" ")
node_paths=set()
for stub in stubs:
    if "/" in stub:
        node_paths.add(stub)

print("\n".join(sorted(list(node_paths))))
