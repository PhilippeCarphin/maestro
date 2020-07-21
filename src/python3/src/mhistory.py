#!venv/bin/python3

"""
Show a report on many task statuses for many dates for one maestro suite.

Usage:
  m.history <maestro-experiment> [options]

Options:
  --start=<yyyymmddhh>     The earliest datestamp to consider. [default: $START_DATESTAMP]
  --end=<yyyymmddhh>       The latest datestamp to consider. [default: $END_DATESTAMP]
  --json                   Only print a results JSON.
  --html                   Generate a temporary HTML report.
  --html-path=<path>       The path of the generated HTML. [default: $HOME/tmp/maestro-status-summary/$UNIX_TIME.html]
  --browser                Generate a temporary HTML report and open it in a your browser.
  
  -h, --help               Show this documentation.

"""

import os
import time
import webbrowser

from history import get_yyyymmddhh
from utilities import docopt, print_green
from history import scan_maestro_statuses, print_results, save_report_html

start_datestamp = get_yyyymmddhh(hours_offset=-12)
end_datestamp = get_yyyymmddhh()
__doc__ = __doc__.replace("$HOME", os.environ["HOME"])
__doc__ = __doc__.replace("$START_DATESTAMP", start_datestamp)
__doc__ = __doc__.replace("$END_DATESTAMP", end_datestamp)


def main(args):
    start = args["--start"]
    end = args["--end"]
    html_path = args["--html-path"].replace("$UNIX_TIME", str(round(time.time())))
    verbose = not args["--html"] and not args["--json"]

    results = scan_maestro_statuses(args["<maestro-experiment>"], start, end,
                                    fill_in_date_gaps=True)

    if args["--json"]:
        print(json.dumps(results, indent=4, sort_keys=1))
    elif verbose:
        print_results(results)

    if args["--html"] or args["--browser"]:
        save_report_html(results, html_path, verbose=verbose)

    if args["--html"]:
        print(html_path)

    if args["--browser"]:
        print_green(f"Opening '{html_path}' with a web browser.")
        webbrowser.get("firefox").open(html_path)

    if verbose:
        print_green("Done.")


if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
