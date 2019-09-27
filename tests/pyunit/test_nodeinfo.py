import unittest
from utilities import *

class TestNodeInfo(unittest.TestCase):
	
    def test_basic_usage(self):
        cmd=SSM_USE_COMMAND+success_commands["nodeinfo"]
        output,status = get_output(cmd)
        
        expected="node.name=/sample/Different_Hosts/IBMTask"
        self.assertIn(expected, output)
        expected="node.container=/sample/Different_Hosts"        
        self.assertIn(expected, output)
    
    def test_nodesource(self):
        cmd=SSM_USE_COMMAND+success_commands["nodesource"]
        output,status = get_output(cmd)
        expected="getdef resources FRONTEND"
        message="\n\nCommand used:\n    "+cmd
        self.assertIn(expected, output,msg=message)
        
