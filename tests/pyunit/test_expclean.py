import unittest
from utilities.utils import *
 
class TestExpClean(unittest.TestCase):
	
    @classmethod 
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "expclean -e "+ exp_path +" -d 20191102111111 -l")
        
    def test_basic_usage(self):
        self.assertNotIn("SEQ_EXP_HOME", self.output[0])
			
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
				
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")
