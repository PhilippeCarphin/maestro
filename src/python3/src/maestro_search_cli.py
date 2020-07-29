#!venv/bin/python3

"""
Search maestro experiments and maestro experiment files.

Usage:
    maestro_search node_path [options]

Options:
    --substring=<string>      Print node paths containing this substring.
    --regex=<r>               Print node paths matching this regular expression.
    --exp=<experiment>        A path to a maestro experiment. [default: $PWD]
    
    --verbose                 Enable verbose debug logging in the "$HOME/logs/maestro_search" files.
    -h --help   Show this description.
"""
from utilities.docopt import docopt
from maestro_experiment import MaestroExperiment
import sys
import re
import os
__doc__ = __doc__.replace("$PWD", os.environ["PWD"])


def node_path_search(path, substring, regex_string, verbose=False):
    """
    Print node paths matching this search.
    """

    if verbose and regex_string:
        print("Node path search is using regular expression:\n"+regex_string+"\n")

    me = MaestroExperiment(path)

    regex = None if not regex_string else re.compile(regex_string)

    for node_data in me.get_node_datas():
        node_path = node_data["path"]
        if substring and substring in node_path:
            print(node_path)
        elif regex and regex.findall(node_path):
            print(node_path)


def main(args):

    verbose = args["--verbose"]

    experiment_path = args["--exp"]
    if experiment_path.startswith("~"):
        experiment_path = os.path.expanduser(experiment_path)

    if args["node_path"]:
        substring = args["--substring"]
        regex_string = args["--regex"]

        if regex_string:
            try:
                re.compile(regex_string)
            except re.error:
                print("Aborted. Not a valid regex: '%s'" % regex_string)
                sys.exit(1)

        if not substring and not regex_string:
            print("Aborted. Node path search requires '--substring' or '--regex'.")
            sys.exit(1)

        node_path_search(experiment_path,
                         substring,
                         regex_string,
                         verbose=verbose)

    if verbose:
        print("Done.")


if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
