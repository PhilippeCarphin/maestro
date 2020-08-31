import os.path
import re
from datetime import datetime

from constants.maestro import NODE_STATUS
from constants import ENCODINGS
from utilities.generic import safe_open


class NodeLogParser():
    def __init__(self, path, refresh_interval=10):
        assert type(path) is str
        assert path

        self.path = path
        self.latest_parse_mtime = -1
        self.refresh_interval = refresh_interval

        "key is node_path, value is MSGTYPE in newest/lowest line with that node_path"
        self.latest_status_in_log = {}

        self.refresh_if_necessary()

    def refresh_if_necessary(self):
        "re-open and re-parse the node log file, if it has been modified more than 'interval' seconds since last refresh"

        if not os.path.exists(self.path):
            return

        mtime = os.path.getmtime(self.path)
        
        first_refresh = self.latest_parse_mtime == -1
        
        if first_refresh or self.latest_parse_mtime+self.refresh_interval < mtime:
            self.latest_parse_mtime = mtime
            self.parse_node_log()

    def get_status(self, node_path):
        """
        Returns a NODE_STATUS if a line in this node_log should override 
        status files in 'sequencing/status'. Otherwise, returns None.
        """

        self.refresh_if_necessary()
        return self.latest_status_in_log.get(node_path)
    
    def get_successful_execution_duration(self, node_path):
        """
        Returns the latest successful execution duration in seconds for this node path.
        """
        
        self.refresh_if_necessary()
        if node_path.startswith("/"):
            node_path=node_path[1:]
        return self.latest_execution_duration.get(node_path,0)

    def parse_node_log(self):
        self.node_log_aborts = set()

        if not os.path.isfile(self.path):
            return

        """
        utf-8 encoding usually works, but sometimes a fallback
        is needed to prevent decode errors.
        """
        self.lines = safe_open(self.path).split("\n")

        "key is node_path, value is the parsed newest/latest line"
        latest_lines_parsed = {}
        
        "key is node_path, value is duration of the latest succesful job in seconds"
        self.latest_execution_duration={}
        
        "key is node_path, value is the begin timestamp used to find the latest_execution_duration"
        self.latest_execution_timestamp={}
        
        "key is node_path, value is timestamp of latest BEGIN line"
        latest_begin_timestamp={}

        "find the newest/latest lines for each node_path"
        for line in self.lines:
            
            values=get_values_from_node_log_line(line)
            node_path = values.get("SEQNODE")
            message_type = values.get("MSGTYPE")
            if not node_path or not message_type:
                continue

            if node_path.startswith("/"):
                node_path = node_path[1:]

            latest_lines_parsed[node_path] = values
            
            timestamp = values.get("TIMESTAMP")
            if not timestamp:
                continue
            
            if message_type=="begin":
                latest_begin_timestamp[node_path]=timestamp
            if message_type=="end":
                begin_timestamp=latest_begin_timestamp.get(node_path)
                if begin_timestamp:
                    seconds=get_timestamp_string_difference(timestamp,begin_timestamp)
                    self.latest_execution_duration[node_path]=seconds
                    self.latest_execution_timestamp[node_path]=begin_timestamp
        
        "parse the latest lines"
        for node_path, values in latest_lines_parsed.items():
            
            status = ""
            message = values.get("SEQMSG","")
            message_type = values.get("MSGTYPE","")
            
            if message.startswith("ord_soumet failed"):
                status = NODE_STATUS.SUBMIT_FAILURE
            elif message_type.startswith("abort"):
                status = NODE_STATUS.ABORT
            elif message_type.startswith("begin"):
                status = NODE_STATUS.BEGIN
            elif message_type.startswith("end"):
                status = NODE_STATUS.END
            elif message_type.startswith("init"):
                status = NODE_STATUS.NOT_STARTED

            if status:
                self.latest_status_in_log[node_path] = status


def get_timestamp_string_difference(timestamp1, timestamp2):
    """
    Given two timestamps:
        20200828.20:31:20
        20200828.20:31:10
    returns the number of seconds for timestamp1-timestamp2:
        10
    """    
    
    try:
        date1 = datetime.strptime(timestamp1, '%Y%m%d.%H:%M:%S')
        date2 = datetime.strptime(timestamp2, '%Y%m%d.%H:%M:%S')
    except ValueError:
        return 0
    
    return (date1-date2).total_seconds()    

def get_values_from_node_log_line(line):
    """
    For a line:
        TIMESTAMP=20200828.20:35:50:SEQNODE=/turtle
    returns:
        {"TIMESTAMP":"123",
         "SEQNODE":"/turtle"}
        
    Parsing the line is easy, but not trivial, because of node log line design choices.
    """
    
    """
    For lines like:
        TIMESTAMP=20200828.20:35:50:SEQNODE=/turtle:MSGTYPE=abortx:SEQLOOP=:SEQMSG=ABORTED job stopped , job_ID=job4
    matches substrings like:
        :SEQNODE=
    """
    node_log_key_regex=re.compile(":[A-Z_]+=")
    
    with_newlines=line.strip()
    for match in node_log_key_regex.findall(line):
        with_newlines=with_newlines.replace(match,"\n"+match[1:])
    
    values={}
    for chunk in with_newlines.split("\n"):
        if not chunk or "=" not in chunk:
            continue
        
        key=chunk[:chunk.index("=")].strip()
        value=chunk[chunk.index("=")+1:].strip()
        values[key]=value
    return values        