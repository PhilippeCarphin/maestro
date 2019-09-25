import unittest, os
from utilities.utils import *

class TestEnvironment(unittest.TestCase):
    def test_variable_values(self):
        key="SEQ_WRAPPERS"
        
        # SEQ_WRAPPERS is set
        cmd="echo $SEQ_WRAPPERS"
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertNotEqual(output,"\n")        
        
        # wrappers folder was found
        cmd="ls ${%s}/wrappers"%key
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertEqual(status,0)
