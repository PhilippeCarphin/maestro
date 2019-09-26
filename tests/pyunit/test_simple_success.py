import unittest
from utilities import *

"""
Test a long list of simple commands which should simply return a success status.
"""

class TestSimpleSuccess(unittest.TestCase):
    def test_exit_status(self):
        
        for key in success_commands:
            cmd=SSM_USE_COMMAND+success_commands[key]
            output,status = get_output(cmd)
            message="\nFull command used:\n    "+command
            self.assertEqual(status,0,msg=message)
            
