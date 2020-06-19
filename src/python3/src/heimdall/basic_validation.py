from heimdall.message_manager import hmm
import os.path

def get_blocking_error(path):
    code,message=find_blocking_error(path)
    return message

def find_blocking_error(path):
    """
    Quickly scan a maestro experiment path for very basic, critical errors 
    that prevent even MaestroExperiment or mflow from running.
    Return a heimdall code and message:
        (code,message)
    """
    
    entry_module=path+"EntryModule"
    
    if not path or not os.path.exists(path) or not os.path.isdir(path):
        code="e4"
        message=hmm.get(code,path=path)
        return code,message    
    
    if not os.path.exists(entry_module):
        code="e2"
        message=hmm.get(code,entry_module=entry_module)
        return code,message
    
    if not os.path.islink(entry_module):
        code="e3"
        message=hmm.get(code,entry_module=entry_module)
        return code,message    

    return None,None