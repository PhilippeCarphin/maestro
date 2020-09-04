
import os
import os.path
import subprocess
import time

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

def get_link_chain_from_link(start_link):
    """
    Returns a list of all links followed to resolve this link.
    
    Given a link "a" in a folder with links:
        a -> b
        b -> c
        c -> d
    returns:
        ["a","b","c","d"]
    where each string will be the full path.
    """
    
    """
    output will be something like this:
        ...
        lstat("/home/123/a", {st_mode=S_IFLNK|0777, st_size=13, ...}) = 0
        ...
        lstat("/home/123/b", {st_mode=S_IFDIR|0775, st_size=4096, ...}) = 0
        ...
    """
    
    output,status=safe_check_output_with_status("strace realpath "+start_link)
    
    if status!=0:
        return []
    
    lstat_lines=[line for line in output.split("\n") if line.startswith("lstat(")]
    paths=[line.split("\"")[1] for line in lstat_lines]
    
    """
    If start_link is "/home/123/a" then the first strings in paths will be:
        "/home"
        "/home/123"
    so remove those.
    """
    basename=os.path.basename(start_link)
    for i,path in enumerate(paths):
        if path.endswith(basename):
            break
    return paths[i:]

def get_links_source_and_target(path,max_depth=0):
    """
    Searches this path recursively for all symlinks, returning a list of 
    dictionaries, with all symlinks and their unresolved targets:

        {
        "source":"/home/abc123/projects/tmp",
        "target":"../tmp"
        }

    This can be used to audit relative/absolute links.
    """
    
    assert type(max_depth) is int and max_depth>=0
    depth_option=" -maxdepth %s"%max_depth if max_depth else ""

    cmd = "find %s %s -type l" % (path.strip(),depth_option)
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

def iterative_deepening_search(rootdir,
                               max_seconds, 
                               follow_links=True,
                               debug_sleep_seconds=0):
    """
    Returns a list of file paths in this rootdir - as many as possible in the time given.
    Example:
        folder1/folder2/folder3
        folder1/folder2/folder4
    We search folder1
    folders 1, 2, and 3 contains just a few files.
    folder4 contains ten million files and listing them exceeds max_seconds.
    
    This will return the paths to files in folder1, folder2, but not folder3 or folder 4.
    
    debug_sleep_seconds can be used for testing - each depth iteration will sleep 
    this much to simulate large numbers of files.
    """
    
    assert type(max_seconds) in (int,float)
    assert max_seconds>0
    max_depth=100
    
    ids_start_time=time.time()
    
    "how long the most recent depth search took"
    previous_depth_seconds=0
    
    "the results of the most recent search"
    previous_results=[]
    
    for depth in range(1,max_depth):
        
        time_remaining=ids_start_time+max_seconds-time.time()
        if time_remaining<0:
            break
        
        """
        depth+1 will take longer than depth, so stop now if we have 
        less time left than last search took.
        """
        if time_remaining < previous_depth_seconds:
            break
        
        start_time=time.time()
        results=timeout_search(rootdir,depth,time_remaining,follow_links=follow_links)
        if debug_sleep_seconds:
            time.sleep(debug_sleep_seconds)
        previous_depth_seconds=time.time()-start_time
        
        "same result as depth-1 means we searched all, no need for deeper."
        if len(results) == len(previous_results):
            return results
        
        previous_results=results
    
    return sorted(results)
    
def timeout_search(rootdir,depth,max_seconds,follow_links=True):
    """
    Returns a list of all files found in rootdir at this depth.
    Returns an empty list if the search takes longer than max_seconds.
    """
    
    follow_links_option="-L" if follow_links else ""
    cmd="timeout %s find %s %s -maxdepth %s -type f | cut -c1-"%(max_seconds,
                                                    follow_links_option,
                                                    rootdir,
                                                    depth)
    output,status=safe_check_output_with_status(cmd)
    if status==0:
        return output.strip().split("\n")
    return []

def get_matching_paths_recursively(rootdir, 
                                   extension="", 
                                   verbose=0,
                                   path_blacklist=None, 
                                   path_whitelist=None, 
                                   follow_links=True,
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
