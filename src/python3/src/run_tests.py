#!../venv/bin/python3

"""mflow automated unit tests.

If no option like '--heimdall' or '--mflow' is provided, run all tests.

Usage:
   run_tests.py [options]

Options:
    --mflow             Run the mflow tests.
    --heimdall          Run heimdall tests.
    --verbose           More console output.
    --filter=<string>   Only Python script files containing this string will be run. [default: test_]

    -h --help           Show this screen.
    -v --version        Show version.
"""

from utilities import docopt
from tests.utilities import run_tests

def main(args):
    
    "if no option, test all"
    test_all=not args["--mflow"] and not args["--heimdall"]
    
    test_filter=args["--filter"]
    run_tests(verbose=args["--verbose"],
              test_mflow=args["--mflow"] or test_all,
              test_heimdall=args["--heimdall"] or test_all,              
              test_filter=test_filter)    
    print("Done.")

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)