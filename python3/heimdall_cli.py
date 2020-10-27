#!venv/bin/python3

"""
Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues. Version {version}.

Running just "heimdall" scans a maestro experiment.

"heimdall blame" examines the git history of a project to find its lead authors. It awards points based on commit frequency, recency, and consistency.

"heimdall deltas" examines all experiments described in the comma delimited list '<delta-targets>'. A target can be a path to a suites XML, or a single experiment. If new scan codes are detected compared to last time 'deltas' was run, messages are printed and optionally emails are sent.

Usage:
    heimdall [options]
    heimdall blame <path-to-git-repo> [--count=<count>]
    heimdall deltas <delta-targets> [--scan-history=<folder>] [--email=<address>] [--op-home=<path>] [--op-suites-home=<path>] [--par-home=<path>] [--dry-run] [--verbose]

Options:
    --blacklist=<codes>          Comma delimited list of codes like '--blacklist=c001,w001'. Never show these codes.
    --context=<context>          Heimdall will guess the context like operational, preoperational, or parallel. Or you can override the guess with this option.
    --count=<count>              How many top maintainers to show in heimdall blame. [default: 5]
    --dry-run                    Do not perform any actions, like sending emails.
    --email=<address>            For use with 'deltas'. If new codes detected, sends an email with a delta report. Can also be a comma delimited list of emails.
    --exp=<experiment-path>      The path to a maestro experiment. By default, look in $PWD. [default: {experiment_path}]
    --home=<folder>              The home folder used to lookup files like '~/.suites/overrides.def'. By default, use the home of the owner of the maestro experiment.
    --hub-seconds=<t>            Spend this many seconds scanning the hub folder with an iterative deepening search. Max {max_hub_seconds}. Necessary because hubs can be huge. [default: 1]
    --language=<language>        Choose the language of the result messages. The default uses the value of $LANG and whether the first two letters are "en" or "fr". [default: {language}]
    --level=<level>              Only show messages at this level or above. There is critical, error, warning, info, and best-practice. You can also just use the first letter as an argument. [default: best-practice]    
    --max-repeat=<count>         The same message code will be shown this maximum number of times. Use zero for unlimited. [default: 5]
    --op-home=<path>             Path to the home of the operational user. [default: /home/smco500]
    --op-suites-home=<path>      Path to the home of owner of operational maestro suite files. [default: /home/smco502]
    --par-home=<path>            Path to the home of the parallel user. [default: /home/smco501]
    --results-json=<path>        Write the results JSON of one full scan to this path. [default: {user_home}/tmp/heimdall-scans/results.json]
    --scan-history=<folder>      For 'deltas', write the results JSON of many full scans to this path. [default: {user_home}/tmp/heimdall-scans/]
    --verbose                    Extra output.
    --whitelist=<codes>          Comma delimited list of codes like '--whitelist=c001,w001'. Only show these codes.
    
    -h --help   Show this description.
"""
from utilities.docopt import docopt
import os
import os.path

from home_logger import logger, add_stdout_handler
from constants import SCANNER_CONTEXTS
from heimdall import ExperimentScanner, run_heimdall_blame, get_new_messages_for_experiment_paths, print_scan_message, send_email_for_new_messages
from heimdall.docstring import adjust_docstring
__doc__ = adjust_docstring(__doc__)

def blame_cli(args):
    
    if not process_scan_cli_options(args):
        return
    
    run_heimdall_blame(args["<path-to-git-repo>"],
                       count=args["--count"])

def process_scan_cli_options(args):
    """
    Mutate the args dictionary from docopt, so that its options are cast and verified.
    
    Return True if the options seem valid. Print messages if invalid.
    
    This is used because different heimdall commands re-use the same options.
    """
    
    args["--exp"] = os.path.expanduser(args["--exp"])

    context = args["--context"]
    if context and context not in SCANNER_CONTEXTS:
        print("Invalid context '%s'. Context must be one of:\n    %s" % (context, "\n    ".join(SCANNER_CONTEXTS)))
        return False

    try:
        args["--hub-seconds"]=float(args["--hub-seconds"])
    except ValueError:
        print("--hub-seconds not a number.")
        return False
    
    if not args["--scan-history"].endswith("/"):
        args["--scan-history"]+="/"
    args["--scan-history"]=os.path.expanduser(args["--scan-history"])

    try:
        args["--max-repeat"] = max(0,int(args["--max-repeat"]))
    except ValueError:
        print("Bad --max-repeat value. Must be an integer.")
        return False
    
    try:
        args["--count"]=int(args["--count"])
    except ValueError:
        print("--count '%s' must be integer."%args["--count"])
        return False

    level = args["--level"].lower()
    if not level or level[0] not in "cewib":
        print("Bad --level option. See -h for more info.")
        return False
    args["--level"] = level[0]
    
    args["--whitelist"] = [] if not args["--whitelist"] else args["--whitelist"].split(",")
    args["--blacklist"] = [] if not args["--blacklist"] else args["--blacklist"].split(",")
    
    args["--email"] = [] if not args["--email"] else args["--email"].split(",")    
    for email in args["--email"]:
        if "@" not in email:
            print("Not an email address: '%s'"%email)
            return False

    targets=args["<delta-targets>"]
    if targets:
        targets=targets.split(",")
    else:
        targets=[]
    args["<delta-targets>"]=[os.path.expanduser(target) for target in targets]
    
    return True

def deltas_cli(args):
    
    if not process_scan_cli_options(args):
        return

    results=get_new_messages_for_experiment_paths(args["<delta-targets>"],
                                                  args["--scan-history"],
                                                  operational_home=args["--op-home"],
                                                  parallel_home=args["--par-home"],
                                                  operational_suites_home=args["--op-suites-home"])

    for result in results:
        new_messages=result["new_messages"]
        path=result["path"]
        scanner=result["scanner"]

        "filter out levels if --level"
        level=args["--level"]
        if level:
            levels="cewib"
            new_messages=[m for m in new_messages if levels.index(m["code"][0])<=levels.index(level)]
        
        "print"
        for message in new_messages:
            print_scan_message(message)

        if new_messages:
            logger.info("Found %s new message codes compared to last scan."%len(new_messages))
        else:
            logger.info("No new message codes compared to last scan.")
        
        emails=args["--email"]
        if new_messages and emails:
            send_email_for_new_messages(emails,
                                        new_messages,
                                        scanner.results_json,
                                        level=level,
                                        is_dry_run=args["--dry-run"])
            
def scan_cli(args):
    """
    Parse and validate the commandline options before proceeding to run the scan.
    """
    
    if not process_scan_cli_options(args):
        return

    print("Scanning maestro experiment.")
    
    scanner = ExperimentScanner(args["--exp"],
                                context=args["--context"],
                                operational_home=args["--op-home"],
                                parallel_home=args["--par-home"],
                                operational_suites_home=args["--op-suites-home"],
                                language=args["--language"],
                                hub_seconds=args["--hub-seconds"],
                                critical_error_is_exception=False,
                                write_results_json_path=args["--results-json"])

    """
    This next blacklist line can be removed once the MAESTRO_* 
    merge has been released to operations.
    """
    args["--blacklist"].append("b017")

    scanner.print_report(level=args["--level"],
                         max_repeat=args["--max-repeat"],
                         whitelist=args["--whitelist"],
                         blacklist=args["--blacklist"])

def main(args):

    if args["--verbose"]:
        add_stdout_handler(logger)
    
    if args["blame"]:
        blame_cli(args)
    elif args["deltas"]:
        deltas_cli(args)
    else:
        scan_cli(args)

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
