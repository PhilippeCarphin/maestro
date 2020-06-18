
"""
This code handles code related node_data for the MaestroExperiment class.

This abstract class is not meant to be instantiated, only inherited.
"""

from constants import NODE_TYPE, DEFAULT_BATCH_RESOURCES
from utilities import pretty, get_true_host
from utilities.generic import superstrip
from maestro.utilities.xml import is_container

class ME_NodeData():

    def get_node_datas(self):
        return [self.get_node_data(node_path) for node_path in self.get_node_paths()]
    
    def get_node_data(self,node_path):        
        if node_path not in self.node_datas:
            self.node_datas[node_path]=self.calculate_node_data(node_path)
        return self.node_datas[node_path]
    
    def calculate_node_data(self,node_path):

        flow_data=self.get_flow_data(node_path)        
        if not flow_data:
            msg="node_path '%s' was not found in the flow XML files."%node_path
            msg+="\nMaestroExperiment node paths:\n"+pretty(list(self.flow_datas.keys()))
            raise ValueError(msg)
            
        node_name=node_path.split("/")[-1]
        node_type=flow_data["type"]
                
        no_slash_node_path=node_path
        if no_slash_node_path.endswith("/"):
            no_slash_node_path=no_slash_node_path[:-1]
        mpath=flow_data["module_path_inner"]
        
        "task, config, resource paths"
        resource_path=self.path+"resources/"+node_path
        if is_container(node_type):
            task_path=""
            config_path=self.path+"modules/"+mpath+"/container.cfg"
            resource_path+="/container.xml"
        else:
            task_path=self.path+"modules/"+mpath+".tsk"
            config_path=self.path+"modules/"+mpath+".cfg"    
            resource_path+=".xml"
        
        loop_indexes=self.get_indexes_from_node_path(node_path)
        
        node_data={"flow_children_node_paths":flow_data["flow_children_node_paths"],
                "config_path":config_path,
                "loop_indexes_available":loop_indexes,
                "module_name":flow_data["module_name"],
                "name":node_name,
                "path":node_path,
                "resource_path":resource_path,
                "submits_children_node_paths":flow_data["submits_children_node_paths"],
                "task_path":task_path,
                "flow_branch":flow_data["flow_branch"],
                "flow_path":flow_data["flow_path"],
                "type":node_type}
        
        self.add_batch_data_to_node_data(node_data,resource_path)
        self.cast_node_data(node_data)
        
        if node_type == NODE_TYPE.SWITCH:
            node_data["switch_type"]=flow_data["switch_type"]
        
        return node_data
    
    def cast_node_data(self,node_data):
        """
        As values are read from files, they start as strings like '9'
        This casts the values for node_data as bool, int, str, as appropriate.
        """
        
        for key,default in DEFAULT_BATCH_RESOURCES.items():
            
            if type(default) is bool:
                node_data[key]=bool(node_data[key])
                
            if type(default) is int:
                try:
                    node_data[key]=int(node_data[key])
                except:
                    node_data[key]=default
            
            if type(default) != type(node_data[key]):
                node_data[key]=default
    
    def add_batch_data_to_node_data(self,node_data,resource_path):
        """
        Read this resource XML and add some of its <BATCH> attributes to this 
        node_data dictionary, like "cpu" and "catchup"
        """
        
        batch_data=self.get_batch_data_from_xml(resource_path)
        
        "replace values like '${FRONTEND}' with the resource value for FRONTEND"
        for key,item in batch_data.items():
            if type(item) is str and item.startswith("$"):
                name=superstrip(item,"${}")
                value=self.get_resource_value_from_key(name)
                batch_data[key]=value
        
        """
        insert resource data into node_data
        for each key, use defaults if not in resource data
        """
        for key,default in DEFAULT_BATCH_RESOURCES.items():
            if key in batch_data:
                node_data[key]=batch_data[key]
            else:
                node_data[key]=DEFAULT_BATCH_RESOURCES[key]
        
        "if no machine in <BATCH> use default in resources"
        key="machine"
        if key not in node_data:
            node_data[key]=self.get_resource_value_from_key("SEQ_DEFAULT_MACHINE")
        
        "if still not machine, use true host"
        if not node_data[key]:
            node_data[key]=get_true_host()
    
    
    
    
    
    
    
    