
import Levenshtein
import re
from heimdall.file_cache import file_cache

"""
Regex to capture the entire line that seems to be a call to nodelogger with -s argument.
Captured group 1 is '-s' argument.
"""
NODELOGGER_SIGNAL_REGEX = re.compile(r".*nodelogger.*-s[ ]+([^ \n]+).*")

"""
Captures strings like 'ABC_DEF=123' where group 1 is "ABC_DEF"
"""
CONSTANT_VARIABLE_REGEX = re.compile(r"^[ ]*([A-Z]+[A-Z_]*)[ ]*=")

def get_nodelogger_signals_from_task_path(path):
    data = file_cache.open(path)
    return get_nodelogger_signals_from_task_text(data)


def get_constant_definition_count(text):
    """
    Given text content like:        
        ABC=55
        ABC=66
        CAT=1
        # CAT=2
    returns counts of all variables:
        {"ABC":2, "CAT":1}
    """
    
    constants={}
    lines=text.split("\n")
    for line in lines:
        match=CONSTANT_VARIABLE_REGEX.match(line)
        if not match:
            continue
        name=match.group(1)
        if name not in constants:
            constants[name]=0
        constants[name]+=1  
    return constants

def get_resource_limits_from_batch_element(batch_element):
    """
    Given an lxml <BATCH> element, returns a resource limit dictionary
    that can be compared to get_resource_limits_from_qstat_data
    """

    result = {"wallclock_seconds": 0,
              "cpu_count": 0,
              "memory_bytes": 0}

    for attribute in ("wallclock", "cpu", "memory"):
        result[attribute] = "" if batch_element is None else batch_element.attrib.get(attribute)

    if batch_element is None:
        return result

    try:
        result["wallclock_seconds"] = int(batch_element.attrib["wallclock"])*60
    except:
        pass

    try:
        result["cpu_count"] = int(batch_element.attrib["cpu"])
    except:
        pass

    try:
        text = batch_element.attrib["memory"]
        if text.lower().endswith("g"):
            result["memory_bytes"] = int(text[:-1])*1024**3
    except:
        pass

    return result


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

    results = []
    lines = text.split("\n")
    for match in NODELOGGER_SIGNAL_REGEX.finditer(text):
        line = match.group(0)
        signal = match.group(1)
        result = {"line_number": lines.index(line),
                  "line": line,
                  "signal": signal}
        results.append(result)

    return results


def get_levenshtein_pairs(items, max_distance=1):
    """
    Given a list:
        ["eccc-ppp1","eccc-ppp2","turtle"]
    returns:
        {"pairs":(("eccc-ppp1","eccc-ppp2")),
         "no_match":("turtle"),
         "matches":("eccc-ppp1","eccc-ppp2")}
    based on closest Levenshtein distances to pair up strings.

    In cases like "a1" "a2" "a3" all are placed in "no_match"
    """

    items = sorted(list(set(items)))
    used = []
    pairs = []

    for item1 in items:
        best_score = -1
        best_item = ""
        for item2 in items:
            if item1 == item2:
                continue

            if item2 in used:
                continue

            d = Levenshtein.distance(item1, item2)
            if d < best_score or best_score == -1:
                best_score = d
                best_item = item2

        if best_item and best_score <= max_distance:
            used.append(item1)
            used.append(item2)
            pairs.append([item1, item2])

    no_match = [item for item in items if item not in used]
    return {"no_match": no_match,
            "pairs": pairs,
            "matches": used}
