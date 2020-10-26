#!venv/bin/python3

"""
mflow visualizes maestro suites and tasks like xflow, but purely as a commandline application. This project aims to be simple and fast. Version %s.

Keyboard keys:
* Press 'q' or 'x' to quit.
* Press 'e' to go into edit mode. Normally, temporary copies of CFG/TSK/XML files are created for viewing in a text editor. In edit mode, the actual real files are opened for editing instead.

Config:
    You can find good defaults for the '--config' option here:
    %s

Usage:
    m.flow [options]

Options:
    --exp=<experiment-path>      The path to a maestro experiment, such as a folder containing "ExpOptions". [default: %s]
    --date=<datestamp>           The datestamp to view using YYYYMMDDHH or YYYYMMDD format. Default is the latest found in experiment logs. If none, datestamp is now.
    --config=<path>              A path to a configuration file for options which are rarely changed. If '%s/.mflowrc' exists, that becomes the default. [default: %s]
    --config-inline=<values>     A comma delimited list of values here is read as if it were in the --config file. Example: --config-inline=A=1,B=2
    --home=<folder>              The home folder used to lookup files like '~/.suites/overrides.def'. By default, use the home of the owner of the maestro experiment.
    
    --tui-id=<id>                Used internally. This value helps the bash wrapper distinguish between multiple launches of mflow.
    --debug                      Enable debug/developer features which regular users should never see.
    --verbose                    Enable verbose debug logging in the "$HOME/logs/mflow" files.
    
    -h --help   Show this description.

See Also:
    https://gitlab.science.gc.ca/CMOI/maestro
    https://gitlab.science.gc.ca/CMOI/maestro/issues?label_name%%5B%%5D=component%%3Amflow
"""

from maestro.datestamp import get_latest_yyyymmddhh_from_experiment_path, get_yyyymmddhh
from maestro_experiment import MaestroExperiment
from mflow import TuiManager
from mflow.threading import async_set_qstat_data_in_maestro_experiment
from mflow import get_mflow_config, get_unknown_mflow_config_keys
from utilities import print_red
from utilities.docopt import docopt
import traceback
import os.path

from mflow.docstring import adjust_docstring
__doc__ = adjust_docstring(__doc__)


def main(args):

    experiment_path = args["--exp"]
    if experiment_path.startswith("~"):
        experiment_path = os.path.expanduser(experiment_path)

    datestamp = args["--date"]
    if not datestamp:
        datestamp = get_latest_yyyymmddhh_from_experiment_path(experiment_path)
    if not datestamp:
        datestamp = get_yyyymmddhh()

    print("Reading experiment files for '%s'" % experiment_path)

    try:
        tui_config = get_mflow_config(os.path.expanduser(args["--config"]),
                                      inline_config_string=args["--config-inline"])
    except:
        print_red("Aborted. Failed to open or parse config file '%s'" % args["--config"])
        traceback.print_exc()
        return
    
    unknown_keys=get_unknown_mflow_config_keys(tui_config)
    if unknown_keys:
        print_red("Aborted. Found config keys that are not present in the default config file. This probably means it's a typo: "+str(unknown_keys))
        return

    interval = tui_config["FLOW_STATUS_REFRESH_SECONDS"]
    me = MaestroExperiment(experiment_path,
                           datestamp=datestamp,
                           user_home=args["--home"],
                           node_log_refresh_interval=interval)

    if me.has_critical_error():
        for error in me.get_critical_error():
            print_red(error)
        return

    """
    Launch a different thread to run, parse, and eventually set qstat_data
    Not required, but nice to have for user/queue checks.
    """
    async_set_qstat_data_in_maestro_experiment(me)

    tui = TuiManager(me,
                     tui_config=tui_config,
                     is_debug=args["--debug"],
                     verbose=args["--verbose"],
                     tui_id=args["--tui-id"])

    tui.start()

    if tui.curses_setup_fail_message:
        print(tui.curses_setup_fail_message)
        return

    if tui.has_scheduled_command:
        print("Pausing mflow to run a command, mflow will resume after the other program finishes.")
    else:
        print("Exiting mflow.")


if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
