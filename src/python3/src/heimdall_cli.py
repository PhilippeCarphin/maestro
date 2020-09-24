#!venv/bin/python3

"""
Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues. Version %s.

Running just "heimdall" scans a maestro experiment.

"heimdall blame" examines the git history of a project to find its lead authors. It awards points based on commit frequency, recency, and consistency.

Usage:
    heimdall [options]
    heimdall blame <path-to-git-repo> [--count=<count>]

Options:
    --exp=<experiment-path>      The path to a maestro experiment. By default, look in $PWD. [default: %s]
    --context=<context>          Heimdall will guess the context like operational, preoperational, or parallel. Or you can override the guess with this option.
    --level=<level>              Only show messages at this level or above. There is critical, error, warning, info, and best-practice. You can also just use the first letter as an argument. [default: best-practice]    
    --max-repeat=<count>         The same message code will be shown this maximum number of times. Use zero for unlimited. [default: 5]
    --whitelist=<codes>          Comma delimited list of codes like '--whitelist=c001,w001'. Only show these codes.
    --blacklist=<codes>          Comma delimited list of codes like '--blacklist=c001,w001'. Never show these codes.
    --home=<folder>              The home folder used to lookup files like '~/.suites/overrides.def'. By default, use the home of the owner of the maestro experiment.
    --op-home=<path>             Path to the home of the operational user. [default: /home/smco500]
    --par-home=<path>            Path to the home of the parallel user. [default: /home/smco501]
    --op-suites-home=<path>       Path to the home of owner of operational maestro suite files. [default: /home/smco502]
    
    --count=<count>              How many top maintainers to show in heimdall blame. [default: 5]
    
    --language=<language>        Choose the language of the result messages. The default uses the value of $LANG and whether the first two letters are "en" or "fr". [default: %s]
    --verbose                    Enable verbose debug logging in the "$HOME/logs/mflow" files.
    -h --help   Show this description.
"""
from utilities.docopt import docopt
import os

from constants import SCANNER_CONTEXTS
from heimdall import ExperimentScanner, run_heimdall_blame
from utilities.heimdall.docstring import adjust_docstring
__doc__ = adjust_docstring(__doc__)

def blame_cli(args):
    """
    Parse and validate the commandline options before running blame.
    """
    
    try:
        count=args["--count"]
        if not count:
            count=0
        count=int(count)
    except:
        print("--count '%s' must be integer."%args["--count"])
        return
    
    run_heimdall_blame(args["<path-to-git-repo>"],
                       count=count)

def scan_cli(args):
    """
    Parse and validate the commandline options before proceeding to run the scan.
    """

    experiment_path = args["--exp"]
    if experiment_path.startswith("~"):
        experiment_path = os.path.expanduser(experiment_path)

    context = args["--context"]
    if context and context not in SCANNER_CONTEXTS:
        print("Invalid context '%s'. Context must be one of:\n    %s" % (context, "\n    ".join(SCANNER_CONTEXTS)))
        return

    print("Scanning maestro experiment.")

    scanner = ExperimentScanner(experiment_path,
                                context=context,
                                operational_home=args["--op-home"],
                                parallel_home=args["--par-home"],
                                operational_suites_home=args["--op-suites-home"],
                                language=args["--language"],
                                critical_error_is_exception=False)

    try:
        max_repeat = int(args["--max-repeat"])
        max_repeat = max(0, max_repeat)
    except:
        print("Bad --max-repeat value. Must be an integer.")
        return

    level = args["--level"].lower()
    if not level or level[0] not in "cewib":
        print("Bad --level option. See -h for more info.")
        return
    level = level[0]

    whitelist = [] if not args["--whitelist"] else args["--whitelist"].split(",")
    blacklist = [] if not args["--blacklist"] else args["--blacklist"].split(",")
    
    """
    This next blacklist line can be removed once the MAESTRO_* 
    merge has been released to operations.
    """
    blacklist.append("b017")

    scanner.print_report(level=level,
                         max_repeat=max_repeat,
                         whitelist=whitelist,
                         blacklist=blacklist)


def main(args):
    
    if args["blame"]:
        return blame_cli(args)
    
    return scan_cli(args)

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
