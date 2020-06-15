import unittest
from utilities import *

class TestGui(unittest.TestCase):
		
    def test_success_status(self):
        
        # if a gui is still running after a second, the gui probably launched successfully
        commands=("xflow_overview -exp "+PATH.SAMPLE_EXP1,
                  "xflow -exp "+PATH.SAMPLE_EXP1,
                  "xm")
        for command in commands:
            cmd=SSM_USE_COMMAND + command
            is_success=is_success_after_x_seconds(cmd, 1)
            self.assertTrue(is_success,msg=cmd)
