import os
import unittest
from constants import SSM_USE_COMMAND, MAESTRO_PARAMETERS_FILE
from utilities import get_output

class TestMServer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        delete_parameters_file()
    
    @classmethod
    def tearDownClass(cls):
        delete_parameters_file()
        
    def test_mserver(self):
        
        # this is necessary to setup the maestro parameters file
        machine=os.environ.get("TRUE_HOST","eccc-ppp4")
        mcheck=" mserver_check -m %s ; "%machine
        
        cmd=SSM_USE_COMMAND+mcheck+"madmin -i"
        output,status = get_output(cmd)
        self.assertIn("Server is Alive", output)
        msg="output=\n\n"+output
        self.assertEqual(status,0,msg=msg)

def delete_parameters_file():
    try:
        os.remove(MAESTRO_PARAMETERS_FILE)
    except:
        pass
