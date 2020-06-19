import os
import os.path

from constants import NODE_STATUS

def get_intervals_from_status_path(path):
    """given a 'sequencing/status' path, returns a list of valid hour intervals, for example ("06","18") """
    datestamps=[d for d in os.listdir(path) if len(d)==14 and d.isdigit()]
    hours=set([d[8:10] for d in datestamps])
    return tuple(sorted(list(hours)))

def get_status_from_path(path):
    """
    examples for paths:
        folder/abc.abort.stop     returns "stop", "abort.stop"
        folder/abc.begin          returns "begin", "begin"
        folder/abc.end            returns "end", "end"
    """
    
    if path.endswith("abort.stop"):
        return NODE_STATUS.ABORT, "abort.stop"
    
    status=path.split(".")[-1]
    return status, status