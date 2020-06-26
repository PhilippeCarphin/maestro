from constants import SCANNER_CONTEXT, MAESTRO_ROOT

from heimdall.file_cache import file_cache

def guess_scanner_context_from_path(path):
    """
    Return a SCANNER_CONTEXT string like 'operational' or 'parallel'
    Makes a best guess.
    
    This code will need to be updated after system upgrades.
    """
        
    realpath=file_cache.realpath(path)
    
    a="/smco502/.suites/"
    if a in realpath:
        after=realpath.split(a)[-1]
        if after.startswith("preop"):
            return SCANNER_CONTEXT.PREOPERATIONAL
        return SCANNER_CONTEXT.OPERATIONAL
    
    if "/smco501/.suites/" in realpath:
        return SCANNER_CONTEXT.PARALLEL
    
    if MAESTRO_ROOT in realpath:
        return SCANNER_CONTEXT.TEST
    
    return SCANNER_CONTEXT.DEVELOPMENT