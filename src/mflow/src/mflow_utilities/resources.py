
import os.path

from utilities.shell import get_true_host
from constants import DEFAULT_BATCH_RESOURCES

def insert_default_batch_data(node_data,
                              overwrite=False,
                              default_machine_is_truehost=False):
    for key,item in DEFAULT_BATCH_RESOURCES.items():
        if overwrite or key not in node_data:
            node_data[key]=DEFAULT_BATCH_RESOURCES[key]
            
    if default_machine_is_truehost and not node_data["machine"]:
        node_data["machine"]=get_true_host()


