import unittest
from utilities import get_output
from constants import SSM_USE_COMMAND

"""
Maestro should not be in the environment until the SSM use command is run on the test SSM.
"""

class TestEnvironment(unittest.TestCase):
    def test_before_after_ssm(self):
        
        # required by test suite
        cmd="echo $MAESTRO_TEST_SSM_DOMAIN_PATH"
        output,status = get_output(cmd)
        self.assertTrue(output.strip())
        
        # ssm use success
        output,status = get_output(SSM_USE_COMMAND)
        self.assertEqual(status,0)
        
        # environment variables are not in environment, SSM adds them
        variables=("SEQ_WRAPPERS",)
        for variable in variables:
            cmd="echo $"+variable
            output,status = get_output(cmd)
            self.assertFalse(output.strip())        
            output,status = get_output(SSM_USE_COMMAND + cmd)
            self.assertTrue(output.strip())
        
        # executables are not in environment, SSM adds them
        executables = ("maestro","xflow","xflow_overview","expbegin", "expclean", "getdef", "logreader","mserver","nodeinfo", "nodelogger", "scanexp","madmin")        
        for executable in executables:
            cmd="which "+executable
            output,status = get_output(cmd)
            self.assertNotEqual(status,0)
            output,status = get_output(SSM_USE_COMMAND+cmd)
            self.assertEqual(status,0,msg=cmd)
    
    def test_ssm_folders(self):
        # wrappers folder exists
        cmd=SSM_USE_COMMAND+"ls $SEQ_WRAPPERS/wrappers"
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertEqual(status,0)
