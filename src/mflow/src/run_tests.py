#!../venv/bin/python3

"""mflow automated unit tests.

Usage:
   run_tests.py [options]

Options:
    --verbose           More console output.
    --filter=<string>   Only Python script files containing this string will be run. [default: test_]

    -h --help           Show this screen.
    -v --version        Show version.
"""

from utilities import docopt
from utilities.test import run_tests

def main(args):
    test_filter=args["--filter"]
    run_tests(verbose=args["--verbose"],test_filter=test_filter)    
    print("Done.")

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)