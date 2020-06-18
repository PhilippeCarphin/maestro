#!venv/bin/python3

"""
Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues. Version %s.

Config:
    You can find good defaults for the '--config' option here:
    %s

Usage:
    heimdall [options]

Options:
    --context=<context>          Heimdall will guess the context like operational, preoperational, or parallel. Or you can override the guess with this option.
    --exp=<experiment-path>      The path to a maestro experiment. By default, look in $PWD. [default: %s]
    --home=<folder>              The home folder used to lookup files like '~/.suites/overrides.def'. By default, use the home of the owner of the maestro experiment.
    
    --verbose                    Enable verbose debug logging in the "$HOME/logs/mflow" files.
    -h --help   Show this description.
"""
import os
from heimdall_utilities.docstring import adjust_docstring
__doc__=adjust_docstring(__doc__)

from utilities.docopt import docopt
from utilities import print_red
from mflow.utilities import get_mflow_config
from maestro.experiment import MaestroExperiment
from suite_scanner import ExperimentScanner

def main(args):
    
    experiment_path=args["--exp"]
    if experiment_path.startswith("~"):
        experiment_path=os.path.expanduser(experiment_path)
    
    print("Reading experiment files for '%s'"%experiment_path)
    
    me=MaestroExperiment(experiment_path,
                         user_home=args["--home"])
    
    print("Scanning maestro experiment.")
    
    scanner=ExperimentScanner(me)
    
    scanner.print_report()

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)


