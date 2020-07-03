
"""
if the <BATCH> element in /resources/${NODE_PATH}.xml
is missing attributes, or not there at all, then
then these are the values found in node_data dictionaries.
"""
DEFAULT_BATCH_RESOURCES={"catchup":4,                  
                         "cpu":1,
                         "memory":"3G",
                         "queue":"development",
                         "soumet_args":"",
                         "wallclock":5}