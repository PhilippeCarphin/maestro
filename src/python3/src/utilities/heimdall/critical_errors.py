import os.path
from utilities.xml import is_valid_xml

def has_critical_error(path):
    bool(find_critical_errors(path))

def find_critical_errors(path):
    """
    Quickly scan a maestro experiment path for blocking, critical errors 
    that prevent even MaestroExperiment, xflow, or mflow from running.
        
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
        errors["c3"]={"path":path}
        "no point doing the other scans if no path"
        return errors
    
    entry_flow=entry_module+"/flow.xml"
    if not os.path.isfile(entry_flow):
        errors["c4"]={"flow_xml":entry_flow}
        
    if not is_valid_xml(entry_flow):
        errors["c5"]={"flow_xml":entry_flow}
        
    if os.path.exists(entry_module):
        if not os.path.islink(entry_module):
            errors["c2"]={"entry_module":entry_module}
    else:
        errors["c1"]={"entry_module":entry_module}        
        
    return errors