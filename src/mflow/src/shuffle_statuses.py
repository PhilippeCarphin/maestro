#!../venv/bin/python3

"""
Given a maestro experiment path, toggle all abort statuses to end, and all end to abort. Useful to test flow displays.

Usage:
    shuffle_statuses.py <maestro-experiment> [options]

Options:
    -h --help          Show this description.
    --loop=<seconds>   Repeat the shuffle indefinitely, interval in seconds.
"""

import time
import os
from utilities.docopt import docopt
from utilities import get_matching_paths_recursively, pprint

def shuffle(experiment):
    statuses_path=experiment+"/sequencing/status"
    e1=".end"
    e2=".abort.stop"
    renames={}
    for path in get_matching_paths_recursively(statuses_path):
        
        for i in range(2):
            e1,e2=e2,e1
            if path.endswith(e1):
                new_path=path[:-len(e1)]+e2
                renames[path]=new_path
    
    for old_path,new_path in renames.items():
        os.rename(old_path,new_path)
    print("Renamed %s status files."%len(renames))

def main(args):

    loop_seconds=0
    if args["--loop"]:
        loop_seconds=int(args["--loop"])

    first_loop=True
    while first_loop or loop_seconds:
        first_loop=False
        shuffle(args["<maestro-experiment>"])
        if loop_seconds:
            time.sleep(loop_seconds)
    print("Done.")

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)


