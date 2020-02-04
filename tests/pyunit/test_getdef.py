import unittest
from utilities.utils import *

class TestGetDef(unittest.TestCase):
	
    @classmethod 
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "getdef -e mock_files/sample_exp  mock_files/sample_exp/getdef_test.py variable")
        
    def test_basic_usage(self):
        self.assertNotIn("SEQ_EXP_HOME", self.output[0])
        self.assertNotIn("Unable to find key", self.output[0])
		
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")