import json
from constants.path import MFLOW_ROOT

def get_json_from_path(path):
    with open(path,"r") as f:
        return json.loads(f.read())

SCHEMAS=MFLOW_ROOT+"/schemas/"
class JSON_SCHEMAS:
    NODE=get_json_from_path(SCHEMAS+"node_data.json")
    FLOW=get_json_from_path(SCHEMAS+"flow_data.json")