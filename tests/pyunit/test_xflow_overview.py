import unittest
from utilities.utils import *

class TestXFlowOverview(unittest.TestCase):
	
    @classmethod
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "xflow_overview -exp mock_files/sample_exp", use_popen = True)
		
    def test_basic_usage(self):
        self.assertNotIn("SEQ_EXP_HOME", self.output[0])
		
    def test_rc(self):	
        self.assertNotIn("ERROR", self.output[0])
		
    def test_logspan(self):
        self.assertNotIn("bad switch", self.output[0])
		
    def test_display(self):
        self.assertNotIn("couldn't connect to display", self.output[0])
        
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):	
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(-15, self.output[1],"Exit Status 0")