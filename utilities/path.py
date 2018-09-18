 
import os
import os.path

from utilities.colors import *

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
    results = []
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


def safe_write(path,data,verbose=True):
    "Writes this data to path, creates any necessary folders."
    directory=os.sep.join(path.split(os.sep)[:-1])
    if directory and not os.path.exists(directory):
        if verbose:
            print_green("Making directory: '%s'"%directory)
        os.makedirs(directory)
    with open(path,"w") as f:
        f.write(data)
    if verbose:
        print_green("Wrote data to file '%s'"%path)