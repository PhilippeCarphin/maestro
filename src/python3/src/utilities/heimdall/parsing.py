
import re
from heimdall.file_cache import file_cache

"""
Regex to capture the entire line that seems to be a call to nodelogger with -s argument.
Captured group 1 is '-s' argument.
"""
NODELOGGER_SIGNAL_REGEX=re.compile(r".*nodelogger.*-s[ ]+([^ \n]+).*")

def get_nodelogger_signals_from_task_path(path):
    data=file_cache.open(path)
    return get_nodelogger_signals_from_task_text(data)

def get_nodelogger_signals_from_task_text(text):
    """
    Given the text in a task file, returns a list of all '-s' arguments like 'infox'
    
    returns a list of results, where result:
        {
             "line_number":123,
             "line":line,
             "signal":signal
        }
    """
   
    results=[]
    lines=text.split("\n")
    for match in NODELOGGER_SIGNAL_REGEX.finditer(text):
        line=match.group(0)
        signal=match.group(1)
        result={"line_number":lines.index(line),
                "line":line,
                "signal":signal}
        results.append(result)
       
    return results