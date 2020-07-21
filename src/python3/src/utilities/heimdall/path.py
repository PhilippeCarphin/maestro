import re
import os.path

"matches the basename filename of most vim swap files"
VIM_SWAP_REGEX = re.compile(r"^\..+?\.sw[n-p]$")

"matches the basename filename of some emacs swap files"
EMACS_SWAP_REGEX1 = re.compile(r"^\#.+\#$")
EMACS_SWAP_REGEX2 = re.compile(r"^\.\#.+$")


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
