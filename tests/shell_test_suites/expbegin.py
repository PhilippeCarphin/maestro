import unittest
from utilities.utils import *
from os.path import expanduser

class TestExpBegin(unittest.TestCase):
	
    @classmethod 
    def setUpClass(cls):
        home = expanduser("~")
        cls.output = get_output(SSM_USE_COMMAND + "expbegin -e "+ home +"/tests/mock_files/sample_exp -d 20191102111111")
        
    def test_basic_usage(self):
        self.assertNotIn("cannot create", self.output[0])
        self.assertNotIn("SEQ_EXP_HOME", self.output[0])
			
    def test_input_date(self):	
        self.assertNotIn("format error", self.output[0])
        self.assertNotIn("set bounds", self.output[0])
			
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
         self.assertNotEqual(1, self.output[1],"Exit Status 1")
         self.assertEqual(0, self.output[1],"Exit Status 0")