import unittest
from utilities.utils import *

class TestLogReader(unittest.TestCase):
	
    @classmethod        
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "logreader -e mock_files/sample_exp -d 20191122111111")
    
    def test_basic_usage(self): 
        self.assertNotIn("Cannot open", self.output[0])
        self.assertNotIn("requires an argument", self.output[0])
	
    def test_input_date(self):
        self.assertNotIn("SEQ_DATE", self.output[0])
      
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")