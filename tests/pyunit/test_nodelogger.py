import unittest
from utilities.utils import *

expected1="""Node = /sample/Different_Hosts/IBMTask 
Signal = info 
Message = hello"""

class TestNodeLogger(unittest.TestCase):
    
    def test_basic_usage(self):
        cmd=success_commands["nodelogger"]
        output,status = get_output()
        self.assertIn(expected1, output)
