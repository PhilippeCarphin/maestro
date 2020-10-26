import os.path
from utilities.xml import xml_cache


def has_critical_error(path):
    return bool(find_critical_errors(path))

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

    errors = {}

    entry_module = path+"EntryModule"

    if not path or not os.path.exists(path) or not os.path.isdir(path):
        errors["c003"] = {"path": path}
        "no point doing the other scans if no path"
        return errors

    entry_flow = entry_module+"/flow.xml"
    if not os.path.isfile(entry_flow):
        errors["c004"] = {"flow_xml": entry_flow}

    if not xml_cache.is_valid_xml(entry_flow):
        errors["c005"] = {"flow_xml": entry_flow}

    if os.path.exists(entry_module):
        if not os.path.islink(entry_module):
            errors["c002"] = {"entry_module": entry_module}
    else:
        errors["c001"] = {"entry_module": entry_module}

    return errors
