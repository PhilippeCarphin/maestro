import os
import os.path


def find_exp_home_in_path(path):
    """
    Travel up the directory tree in path until a valid maestro experiment
    SEQ_EXP_HOME is found, return that.
    """
    cursor = path
    while cursor and cursor != "/":
        path = cursor+"/EntryModule"
        if os.path.isdir(path):
            if not cursor.endswith("/"):
                cursor += "/"
            return cursor
        cursor = os.path.dirname(cursor)
    return ""


def get_exp_home_from_pwd():
    pwd = os.getcwd()
    path = find_exp_home_in_path(pwd)
    if path:
        return path
    return os.path.realpath("")


def get_experiment_name(path):
    """
    Given a path like:
        /suites/gdps/g0
    returns:
        gdps/g0
    """

    if path.endswith("/"):
        path = path[:-1]

    chunks = path.split("/")
    return chunks[-2]+"/"+chunks[-1]
