
import Levenshtein
import re
from heimdall.file_cache import file_cache
from utilities.parsing import get_bash_variables_used_in_text
from constants import TASK_MAESTRO_BINS

"""
Regex to capture the entire line that seems to be a call to nodelogger with -s argument.
Captured group 1 is '-s' argument.
"""
NODELOGGER_SIGNAL_REGEX = re.compile(r".*nodelogger.*-s[ ]+([^ \n]+).*")

"""
Captures strings like 'ABC_DEF=123' where group 1 is "ABC_DEF"
"""
CONSTANT_VARIABLE_REGEX = re.compile(r"^[ ]*([A-Z]+[A-Z_]*)[ ]*=")

"""
Captures the full path to maestro tools often used in tsk files, like:
    ${MAYBE_SEQ_BIN}/nodelogger
    maestro
    $ABC/nodeinfo
"""
regex_suffix="("+"|".join(TASK_MAESTRO_BINS)+")"
TASK_MAESTRO_BINS_REGEX = re.compile("\/?(([a-zA-Z0-9-_.${}]\/?)*)"+regex_suffix)

def get_maestro_executables_from_bash_text(text):
    """
    Finds many maestro executables in this bash-like text.
    
    Given bash text like:
        
    echo 123
    nodelogger -m 123
    ${MAYBE_SEQ_BIN}/scanexp -a 123
    du -sh 123
    
    returns:
        ["nodelogger", "${MAYBE_SEQ_BIN}/scanexp"]
    """
    
    "the join is necessary because of multiple regex groups returned"
    results=[m.group(0) for m in TASK_MAESTRO_BINS_REGEX.finditer(text)]
    
    return sorted(list(set(results)))

def is_etiket_variable(bash_variable_name):
    """
    Returns true if this bash variable name appears to be an etiket variable name.
    """
    lower=bash_variable_name.lower()
    return (lower.startswith("etik") or 
            lower.endswith("etik") or 
            lower.endswith("etiket") or 
            lower.endswith("eticket"))

def get_etiket_variables_used_from_path(path,require_etiket_programs=True):
    "See get_etiket_variables_used_from_text"
    with open(path,"r") as f:
        text=f.read()
    return get_etiket_variables_used_from_text(text,
                                               require_etiket_programs=require_etiket_programs)

def get_etiket_variables_used_from_text(text,require_etiket_programs=True):
    """
    Return a list of all variables used in this text that appear to be etiket related.
    """
    
    "return [] if no etiket-like programs are found."
    if require_etiket_programs and "/pgsm " not in text and "/editfst " not in text:
        return []
    
    variables=get_bash_variables_used_in_text(text)
    etikets=[v for v in variables if is_etiket_variable(v)]
    return sorted(list(set(etikets)))

def get_nodelogger_signals_from_task_path(path):
    data = file_cache.open(path)
    return get_nodelogger_signals_from_task_text(data)

def get_ssm_domains_from_string(text):
    """
    Given strings like:
        . ssmuse-sh -d abc -d def
        . ssmuse-sh -x abc
        . r.load.dot abc def
    returns ["abc","def"]
    """
    text=text.strip()
    domains=[]
    
    if text.startswith("#"):
        return []
    
    if text.startswith(". ssmuse"):
        last_stub_was_option=False
        for stub in re.split("[ ]+",text):
            if last_stub_was_option:
                last_stub_was_option=False
                domains.append(stub)
            if stub in ("-d","+d","-p","+p","-x"):
                last_stub_was_option=True
    elif text.startswith(". r.load"):
        chunks=re.split("[ ]+",text)
        for i,chunk in enumerate(chunks[:]):
            if chunk.startswith("r.load") or chunk.startswith("r.shortcut"):
                domains=chunks[i+1:]
                break
    
    return domains

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
