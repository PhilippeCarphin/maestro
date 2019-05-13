import unittest
from utilities.utils import *

class TestNodeLogger(unittest.TestCase):
	
    @classmethod
    def setUpClass(cls):
        cls.output = get_output(SSM_USE_COMMAND + "nodelogger -n module -s info -m hello -e mock_files/sample_exp -d 20191102111111")
		
    def test_basic_usage(self):
        self.assertNotIn("Cannot connect", self.output[0])
        self.assertNotIn("invalid SEQ_EXP_HOME", self.output[0])
        self.assertNotIn("option requires an argument", self.output[0])
        self.assertIn("Node =", self.output[0])
		
    def test_loop_argument(self):
        self.assertNotIn("Invalid loop arguments", self.output[0])
		
    def test_maestro_server(self):
        self.assertNotIn("Found No Maestro Server", self.output[0])
        
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")
