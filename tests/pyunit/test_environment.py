import unittest, os
from utilities import *

"""
Maestro should not be in the environment until the SSM use command is run on the test SSM.
"""

class TestEnvironment(unittest.TestCase):
    def test_before_after_ssm(self):
        
        "environment variables are not in environment, SSM adds them"
        cmd="echo $SEQ_WRAPPERS"
        output,status = get_output(cmd)
        self.assertFalse(output.strip())        
        
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertTrue(output.strip())
        
        "executables are not in environment, SSM adds them"
        executables = ("maestro","xflow","xflow_overview","expbegin", "expclean", "getdef", "logreader","mserver","nodeinfo", "nodelogger", "scanexp","madmin")        
        for executable in executables:
            cmd="which "+executable
            output,status = get_output(cmd)
            self.assertNotEqual(status,0)
            output,status = get_output(SSM_USE_COMMAND+cmd)
            self.assertEqual(status,0)
    
    def test_ssm_folders(self):
        "wrappers folder exists"
        cmd="ls $SEQ_WRAPPERS/wrappers"
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertEqual(status,0)
