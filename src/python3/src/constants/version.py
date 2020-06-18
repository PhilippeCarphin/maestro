
from constants.path import MAESTRO_ROOT
from utilities.shell import safe_check_output_with_status

def get_version():
    """
    Returns a string like:
        1.6.8
        1.6.8-53-g360cb181
        1.6.8-dev
    depending on tags, commits, git describe, and untracked changes
    """    
    
    cmd="cd %s && git describe"%MAESTRO_ROOT
    output,status=safe_check_output_with_status(cmd)
    if status!=0:
        return "unknown"
    version=output[:20].strip()
    
    cmd="""cd %s ; git diff-index --quiet HEAD -- || echo "untracked" """%MAESTRO_ROOT
    output,status=safe_check_output_with_status(cmd)
    is_untracked="untracked" in output
    if is_untracked:
        commit=version.split("-")[-1]
        version=commit+"-dev"
        
    return version
    
VERSION=get_version()