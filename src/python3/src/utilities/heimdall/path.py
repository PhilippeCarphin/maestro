import re
import os.path

"matches the basename filename of most vim swap files"
VIM_SWAP_REGEX = re.compile(r"^\..+?\.sw[n-p]$")

"matches the basename filename of some emacs swap files"
EMACS_SWAP_REGEX1 = re.compile(r"^\#.+\#$")
EMACS_SWAP_REGEX2 = re.compile(r"^\.\#.+$")

"""
Matches Linux paths that are named reasonbly, without characters like "+"
"""
r="\/?([a-zA-Z0-9-_.]\/?)+"
DECENT_LINUX_PATH_REGEX_WITH_START_END = re.compile("^"+r+"$")
DECENT_LINUX_PATH_REGEX = re.compile(r)

"""
Matches reasonably named Linux paths with variables like:
    /home/$ABC/${CAT}/123
"""    
DECENT_LINUX_PATH_REGEX_WITH_DOLLAR = re.compile("^\/?(\$?{?[a-zA-Z0-9-_.]}?\/?)+$")

def get_ancestor_folders(folder, experiment_path):
    """
    Given a folder:
        /experiment/folder1/folder2
    and experiment_path:
        /experiment
    returns:
        ["/experiment/folder1/folder2",
         "/experiment/folder1",
         "/experiment"]
    """
    folders = set()
    parent = folder
    while parent.startswith(experiment_path):
        if parent != folder:
            folders.add(parent)
        parent = os.path.dirname(parent)
    return sorted(list(set(folders)))


def is_parallel_path(path):
    """
    Checks if this path string seems to be related to parallel systems (as opposed to operational).
    If so, returns the string segment used to diagnose this.
    If not, returns False.
    For example: 'smco501' or 'hubs/ade/par'
    """
    
    substring="/smco501/"
    if substring in path:
        return substring
    
    folders=["/hubs/suites/par",
             "/hubs/gridpt/par"
             "/hubs/scribe/par"
             "/hubs/banco/par"
             "/products/products_dbase/par"
             "/hubs/verif/par"
             "/hubs/umos/par"
             "/hubs/ade/par"]
    for folder in folders:
        if folder in path:
            return folder
        
    return False

def is_editor_swapfile(path):
    """
    Returns true if this path appears to be a swapfile for vim, emacs, etc.
    """

    basename = os.path.basename(path)

    regexes = [VIM_SWAP_REGEX,
               EMACS_SWAP_REGEX1,
               EMACS_SWAP_REGEX2]
    for r in regexes:
        if r.match(basename):
            return True

    emacs = [".emacs.desktop",
             ".emacs.desktop.lock",
             ".elc",
             "auto-save-list"]
    for e in emacs:
        if basename == e:
            return True

    return False
