#!venv/bin/python3

"""
mflow visualizes maestro suites and tasks like xflow, but purely as a commandline application. This project aims to be simple and fast.

Lots of work is still being done on mflow. So far these are input keys you can use:
    
    up/down/left/right/end/home/page-up/page-down
    
    Also, 'q' or 'x' to quit.

Usage:
    m.flow [options]

Options:
    --exp=<experiment-path>      The path to a maestro experiment, such as a folder containing "ExpOptions". [default: %s]
    --date=<datestamp>           The datestamp to view. Uses YYYYMMDDHH format, or assumes 00 for YYYYMMDD. [default: %s]
    --config=<json>              A path to a configuration file for options which are rarely changed. [default: %s]
    --host=<host>                The host used to lookup log files. [default: %s]
    --verbose                    Enable verbose debug logging in the "$HOME/logs/mflow" files.
    
    -h --help   Show this description.
"""

import traceback

from utilities import adjust_docstring
__doc__=adjust_docstring(__doc__)

from utilities.docopt import docopt
from utilities import get_json_from_path, print_red, get_config
from tui import TuiManager
from maestro import MaestroExperimentSnapshot

def main(args):
    mes=MaestroExperimentSnapshot(args["--date"],
                                  path=args["--exp"],
                                  host=args["--host"],
                                  stdout_logging=False)
        
    try:
        tui_config=get_config(args["--config"])
    except:
        print_red("Aborted. Failed to open or parse config file '%s'"%args["--config"])
        traceback.print_exc()
        return
    
    tui=TuiManager(mes,
                   tui_config=tui_config,
                   verbose=args["--verbose"])
    
    tui.start()

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    import cProfile
    from utilities import xml_cache
    results=cProfile.run("main(args)","profile")
    print(results)

    xml_cache.show_time_report()


