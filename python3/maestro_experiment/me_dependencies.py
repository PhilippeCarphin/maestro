
"""
This code handles dependency reading for the MaestroExperiment class.

This abstract class is not meant to be instantiated, only inherited.
"""

import os.path

from utilities.pretty import pretty_kwargs
from utilities.parsing import superstrip
from maestro import resolve_dependency_path
from home_logger import logger

class ME_Dependencies():
    
    def get_dependency_data_for_node_path(self,node_path):
        "if node_path in cache, return that"
        if node_path in self.dependencies:
            return self.dependencies[node_path]
        
        if not self.is_node_path(node_path):
            return []
        
        node_data=self.get_node_data(node_path)
        resource_xml=self.get_interpreted_resource_lxml_element(node_data["resource_path"])
        
        "lxml is silly and prints a warning to stdout unless the check is done this way"
        if not (resource_xml is not None):
            return []
        
        result=[]
        for element in resource_xml.xpath("//DEPENDS_ON"):
            data=get_dependency_data_from_DEPENDS_ON_element(element,node_path)
            result.append(data)
            
        "cache result"
        self.dependencies[node_path]=result
        
        return self.dependencies[node_path]

def get_dependency_data_from_DEPENDS_ON_element(element,node_path):
    """
    Given an XML element like:
        <DEPENDS_ON dep_name="../task2" status="end" type="node"/>
    returns a dictionary, taking into account relative paths like "../" for this node_path.
    """
    
    dep_name=element.attrib.get("dep_name","")
    if not dep_name:
        return None
    
    dep_node_path=resolve_dependency_path(dep_name,node_path)
    
    return new_dep_data(node_path=dep_node_path,
                        experiment_path=element.attrib.get("exp",""),
                        status=element.attrib.get("status","end"),
                        type=element.attrib.get("type","node"),
                        valid_hour=element.attrib.get("valid_hour",""),
                        valid_dow=element.attrib.get("valid_dow",""),
                        dep_name=dep_name)

def new_dep_data(**kwargs):
    data={"node_path":"",
          "experiment_path":"",
          "status":"end",
          "type":"node",
          "valid_hour":"",
          "valid_dow":"",
          "dep_name":"",
          "node_folder":""}
    for key,value in kwargs.items():
        data[key]=value
    return data