import os.path

from constants.maestro import NODE_STATUS
from constants import ENCODINGS
from utilities.generic import safe_open

class NodeLogParser():
    def __init__(self,path,refresh_interval=10):
        assert type(path) is str
        
        self.path=path
        self.latest_parse_mtime=-1
        self.refresh_interval=refresh_interval
        
        "key is node_path, value is MSGTYPE in newest/lowest line with that node_path"
        self.latest_status_in_log={}
                
        self.refresh_if_necessary()
        
    def refresh_if_necessary(self):
        "re-open and re-parse the node log file, if it has been modified more than 'interval' seconds since last refresh"
        
        if not os.path.exists(self.path):
            return
        
        mtime=os.path.getmtime(self.path)
        
        first_refresh=self.latest_parse_mtime==-1
        if first_refresh or self.latest_parse_mtime+self.refresh_interval<mtime:
            self.latest_parse_mtime=mtime
            self.parse_node_log()
        
    def get_status(self,node_path):
        """
        Returns a NODE_STATUS if a line in this node_log should override 
        status files in 'sequencing/status'. Otherwise, returns None.
        """
        
        self.refresh_if_necessary()        
        return self.latest_status_in_log.get(node_path)
    
    def parse_node_log(self):
        
        self.node_log_aborts=set()
               
        if not os.path.isfile(self.path):
            return
        
        """
        utf-8 encoding usually works, but sometimes a fallback
        is needed to prevent decode errors.
        """        
        self.lines=safe_open(self.path).split("\n")
        
        "key is node_path, value is newest/latest line"
        latest_lines={}
        
        "find the newest/latest lines for each node_path"
        for line in self.lines:
            
            node_path=get_value_from_node_log_line(line,"SEQNODE")
            if not node_path:
                continue
            
            message_type=get_value_from_node_log_line(line,"MSGTYPE")
            if not message_type:
                continue
            
            if node_path.startswith("/"):
                node_path=node_path[1:]
                
            latest_lines[node_path]=line
        
        "parse the latest lines"
        for node_path,line in latest_lines.items():
                
            status=""            
            message=get_value_from_node_log_line(line,"SEQMSG")
            message_type=get_value_from_node_log_line(line,"MSGTYPE")
            
            if message.startswith("ord_soumet failed"):
                status=NODE_STATUS.SUBMIT_FAILURE
            elif message_type.startswith("abort"):
                status=NODE_STATUS.ABORT
            elif message_type.startswith("begin"):    
                status=NODE_STATUS.BEGIN
            elif message_type.startswith("end"):
                status=NODE_STATUS.END
            elif message_type.startswith("init"):
                status=NODE_STATUS.NOT_STARTED
            
            if status:
                self.latest_status_in_log[node_path]=status
                
def get_value_from_node_log_line(line,key,default=""):
    """
    Given a line containing:
        abc:SEQNODE=123:def
    returns:
        123
    """
    try:
        a=line.split(":%s="%key)[1]
        return a.split(":")[0].strip()
    except:
        return default