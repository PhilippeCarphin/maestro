#!../venv/bin/python3

"""
This class parses a maestro experiment and builds information about it.

This class, and the classes it inherits from, have no code specific to 
any project like for mflow. Instead it only has generally useful 
information about a maestro experiment.
"""

import os
from os import stat
from pwd import getpwuid

from maestro.path import find_exp_home_in_path, get_experiment_name
from maestro.sequencer import get_sequencer_command
from mflow_utilities import logger
from utilities import pretty, clamp

from maestro_experiment.me_flow import ME_Flow
from maestro_experiment.me_indexes import ME_Indexes
from maestro_experiment.me_logs import ME_Logs
from maestro_experiment.me_node_data import ME_NodeData
from maestro_experiment.me_node_status import ME_NodeStatus
from maestro_experiment.me_resources import ME_Resources
from maestro_experiment.me_snapshot import ME_Snapshot
from maestro_experiment.me_validation import ME_Validation

class MaestroExperiment(ME_Flow, ME_Indexes, ME_Logs, ME_NodeData, ME_NodeStatus, ME_Resources, ME_Snapshot, ME_Validation):
    def __init__(self,
                 path,
                 datestamp=None,
                 node_log_refresh_interval=10,
                 user_home=None):
        
        self.node_log_refresh_interval=clamp(node_log_refresh_interval,1,600)
        
        """
        A list of strings describing any errors in parsing or reading this experiment path.
        """
        self.validation_errors=[]
           
        """
        key is resource variable like FRONTEND, value is its value from resource files.
        """
        self.resource_cache={}
        
        """
        key is path to xml file, value is the lxml element for its resource XML, with 
        all resource variables like ${FRONTEND} replaced with their resource value.
        """
        self.resource_xml_cache={}
        
        self.path=find_exp_home_in_path(path)        
        self.name=get_experiment_name(path)
        
        """
        If this value is set outside this class, maestro can give additional 
        info and warnings if the user cannot submit to a queue.
        MaestroExperiment doesn't find this itself since that may be slow and
        in many cases it is not used.
        """
        self.qstat_data=None
        
        if user_home:
            self.user_home=user_home
        else:
            self.find_user_home()
            
        if not self.basic_experiment_validation():
            raise ValueError("Experiment validation errors:\n"+"\n".join(self.validation_errors))
            
        self.inspect_flow()
                
        if datestamp:
            self.set_snapshot(datestamp)
        else:
            self.datestamp=""
            self.long_datestamp=""
            
    def find_user_home(self):
        "Set home to the home of the owner of the experiment."
        username=getpwuid(stat(self.path).st_uid).pw_name
        home_root=os.path.dirname(os.environ["HOME"])
        self.user_home=home_root+"/"+username+"/"
    
    def get_workdir_path(self,node_path):
        if not self.long_datestamp:
            return ""
        
        node_data=self.get_node_data(node_path)
        machine=node_data["machine"]
        
        path=self.path+"hub/%s/work/%s/"%(machine,self.long_datestamp)
        path+=node_path+"/"
        return path
        
    def get_sequencer_command(self,node_path,signal,**kwargs):
        return get_sequencer_command(self.path,
                                     self.long_datestamp,
                                     node_path,
                                     signal,
                                     **kwargs)
        
    def __str__(self):
        lines=["<MaestroExperiment>"]
        lines.append("\npath = '%s'"%self.path)
        lines.append("\nnode_datas = "+pretty(self.node_datas))
        lines.append("\nmodule_name_to_tree = "+pretty(self.module_name_to_tree))
        lines.append("</MaestroExperiment>")
        
        return "\n".join(lines)

if __name__=="__main__":
    import sys
    path=sys.argv[1]
    print(MaestroExperiment(path))
