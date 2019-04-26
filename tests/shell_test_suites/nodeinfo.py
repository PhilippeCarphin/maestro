import unittest
from utilities.utils import *

class TestNodeInfo(unittest.TestCase):
	
    @classmethod 
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "nodeinfo -n module -e mock_files/sample_exp")
		
    def test_basic_usage(self):
        self.assertNotIn("specified node", self.output[0])
        self.assertNotIn("requires an argument", self.output[0])
        self.assertNotIn("invalid SEQ_EXP_HOME", self.output[0])
        self.assertIn("node.name", self.output[0])
		
    def test_loop_argument(self):
        self.assertNotIn("Invalid loop arguments", self.output[0])
	
    def test_filter(self):
        self.assertNotIn("Unrecognized filter", self.output[0])
        
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")