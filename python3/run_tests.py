#!../venv/bin/python3

"""Automated unit tests for all maestro scripts written in Python3.

If no option like '--heimdall' or '--mflow' is provided, run all tests.

Usage:
   run_tests.py [options]

Options:
    --mflow             Run mflow tests.
    --heimdall          Run heimdall tests.
    --maestro           Run tests on Python3 maestro utility scripts.
    --filter=<string>   Only Python test script files containing this string will be run. [default: test_]
    --verbose
    
    -h --help           Show this screen.
    -v --version        Show version.
"""

from utilities import docopt
from tests.utilities import run_tests

def main(args):
    "if no option, test all"
    test_all = not args["--mflow"] and not args["--heimdall"] and not args["--maestro"]

    test_filter = args["--filter"]
    run_tests(verbose=args["--verbose"],
              test_mflow=args["--mflow"] or test_all,
              test_heimdall=args["--heimdall"] or test_all,
              test_maestro=args["--maestro"] or test_all,
              test_filter=test_filter)
    print("Done.")


if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
