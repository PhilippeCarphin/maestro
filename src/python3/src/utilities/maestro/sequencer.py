
from utilities.shell import safe_check_output_with_status


def environment_has_maestro():
    """
    Returns true if there is a 'maestro' command.
    """
    output, status = safe_check_output_with_status("which maestro")
    return status == 0


def get_sequencer_loop_argument(loop_index_selection):
    """
    returns a string like 'loop1=5,loop3=2'
    """
    chunks = []
    for key, value in loop_index_selection.items():
        chunks.append("%s=%s" % (key, value))
    return ",".join(chunks)


def get_sequencer_command(experiment_path,
                          datestamp,
                          node_path,
                          signal="submit",
                          is_continue=True,
                          is_no_dependency=False,
                          loop_index_selection=None,
                          loop_index_argument=None):
    """
    constructs a maestro command like:
        maestro -e /home/sts271/turtle -d 20200401000000 
        -n /turtle/TurtlePower/splinterTask -s submit -f continue -i -l TurtlePower=1
    """
    if len(datestamp) == 10:
        datestamp += "0000"
    cmd = "maestro -e %s -d %s -n %s -s %s" % (experiment_path, datestamp, node_path, signal)

    if is_continue:
        cmd += " -f continue"

    if is_no_dependency:
        cmd += " -i"

    if loop_index_selection:
        loop_index_argument = get_sequencer_loop_argument(loop_index_selection)

    if loop_index_argument:
        cmd += " -l "+loop_index_argument

    return cmd
