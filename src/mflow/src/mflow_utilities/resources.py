
from utilities.shell import get_true_host

"""
if the <BATCH> element in /resources/${NODE_PATH}.xml
is missing attributes, or not there at all, then
then these are the values found in node_data dictionaries.
"""
DEFAULT_BATCH_RESOURCES={"catchup":4,                  
                         "cpu":1,
                         "machine":get_true_host(),                  
                         "memory":"3G",
                         "queue":"development",
                         "soumet_args":"",
                         "wallclock":5}

def insert_default_batch_resources(node_data,overwrite=False):
    for key,item in DEFAULT_BATCH_RESOURCES.items():
        if overwrite or key not in node_data:
            node_data[key]=DEFAULT_BATCH_RESOURCES[key]