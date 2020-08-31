import unittest
import json

from utilities.maestro import NodeLogParser, get_values_from_node_log_line
from tests.path import NODE_LOG_UTF8_ERROR, NODE_LOG_TURTLE_DURATION
from utilities import pretty_kwargs

class TestNodeLogParser(unittest.TestCase):

    def test_utf8_open_error(self):
        NodeLogParser(NODE_LOG_UTF8_ERROR)
        
    def test_execution_duration(self):
        nlp = NodeLogParser(NODE_LOG_TURTLE_DURATION)
        seconds=nlp.get_successful_execution_duration("/turtle/turtleTask1")
        self.assertEqual(seconds,10)
    
    def test_parse_node_log_line(self):
        line="TIMESTAMP=20200828.20:35:50:SEQNODE=/turtle:MSGTYPE=abortx:SEQLOOP=:SEQMSG=ABORTED job stopped , job_ID=job4"
        result=get_values_from_node_log_line(line)
        expected={"TIMESTAMP":"20200828.20:35:50",
                  "SEQNODE":"/turtle",
                  "MSGTYPE":"abortx",
                  "SEQLOOP":"",
                  "SEQMSG":"ABORTED job stopped , job_ID=job4"}
        msg=pretty_kwargs(result=result,expected=expected)
        self.assertEqual(result,expected,msg=msg)