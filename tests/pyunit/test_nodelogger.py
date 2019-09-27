import unittest
from utilities import *

expected1="""Node = /sample/Different_Hosts/IBMTask 
Signal = info 
Message = hello"""

class TestNodeLogger(unittest.TestCase):
    
    def test_basic_usage(self):
        cmd=SSM_USE_COMMAND+success_commands["nodelogger"]
        output,status = get_output(cmd)
        self.assertIn(expected1, output)
