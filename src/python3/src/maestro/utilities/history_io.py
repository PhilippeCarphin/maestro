import os
import json

from jinja2 import Template
from datetime import datetime

from utilities.colors import *
from utilities.generic import safe_write
from constants import TEMPLATE_FOLDER, NODE_STATUS

def print_results(results):
    print("Maestro status summary for path: ")
    print_orange("   '"+results["path"]+"'")
    
    start=results["start_date"]        
    end=results["end_date"]
    print(f"{start} to {end}")
    
    print("")
    for task_name in results["tasks"]:
        print("\n"+task_name)
        task_results=results["tasks"][task_name]
        for datestamp in sorted(task_results.keys()):
            status=task_results[datestamp]
            print_result(datestamp,status)        

def print_result(datestamp,status):
    "prints one line of a result status with color"
    lookup={NODE_STATUS.ABORT:("abort",print_red),
            NODE_STATUS.END:("success",print_blue),
            NODE_STATUS.BEGIN:("in progress",print_green),
            NODE_STATUS.WAITING:("waiting for a dependency",print_yellow),
            NODE_STATUS.NOT_STARTED:("not started or no history",print)}
    
    default_lookup=(status,print)
    message,function=lookup.get(status,default_lookup)
    print(datestamp+" ",end="")
    function(message)

def save_report_html(results,html_path,verbose=True):
    template_path=TEMPLATE_FOLDER+"maestro_status_summary.html"
    with open(template_path,"r") as f:
        template_html=f.read()
        
    template = Template(template_html)
    pretty_json=json.dumps(results,indent=4,sort_keys=1)
    if verbose:
        print(pretty_json)

    now=datetime.now()
    date_string_now=now.strftime("%m/%d/%Y, %H:%M:%S")
    
    python_script_path=os.path.realpath(__file__)
    html=template.render(results=results,
                         pretty_json=pretty_json,
                         script_path=python_script_path,
                         date_string_now=date_string_now)
    
    safe_write(html_path,html,verbose=verbose)
