import unittest
from utilities import *

"""
Test a long list of simple commands which should simply return a success status.
"""

class TestSimpleSuccess(unittest.TestCase):
    def test_exit_status(self):
        
        for key in success_commands:
            for expect_success in (0,1):
                cmd=success_commands[key]
                if expect_success:
                    cmd=SSM_USE_COMMAND+cmd
                output,status = get_output(cmd)
                message="\nFull command used:\n    "+cmd     
                
                if expect_success:
                    self.assertEqual(status,0,msg=message)
                else:
                    self.assertNotEqual(status,0,msg=message)
                
            
