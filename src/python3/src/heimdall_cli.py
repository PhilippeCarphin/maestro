#!venv/bin/python3

"""
Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues. Version %s.

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

from constants import SCANNER_CONTEXTS
from heimdall import ExperimentScanner
from utilities.heimdall import adjust_docstring
__doc__=adjust_docstring(__doc__)

from utilities.docopt import docopt

def main(args):
    
    experiment_path=args["--exp"]
    if experiment_path.startswith("~"):
        experiment_path=os.path.expanduser(experiment_path)
        
    context=args["--context"]
    if context and context not in SCANNER_CONTEXTS:
        print("Invalid context '%s'. Context must be one of:\n    %s"%(context,"\n    ".join(SCANNER_CONTEXTS)))
        return
        
    print("Scanning maestro experiment.")
    
    scanner=ExperimentScanner(experiment_path,
                              context=context,
                              critical_error_is_exception=False)
    
    scanner.print_report()

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)


