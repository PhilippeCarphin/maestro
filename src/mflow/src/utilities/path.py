 
import os
import os.path

from utilities.colors import print_green

def mkdir_p(path):
    "behaves just like 'mkdir -p' "
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def list_files_recursively(path):
    """
    List all files found in this path.
    
    Faster than python os.walk, follows soft links, but not link loops.
    
    If there are soft link loops, 'find' returns a non-zero exit status and writes non-paths to stderr.
    So this function ignores stderr and exit status.
    """
    
    if not os.path.isdir(path):
        return []
    
    cmd="find -L %s -type f -print"%path
    cmd=cmd.split(" ")
    

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output, error = process.communicate()
    return output.strip().decode("utf8").split("\n")

def get_matching_paths_recursively(rootdir, extension="", verbose=0,
                                   path_blacklist=None, path_whitelist=None,follow_links=True,
                                   include_folders_in_results=False):
    """
    Searches 'rootdir' recursively and returns a list of full paths matching these conditions.
    
    extension: If specified, only files ending with this string are returned.
    path_blacklist: If given, cull the search to exclude any paths containing any one of these strings.
    path_whitelist: If given, only search paths containing at least one of these strings.
    """
    
    if not rootdir.endswith(os.sep):
        rootdir+=os.sep
        
    #Avoid mutability issues with function argument initalisers:
    if not path_blacklist:
        path_blacklist=[]
    if not path_whitelist:
        path_whitelist=[]
        
    if verbose:
        print(
            "Getting filenames for files with extension \"%s\" at:\n%s" %
            (extension, rootdir))
        
    for root, sub_folders, filenames in os.walk(rootdir,followlinks=follow_links):
        
        if include_folders_in_results:
            for sub_folder in sub_folders:
                yield os.path.join(root,sub_folder)
                
        for filename in filenames:
            
            if extension and not filename.endswith(extension):
                continue
                
            path = os.path.join(root, filename)
            
            "whitelist"
            found_white=not path_whitelist
            for white in path_whitelist:
                if white in path:
                    found_white=True
                    break
            if not found_white:
                continue
            
            "blacklist"
            found_black=False
            for black in path_blacklist:
                if black in path:
                    found_black=True
                    break
            if found_black:
                continue
                        
            yield path
    return