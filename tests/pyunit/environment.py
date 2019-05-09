import unittest, os
from constants import *
from utilities import *

class TestEnvironment(unittest.TestCase):
    def test_variable_values(self):
        key="SEQ_WRAPPERS"
        
        # SEQ_WRAPPERS is set
        cmd="echo $SEQ_WRAPPERS"
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertTrue(output)        
        
        # wrappers folder was found
        cmd="ls ${%s}/wrappers"%key
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertEqual(status,0)
