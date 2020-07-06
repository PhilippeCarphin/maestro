import os.path

from constants.maestro import NODE_STATUS
from utilities import reverse_readlines

class NodeLogParser():
    def __init__(self,path,refresh_interval=10):
        assert type(path) is str
        
        self.path=path
        self.latest_parse_mtime=-1
        self.refresh_interval=refresh_interval
        
        """
        A encoding like 'utf-8' which has successfully parsed this log at least once.
        """
        self.successful_encoding=""
        
        """
        The lowest line in the node log that we have parsed, 
        updated as the last line in the file each time it is opened.
        """
        self.lowest_parsed_line=""
        
        """
        key is node path
        value is the lowest line in this log declaring its status
        """
        self.node_path_to_latest_line={}
        
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
            self.parse_node_log(encoding=self.successful_encoding)
        
    def get_status(self,node_path):
        """
        Returns a NODE_STATUS if a line in this node_log should override 
        status files in 'sequencing/status'. Otherwise, returns None.
        """
        
        self.refresh_if_necessary()        
        return self.latest_status_in_log.get(node_path)
    
    def parse_node_log(self,encoding=""):
        
        self.node_log_aborts=set()
               
        if not os.path.isfile(self.path):
            return
        
        """
        If this is the first read, we don't know what a successful encoding is yet.
        So rerun this function with different encoding attempts, saving
        the first successful encoding.
        
        utf-8 encoding usually works, but sometimes a fallback is needed.
        """
        if not encoding:
            encodings=("utf-8","ISO-8859-1")
            reverse_lines_iter=None
            for encoding in encodings:
                try:
                    self.parse_node_log(encoding=encoding)
                    self.successful_encoding=encoding
                    return
                except UnicodeDecodeError:
                    pass
            raise UnicodeDecodeError("Unable to decode '%s' with encodings: %s"%(self.path,str(encodings)))
        
        reverse_lines_iter=reverse_readlines(self.path,
                                             encoding=encoding)
        if not reverse_lines_iter:
            return
        
        """
        Get a list of all lines at the end of the file which we have
        not seen before.
        """
        lines_to_parse=[]
        for line in reverse_lines_iter:
            if self.lowest_parsed_line==line:
                break
            lines_to_parse.append(line)
        lines_to_parse=list(reversed(lines_to_parse))
        self.lowest_parsed_line=lines_to_parse[-1]
                
        "find the newest/latest lines for each node_path"
        for line in lines_to_parse:
            
            node_path=get_value_from_node_log_line(line,"SEQNODE")
            if not node_path:
                continue
            
            message_type=get_value_from_node_log_line(line,"MSGTYPE")
            if not message_type:
                continue
            
            if node_path.startswith("/"):
                node_path=node_path[1:]
                
            self.node_path_to_latest_line[node_path]=line
        
        "parse the latest lines"
        for node_path,line in self.node_path_to_latest_line.items():
                
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