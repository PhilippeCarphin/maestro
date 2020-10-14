#!venv/bin/python3

"""
Sometimes translation or typing introduces weird characters into the translation CSV, like slanted quotations.
This replaces them with normal characters. This happens a lot, and is a bug regression, so this script was written.

Usage:
    repair_codes_csv [options]

Options:
    --csv=<path>    Path to the message codes CSV to repair. [default: {csv_path}]
    
    --verbose
    -h --help   Show this description.
"""

import os.path
from constants import HEIMDALL_MESSAGE_CSV, BAD_SINGLE_QUOTE_CHARS, BAD_DOUBLE_QUOTE_CHARS
from utilities.docopt import docopt
    
def main(args):
    path=args["--csv"]
    verbose=args["--verbose"]
    if not os.path.isfile(path):
        print("Aborted. Not a file: '%s'"%path)
        return
    
    with open(path,"r") as f:
        data=f.read()
    original=data
    
    for c in BAD_SINGLE_QUOTE_CHARS:
        data=data.replace(c,"'")
    for c in BAD_DOUBLE_QUOTE_CHARS:
        data=data.replace(c,"\"")
    
    if original!=data:
        with open(path,"w") as f:
            f.write(data)
        if verbose:
            print("Fixed bad characters in CSV '%s'"%path)
    
if __name__ == "__main__":
    doc=__doc__.format(csv_path=HEIMDALL_MESSAGE_CSV)
    
    args = docopt(doc, version="1.0")
    main(args)
