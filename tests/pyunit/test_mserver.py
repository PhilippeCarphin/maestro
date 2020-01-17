import unittest
from utilities.utils import *

class TestMServer(unittest.TestCase):
	
    @classmethod 
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "madmin -i")
		
    def test_basic_usage(self):	
        self.assertIn("Server is Alive", self.output[0])
        
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")