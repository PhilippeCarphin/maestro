import unittest
from utilities.utils import *

class TestXM(unittest.TestCase):
	
    @classmethod
    def setUpClass(cls):	
        cls.output = get_output(SSM_USE_COMMAND + "xm", use_popen = True)
		
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
	
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")
		