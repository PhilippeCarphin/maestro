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

def get_latest_ssm_path_from_path(path,include_betas=False):
    """
    Given a path like:
        /fs/ssm/eccc/cmo/isst/maestro/1.5.8
    returns the latest version at that path with a similar version format.
    """
    
    ssm_path=os.path.dirname(path)
    version_folders=[]
    for version_folder in os.listdir(ssm_path):
        etc_dir=ssm_path+"/"+version_folder+"/etc"
        is_ssm=os.path.isdir(etc_dir)
        if is_ssm:
            version_folders.append(version_folder)
    
    reference_version=os.path.basename(path)
    return get_latest_ssm_version(reference_version,version_folders,include_betas=include_betas)

def get_latest_ssm_version(reference_version,versions,include_betas=False):
    """
    Return the latest version with similar syntax to the reference_version
    Given '1.3.1' and:
        1.5.3
        1.6.8
        1.6.9-beta
        1.7
    returns '1.6.8'
    or '1.6.9-beta' if include_betas
    """
    
    r=re.compile("[0-9]+")    
    def count_numeric_sections(text):
        "count the number of separate numeric sections in this text"
        return len(r.findall(text.strip()))
    
    section_count=count_numeric_sections(reference_version)
    latest=reference_version
    for version in sorted(versions):
        
        if not include_betas and "beta" in version:
            continue
        
        if count_numeric_sections(version)==section_count:
            latest=version
            
    return latest

def is_non_operational_home(path):
    """
    Returns true if this path is a non operational home, like a developer:
        /home/abc123/.suites/zdps
    These paths should not be referenced in operational projects.
    """
    
    if not path.startswith("/home/") and not path.startswith("/fs/home"):
        return False    
    
    op_users=["smco500","smco501","smco502"]
    op_folders=["/home/"+user for user in op_users]
    op_folders+=[os.path.realpath(folder) for folder in op_folders]
    for folder in op_folders:
        if path.startswith(folder):
            return False
    return True

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
