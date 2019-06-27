import unittest
from utilities.utils import *
from os.path import expanduser

class TestMaestro(unittest.TestCase):

    @classmethod 
    def setUpClass(cls):
        home = expanduser("~")
        cls.output = get_output(SSM_USE_COMMAND + "maestro -n module -s begin -e "+ home +"/maestro/tests/mock_files/sample_exp -d 20191102111111")
		
    def test_basic_usage(self):
        self.assertNotIn("SEQ_EXP_HOME", self.output[0])
        self.assertNotIn("unable to get to the specified node", self.output[0])
        self.assertNotIn("illegal option", self.output[0])
		
    def test_mserver_connection(self):
        self.assertNotIn("could not open connection with server", self.output[0])
        self.assertIn("Server Connection Open And Login Accepted", self.output[0])
		
    def test_input_date(self):	
        self.assertNotIn("outside set bounds", self.output[0])
		
    def test_loop_argument(self):	
        self.assertNotIn("Invalid loop arguments", self.output[0])
		
    def test_flow(self):
        self.assertNotIn("flow value must be", self.output[0])
        
    def test_get_output(self):
        self.assertIs(type(self.output), tuple)
		
    def test_exit_status(self):
        self.assertNotEqual(1, self.output[1],"Exit Status 1")
        self.assertEqual(0, self.output[1],"Exit Status 0")