
import os
import os.path
import subprocess

from utilities.colors import print_green
from utilities.shell import safe_check_output_with_status


def list_files_recursively(path):
    """
    List all files found in this path.

    Faster than python os.walk, follows soft links, but not link loops.

    If there are soft link loops, 'find' returns a non-zero exit status and writes non-paths to stderr.
    So this function ignores stderr and exit status.
    """

    if not os.path.isdir(path):
        return []

    cmd = "find -L %s -type f -print" % path
    cmd = cmd.split(" ")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output, error = process.communicate()
    return output.strip().decode("utf8").split("\n")


def get_links_source_and_target(path):
    """
    Searches this path recursively for all symlinks, returning a list of 
    dictionaries, with all symlinks and their unresolved targets:

        {
        "source":"/home/abc123/projects/tmp",
        "target":"../tmp"
        }

    This can be used to audit relative/absolute links.
    """

    cmd = "find %s -type l" % path.strip()
    output, status = safe_check_output_with_status(cmd)
    if status != 0:
        return []

    results = []
    for source in output.split("\n"):
        cmd = "ls -l "+source
        output, status = safe_check_output_with_status(cmd)
        output = output.strip()
        a = " -> "
        if status != 0 or a not in output:
            continue
        target = output.split(a)[-1]
        result = {"source": source.strip(),
                  "target": target.strip()}
        results.append(result)

    return results


def get_matching_paths_recursively(rootdir, extension="", verbose=0,
                                   path_blacklist=None, path_whitelist=None, follow_links=True,
                                   include_folders_in_results=False):
    """
    Searches 'rootdir' recursively and returns a list of full paths matching these conditions.

    extension: If specified, only files ending with this string are returned.
    path_blacklist: If given, cull the search to exclude any paths containing any one of these strings.
    path_whitelist: If given, only search paths containing at least one of these strings.
    """

    if not rootdir.endswith(os.sep):
        rootdir += os.sep

    # Avoid mutability issues with function argument initalisers:
    if not path_blacklist:
        path_blacklist = []
    if not path_whitelist:
        path_whitelist = []

    if verbose:
        print(
            "Getting filenames for files with extension \"%s\" at:\n%s" %
            (extension, rootdir))

    for root, sub_folders, filenames in os.walk(rootdir, followlinks=follow_links):

        if include_folders_in_results:
            for sub_folder in sub_folders:
                yield os.path.join(root, sub_folder)

        for filename in filenames:

            if extension and not filename.endswith(extension):
                continue

            path = os.path.join(root, filename)

            "whitelist"
            found_white = not path_whitelist
            for white in path_whitelist:
                if white in path:
                    found_white = True
                    break
            if not found_white:
                continue

            "blacklist"
            found_black = False
            for black in path_blacklist:
                if black in path:
                    found_black = True
                    break
            if found_black:
                continue

            yield path
    return


def guess_user_home_from_path(path):
    """
    Given a path like:
        /fs/abc/home/sts271/folder1/folder
    makes a best guess to return the home root:
        /fs/abc/home/sts271

    use realpath, and files/folders typically in home, like '.ssh'
    """

    path = os.path.realpath(path)+"/"

    items1 = """bin
logs
maestro_suites
ovbin
public_html
rarcdirectives
tmp
xflow.suites.xml
xflow_preop.suites.xml
.Xauthority
.Xdefaults
.ade.cfg
.bash_history
.cache
.conda
.config
.emacs.d
.gitconfig
.gnupg
.gossip
.hcron
.jobctl
.kde
.local
.maestrorc
.mozilla
.ord_soumet.d
.profile
.profile.d
.ssh
.sshj
.suites
.vim
.viminfo
.vimrc""".split("\n")

    items2 = """rarcdirectives
xflow.suites.xml
xflow_preop.suites.xml
.Xauthority
.Xdefaults
.bash_history
.cache
.config
.hcron
.kde
.local
.maestrorc
.mozilla
.profile
.profile.d
.ssh
.vim
.viminfo
.vimrc""".split("\n")

    items1 = [i for i in items1 if i not in items2]

    best_path = ""
    best_score = 0

    while path and path != "/":
        score = 0

        if not os.path.exists(path):
            path = os.path.dirname(path)
            continue

        files_here = set(os.listdir(path))
        for item in items1:
            if item in files_here:
                score += 1
        for item in items2:
            if item in files_here:
                score += 3

        """
        You can override the real user's home with a test suite folder,
        if you place a file with this name in that folder.
        """
        for item in files_here:
            if item == "unittest-home-override":
                score += 1000

        if score >= best_score:
            best_path = path
            best_score = score

        path = os.path.dirname(path)

    return best_path+"/"
