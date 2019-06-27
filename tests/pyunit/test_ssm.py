import unittest
from utilities.utils import *

class TestSSM(unittest.TestCase):
	
    @classmethod	
    def setUpClass(cls):	
        cls.commands = ["maestro","xflow","xflow_overview","expbegin", "expclean", "getdef", "logreader","mserver","nodeinfo", "nodelogger", "scanexp"]
    
    def test_ssm_package(self):	
        for executable in (self.commands):
            output = get_output(executable)
            self.assertIn("command not found", output[0])