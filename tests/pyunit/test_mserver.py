import os
import unittest
from utilities import *

class TestMServer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        delete_parameters_file()
    
    @classmethod
    def tearDownClass(cls):
        delete_parameters_file()
        
    def test_basic_usage(self):
        mcheck=" mserver_check -m maestro1 ; "
        cmd=SSM_USE_COMMAND+mcheck+success_commands["madmin"]
        output,status = get_output(cmd)
        self.assertIn("Server is Alive", output)

def delete_parameters_file():
    try:
        os.remove(MAESTRO_PARAMETERS_FILE)
    except:
        pass
