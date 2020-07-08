#!venv/bin/python3

"""
Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues. Version %s.

Usage:
    heimdall [options]

Options:
    --exp=<experiment-path>      The path to a maestro experiment. By default, look in $PWD. [default: %s]
    --context=<context>          Heimdall will guess the context like operational, preoperational, or parallel. Or you can override the guess with this option.    
    --level=<level>              Only show messages at this level or above. There is critical, error, warning, info, and best-practice. You can also just use the first letter as an argument. [default: best-practice]    
    --home=<folder>              The home folder used to lookup files like '~/.suites/overrides.def'. By default, use the home of the owner of the maestro experiment.
    --op-home=<path>             Path to the home of the operational user. [default: /home/smco500]
    --par-home=<path>            Path to the home of the parallel user. [default: /home/smco501]
    
    --verbose                    Enable verbose debug logging in the "$HOME/logs/mflow" files.
    -h --help   Show this description.
"""
import os

from constants import SCANNER_CONTEXTS
from heimdall import ExperimentScanner
from utilities.heimdall.docstring import adjust_docstring
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
                              operational_home=args["--op-home"],
                              parallel_home=args["--par-home"],
                              critical_error_is_exception=False)
    
    level=args["--level"].lower()
    if not level or level[0] not in "cewib":
        print("Bad --level option. See -h for more info.")
        return
    level=level[0]
    
    scanner.print_report(level=level)

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)


