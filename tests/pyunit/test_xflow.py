import unittest
from utilities.utils import *

class TestXFlow(unittest.TestCase):
	
    @classmethod
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "xflow -exp mock_files/sample_exp", use_popen = True)
        
    def test_basic_usage(self):
        self.assertNotIn("XML Document Not Found", self.output[0])
        self.assertNotIn("NODE", self.output[0])
        self.assertNotIn("-l argument requires -n ar gument!", self.output[0])
        
    def test_bug9662(self):
        if "no element found" in self.output[0]:
            #Empty/Invalid flow.xml file (Bug 9662 test)
            self.assertIn("Xflow.xml file is empty", self.output[0])
            
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
	
    def test_exit_status(self):	
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(-15, self.output[1],"Exit Status 0")