import os.path
import json
from datetime import datetime

from home_logger import logger
from heimdall import ExperimentScanner, print_scan_message
from utilities.shell import get_latest_hash_from_repo, safe_check_output_with_status
from utilities.io import get_json_from_path
from maestro.xml import get_experiment_paths_from_suites_xml

def get_new_messages_for_experiment_paths(experiment_paths,
                                          scan_history_folder,
                                          operational_home="",
                                          parallel_home="",
                                          operational_suites_home=""):
    """
    Scan each experiment path.
    Compare those results to the last scan performed.
    Return a dictionary. Key is experiment path, value is its list of 
    new messages found in the new scan but not the old.
    
    scan_history_folder example:
        ~/tmp/heimdall-scans
    """
    
    data={}
    
    for path in experiment_paths:
        scan_result_folder=scan_history_folder+"/"+path
        data[path]=get_new_messages_for_experiment_path(path,
                                                        scan_result_folder,
                                                        operational_home=operational_home,
                                                        parallel_home=parallel_home,
                                                        operational_suites_home=operational_suites_home)
        
    return data
        
def get_new_messages_for_experiment_path(experiment_path,
                                         scan_result_folder,
                                         operational_home="",
                                         parallel_home="",
                                         operational_suites_home=""):
    """
    If no history is found, return empty list.
    
    scan_result_folder example:
        ~/tmp/heimdall-scans/home/zulban/folder1
    """
        
    "paths"
    datestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    json_path_suffix=datestamp+"/scan-results.json"
    json_path=scan_result_folder+"/"+json_path_suffix
    latest_basename="latest.json"
    latest_path=scan_result_folder+"/"+latest_basename
    
    "compare hash now to previous scan"
    now_hash=get_latest_hash_from_repo(experiment_path)
    previous_results=get_json_from_path(latest_path)
    if previous_results:
        previous_hash=previous_results.get("commit_hash","")
    else:
        previous_hash=""
    if not now_hash:
        logger.info("Skipping new messages scan of experiment because it seems to have no git commit hash: '%s'"%experiment_path)
        return []
    if now_hash==previous_hash:
        logger.info("Repo commit has not changed since last scan: '%s'"%experiment_path)
        return []
    
    scanner = ExperimentScanner(path=experiment_path,
                                operational_home=operational_home,
                                parallel_home=parallel_home,
                                operational_suites_home=operational_suites_home,
                                critical_error_is_exception=False,
                                write_results_json_path=json_path)
    
    "update the latest soft link"
    cmd="cd %s ; rm -f %s ; ln -s %s %s"%(scan_result_folder,latest_basename,json_path_suffix,latest_basename)
    output,status=safe_check_output_with_status(cmd)
    if status!=0:
        logger.error("Failed to update latest soft link. Output:\n"+output)
    
    "if no previous history, nothing to compare"
    if not previous_results:
        logger.info("No previous history found for '%s'."%experiment_path)
        return []
    
    "compare old and new"
    latest_results=scanner.results_json
    previous_messages=previous_results["messages"]
    latest_messages=latest_results["messages"]
    return get_new_messages_from_old_new(previous_messages,latest_messages)

def get_experiment_paths_from_deltas_argument(argument):
    """
    Returns a list of all absolute experiment realpaths from the argument.
    
    Given a comma delimited string like:
        ~smco500/suites.xml,~smco500/.suites/gdps/g0
    expands the first argument suites XML file, but simply appends the expanded realpath second argument.
    """
    
    paths=[os.path.expanduser(p) for p in argument.split(",")]
    
    results=[]
    for path in paths:
        if os.path.isfile(path):
            results+=get_experiment_paths_from_suites_xml(path)
        elif os.path.isdir(path):
            results.append(path)
    
    return [os.path.realpath(p) for p in results]

def get_new_messages_from_old_new(old_messages,new_messages):
    """
    Return a list of messages that exist in the new but not in the old.
    """
    
    def dump_func(j):
        return json.dumps(j,sort_keys=True)
    
    "a string dump of each message in 'old' "
    if old_messages:
        old_strings=set([dump_func(message) for message in old_messages])
    else:
        old_strings=[]
        
    return [m for m in new_messages if dump_func(m) not in old_strings]
    