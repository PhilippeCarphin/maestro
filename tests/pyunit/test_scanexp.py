import unittest
from utilities.utils import *

class TestScanExp(unittest.TestCase):
	
    @classmethod
    def setUpClass(cls):	
        cls.output = get_output(SSM_USE_COMMAND + "scanexp -e mock_files/sample_exp  -s turtle")
		
    def test_basic_usage(self):
        self.assertNotIn("No such file", self.output[0])
        self.assertNotIn("argument must be defined", self.output[0])
        self.assertIn("Scanning under", self.output[0])
		
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
			
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")
	