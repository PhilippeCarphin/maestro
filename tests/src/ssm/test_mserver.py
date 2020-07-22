import os
import unittest
from utilities import *
from config import *

class TestMServer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        delete_parameters_file()
    
    @classmethod
    def tearDownClass(cls):
        delete_parameters_file()
        
    def test_mserver(self):
        
        # this is necessary to setup the maestro parameters file
        mcheck=" mserver_check -m %s ; "%MSERVER_MACHINE
        
        cmd=SSM_USE_COMMAND+mcheck+"madmin -i"
        output,status = get_output(cmd)
        self.assertIn("Server is Alive", output)
        self.assertEqual(status,0)

def delete_parameters_file():
    try:
        os.remove(MAESTRO_PARAMETERS_FILE)
    except:
        pass
