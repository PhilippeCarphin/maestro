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
            output,status = get_output(cmd, seconds=1, use_popen = True)
            message="\n\nCommand used:\n    "+cmd+"\nStatus = "+str(status)
            
            has_terminated=status is None
            is_success=not has_terminated
            self.assertTrue(is_success,msg=message)
