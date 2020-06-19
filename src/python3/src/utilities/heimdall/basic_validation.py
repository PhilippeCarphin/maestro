import os.path

def has_blocking_error(path):
    bool(find_blocking_errors(path))

def find_blocking_errors(path):
    """
    Quickly scan a maestro experiment path for very basic, critical errors 
    that prevent even MaestroExperiment or mflow from running.
        
    Returns:
        {
        code:kwargs,
        code:kwargs
        }
    for all errors.
    
    code is a heimdall message code.
    
    kwargs is the dictionary (sometimes empty) required by 
    HeimdallMessageManager to construct a message.
    """
    
    errors={}
    
    entry_module=path+"EntryModule"
    
    if not path or not os.path.exists(path) or not os.path.isdir(path):
        errors["e4"]={"path":path}
        "no point doing the other scans if no path"
        return errors
    
    required_folders=("listings","sequencing","stats","logs")
    missing=[]
    for folder in required_folders:
        if not os.path.isdir(path+folder):
            missing.append(folder)
    if missing:
        errors["e1"]={"folders":", ".join(missing)}
        
    if os.path.exists(entry_module):
        if not os.path.islink(entry_module):
            errors["e3"]={"entry_module":entry_module}
    else:
        errors["e2"]={"entry_module":entry_module}        
        
    return errors