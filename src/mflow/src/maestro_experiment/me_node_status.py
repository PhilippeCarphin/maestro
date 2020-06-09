
"""
This code handles code to lookup the node status (ABORT, END) for the MaestroExperiment class.

This abstract class is not meant to be instantiated, only inherited.
"""

import glob
import os.path

from maestro.status import get_status_from_path
from constants import NODE_STATUS

class ME_NodeStatus():

    def get_node_status(self,node_path,loop_index_selection=None,node_log_refresh_interval=10):
        """
        Find the appropriate status file and return its status. Example status file:           
        simple_experiment/sequencing/status/20200401000000/turtle/TurtlePower/BossaNova/donatello.+0+0.end
        
        loop_index_selection = {"loop1":5,"loop2":7}
        """
        
        "check if a status is in the node_log, which overrides the 'sequencing/status' files."
        node_log_status=self.node_log_parser.get_status(node_path)
        node_data=self.get_node_data(node_path)        
        catchup=node_data["catchup"]
        is_catchup=catchup>4
        
        if node_log_status:
            if is_catchup and node_log_status==NODE_STATUS.NOT_STARTED:
                return NODE_STATUS.CATCHUP
            return node_log_status
        
        if not loop_index_selection:
            loop_index_selection=self.get_first_index_selection(node_path)
        
        loop_suffix=""
        if loop_index_selection:
            loop_suffix=".+"+"+".join([str(value) for value in loop_index_selection.values()])
                
        g=self.path+"/sequencing/status/"+self.long_datestamp+"/"+node_path+loop_suffix+"*"
        status_files=sorted(glob.iglob(g))
        status_files=[i for i in status_files if os.path.isfile(i)]
        
        if not status_files:
            if is_catchup:
                return NODE_STATUS.CATCHUP
            else:
                return NODE_STATUS.NOT_STARTED
            
        status,status_text=get_status_from_path(status_files[0])
        return status
    